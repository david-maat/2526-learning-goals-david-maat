import type {
    LearningGoal,
    LearningGoalData,
    Category,
    Track,
    Status,
} from "./types";
import type { Component } from "svelte";

const categoryNames: Record<number, string> = {
    1: "Analysis",
    2: "AI",
    3: "Web",
    4: "Business",
    5: "Soft Skills",
    6: "Cloud",
    7: "Data",
    8: "DevOps",
    9: "Infrastructure",
    10: "App",
    11: "Security",
};

// Eager load all goals from the root learning_goals/ folder
const goalModules = import.meta.glob<{ default: LearningGoalData }>(
    "../../learning_goals/*/*/goal.json",
    { eager: true }
);

// Load evidence modules with metadata (frontmatter is exported as `metadata`)
const evidenceMetadata = import.meta.glob<{ visible?: boolean }>(
    "../../learning_goals/*/*/evidence.svx",
    {
        eager: true,
        import: "metadata",
    }
);

// Lazy load evidence modules for rendering
const evidenceModulesGlob = import.meta.glob<{
    default: Component;
}>("../../learning_goals/*/*/evidence.svx");

// Map goal number (e.g. "1.1") to the actual glob path (the key)
const evidencePathLookup: Record<string, string> = {};
for (const path of Object.keys(evidenceModulesGlob)) {
    const match = path.match(/\/(\d+\.\d+)\/evidence\.svx$/);
    if (match) {
        evidencePathLookup[match[1]] = path;
    }
}

export const evidenceModules = evidenceModulesGlob;

function hasRealEvidence(goalNumber: string): boolean {
    const modulePath = evidencePathLookup[goalNumber];
    if (!modulePath) return false;

    const metadata = evidenceMetadata[modulePath];
    // If no metadata or visible is not explicitly false, consider it real evidence
    return metadata?.visible !== false;
}

export function loadAllGoals(): Category[] {
    const goals: LearningGoal[] = [];

    let verificationData: Record<string, string> = {};
    try {
        // VERIFICATION.jsonc is in the root
        const verifications = import.meta.glob(
            "../../VERIFICATION.jsonc",
            { query: '?raw', import: 'default', eager: true }
        );
        for (const [key, rawContent] of Object.entries(verifications)) {
            const jsonText = (rawContent as string).replace(/\/\/.*$/gm, '');
            verificationData = JSON.parse(jsonText);
            break; // only one match
        }
    } catch (e) {
        console.warn("Failed to load root VERIFICATION.jsonc", e);
    }

    for (const [path, module] of Object.entries(goalModules)) {
        const goalData = module.default;
        // Path format: ../../learning_goals/{category}/{goalNumber}/goal.json
        const pathMatch = path.match(/\/(\d+)\/(\d+\.\d+)\/goal\.json$/);
        if (!pathMatch) continue;

        const categoryNumber = parseInt(pathMatch[1]);
        const goalNumber = pathMatch[2];

        // Override verified status if present in VERIFICATION.jsonc
        let verifiedName = "";
        let goalStatus = goalData.status;

        if (verificationData[goalNumber] && verificationData[goalNumber].trim() !== "") {
            verifiedName = verificationData[goalNumber].trim();
            goalStatus = "Verified";
        }

        goals.push({
            ...goalData,
            status: goalStatus as Status,
            verified: verifiedName,
            number: goalNumber,
            category:
                categoryNames[categoryNumber] || `Category ${categoryNumber}`,
            categoryNumber,
            evidencePath: evidencePathLookup[goalNumber] || "",
            hasEvidence: hasRealEvidence(goalNumber),
        });
    }

    goals.sort((a, b) => {
        const [aMajor, aMinor] = a.number.split(".").map(Number);
        const [bMajor, bMinor] = b.number.split(".").map(Number);
        if (aMajor !== bMajor) return aMajor - bMajor;
        return aMinor - bMinor;
    });

    const categoriesMap = new Map<number, Category>();

    for (const goal of goals) {
        if (!categoriesMap.has(goal.categoryNumber)) {
            categoriesMap.set(goal.categoryNumber, {
                number: goal.categoryNumber,
                name: goal.category,
                goals: [],
            });
        }
        categoriesMap.get(goal.categoryNumber)!.goals.push(goal);
    }

    return Array.from(categoriesMap.values()).sort(
        (a, b) => a.number - b.number
    );
}

export function filterGoals(
    categories: Category[],
    trackFilter: Track[],
    statusFilter: Status[],
    searchQuery: string,
    evidenceFilter: "all" | "with_evidence" | "without_evidence"
): Category[] {
    const query = searchQuery.toLowerCase().trim();

    return categories
        .map((category) => ({
            ...category,
            goals: category.goals.filter((goal) => {
                // Check if goal has any overlapping track with the selected tracks
                const hasMatchingTrack = goal.track.some((t) =>
                    trackFilter.includes(t)
                );
                if (!hasMatchingTrack) {
                    return false;
                }

                // Check if goal status is in the selected statuses
                if (!statusFilter.includes(goal.status)) {
                    return false;
                }

                // Check evidence filter
                if (evidenceFilter === "with_evidence" && !goal.hasEvidence) {
                    return false;
                }
                if (evidenceFilter === "without_evidence" && goal.hasEvidence) {
                    return false;
                }

                if (query) {
                    const searchable =
                        `${goal.number} ${goal.title}`.toLowerCase();
                    if (!searchable.includes(query)) {
                        return false;
                    }
                }

                return true;
            }),
        }))
        .filter((category) => category.goals.length > 0);
}
