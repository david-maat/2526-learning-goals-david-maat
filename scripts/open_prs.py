#!/usr/bin/env python3
import os
import sys
import json
import glob
import argparse
import subprocess

def run_cmd(args, check=True):
    print(f"Running: {' '.join(args)}")
    res = subprocess.run(args, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"Error running command: {' '.join(args)}")
        print(f"STDOUT:\n{res.stdout}")
        print(f"STDERR:\n{res.stderr}")
        res.check_returncode()
    return res

def get_local_repo_info():
    try:
        url = run_cmd(["git", "remote", "get-url", "origin"], check=False).stdout.strip()
        if url.endswith(".git"):
            url = url[:-4]
        if "github.com" in url:
            parts = url.split("github.com")[-1].strip("/:").split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]
    except Exception as e:
        print(f"Could not determine repo from git remote: {e}")
    return None, None

def main():
    parser = argparse.ArgumentParser(description="Open/update Pull Requests on upstream repo for Done learning goals.")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Dry run: print actions without making actual changes or calling GitHub write operations")
    args = parser.parse_args()

    dry_run = args.dry_run
    if dry_run:
        print("==================================================")
        print("RUNNING IN DRY RUN MODE - NO CHANGES WILL BE MADE")
        print("==================================================")

    # 1. Identify owner and repo
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER")
    repo_full = os.environ.get("GITHUB_REPOSITORY")

    if repo_full:
        parts = repo_full.split("/")
        owner = parts[0]
        repo_name = parts[1]
    else:
        owner, repo_name = get_local_repo_info()
        if not owner or not repo_name:
            try:
                res = run_cmd(["gh", "repo", "view", "--json", "owner,name"], check=False)
                if res.returncode == 0:
                    data = json.loads(res.stdout)
                    owner = data["owner"]["login"]
                    repo_name = data["name"]
            except Exception:
                pass

    if not owner or not repo_name:
        print("Error: Could not determine GitHub repository owner and name.")
        sys.exit(1)

    print(f"Repository: {owner}/{repo_name}")

    # 2. Find parent repository (upstream)
    try:
        info_res = run_cmd(["gh", "repo", "view", f"{owner}/{repo_name}", "--json", "parent,defaultBranchRef"])
        info = json.loads(info_res.stdout)
    except Exception as e:
        print(f"Error querying repo info with gh CLI: {e}")
        sys.exit(1)

    parent_repo = None
    parent_default_branch = "main"

    if info.get("parent") and isinstance(info["parent"], dict):
        parent_owner = info["parent"]["owner"]["login"]
        parent_name = info["parent"]["name"]
        parent_repo = f"{parent_owner}/{parent_name}"
        try:
            parent_info_res = run_cmd(["gh", "repo", "view", parent_repo, "--json", "defaultBranchRef"])
            parent_info = json.loads(parent_info_res.stdout)
            parent_default_branch = parent_info.get("defaultBranchRef", {}).get("name", "main")
        except Exception:
            parent_default_branch = "main"
    else:
        # Fallback to self if not a fork
        parent_repo = f"{owner}/{repo_name}"
        parent_default_branch = info.get("defaultBranchRef", {}).get("name", "main")

    print(f"Upstream target repo: {parent_repo} (branch: {parent_default_branch})")

    # 3. Configure Git remote for upstream if it doesn't exist
    if not dry_run:
        remotes = run_cmd(["git", "remote"]).stdout.split()
        if "upstream" not in remotes:
            run_cmd(["git", "remote", "add", "upstream", f"https://github.com/{parent_repo}.git"])
        
        run_cmd(["git", "fetch", "upstream", parent_default_branch])
    else:
        print(f"[Dry Run] Would configure remote 'upstream' and fetch from {parent_repo}")

    # 4. Configure Git user details if not set
    if not dry_run:
        email_check = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
        if not email_check.stdout.strip():
            run_cmd(["git", "config", "--global", "user.email", "actions@github.com"])
        name_check = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
        if not name_check.stdout.strip():
            run_cmd(["git", "config", "--global", "user.name", "GitHub Actions"])

    current_commit = run_cmd(["git", "rev-parse", "HEAD"]).stdout.strip()

    # 5. Scan goals with status "Done"
    done_goals = []
    goal_files = glob.glob("learning_goals/*/*/goal.json")
    for goal_file in goal_files:
        try:
            with open(goal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get("status") == "Done":
                done_goals.append({
                    "number": data.get("number"),
                    "title": data.get("title"),
                    "dir": os.path.dirname(goal_file)
                })
        except Exception as e:
            print(f"Warning: Could not read {goal_file}: {e}")

    # Sort goals by goal number (major.minor)
    try:
        done_goals.sort(key=lambda g: [int(x) for x in g["number"].split(".")])
    except Exception:
        pass

    print(f"Found {len(done_goals)} goals marked as Done.")

    # 6. Process each Done goal
    for goal in done_goals:
        goal_num = goal["number"]
        goal_title = goal["title"]
        goal_dir = goal["dir"]
        branch_name = f"submit/goal-{goal_num}"

        print(f"\n==================================================")
        print(f"Processing Goal {goal_num}: {goal_title}")
        print(f"==================================================")

        # Check if PR exists
        pr_res = run_cmd([
            "gh", "pr", "list",
            "--repo", parent_repo,
            "--head", f"{owner}:{branch_name}",
            "--state", "all",
            "--json", "state,number"
        ])
        prs = json.loads(pr_res.stdout)

        action = "create"
        pr_number = None
        if prs:
            pr_state = prs[0]["state"].upper()
            pr_number = prs[0]["number"]
            print(f"Found existing PR #{pr_number} with state: {pr_state}")
            if pr_state in ["MERGED", "CLOSED"]:
                print(f"Skipping Goal {goal_num} as the PR is already {pr_state}.")
                continue
            action = "update"

        if dry_run:
            print(f"[Dry Run] Action: {action.upper()} PR for Goal {goal_num}")
            print(f"[Dry Run] Target Branch: {branch_name}")
            print(f"[Dry Run] Would isolate folder: {goal_dir}")
            continue

        # Recreate local branch starting from upstream default branch
        run_cmd(["git", "checkout", "-B", branch_name, f"upstream/{parent_default_branch}"])

        # Checkout the goal directory from current commit
        checkout_res = subprocess.run([
            "git", "checkout", current_commit, "--", goal_dir
        ], capture_output=True, text=True)

        if checkout_res.returncode != 0:
            print(f"Warning: Could not checkout directory {goal_dir} from {current_commit}")
            print(f"STDERR: {checkout_res.stderr}")
            run_cmd(["git", "checkout", current_commit])
            continue

        # Check if there are changes compared to upstream
        status_res = run_cmd(["git", "status", "--porcelain"])
        if not status_res.stdout.strip():
            print(f"No changes detected for Goal {goal_num} compared to upstream/{parent_default_branch}.")
            run_cmd(["git", "checkout", current_commit])
            continue

        # Commit changes
        run_cmd(["git", "add", goal_dir])
        run_cmd(["git", "commit", "-m", f"Submit evidence for learning goal {goal_num}"])

        # Push branch
        # Force-push to make sure the branch matches the current commit exactly
        run_cmd(["git", "push", "origin", branch_name, "--force"])

        # Create/Update PR
        if action == "create":
            print(f"Creating PR for Goal {goal_num}...")
            run_cmd([
                "gh", "pr", "create",
                "--repo", parent_repo,
                "--base", parent_default_branch,
                "--head", f"{owner}:{branch_name}",
                "--title", f"Goal {goal_num}: {goal_title}",
                "--body", f"Pull Request automatically opened for Learning Goal {goal_num}.\n\nContains evidence and status update for this goal."
            ])
            print(f"PR successfully created!")
        else:
            print(f"Branch updated successfully. PR #{pr_number} is updated.")

        # Go back to original HEAD before next loop
        run_cmd(["git", "checkout", current_commit])

    print("\nFinished processing all Done goals.")


if __name__ == "__main__":
    main()
