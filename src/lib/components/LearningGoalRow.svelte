<script lang="ts">
    import type { LearningGoal } from "$lib/types";
    import { get } from "svelte/store";
    import StatusBadge from "./StatusBadge.svelte";
    import TrackBadge from "./TrackBadge.svelte";

    interface Props {
        goal: LearningGoal;
        onViewEvidence: (goal: LearningGoal) => void;
    }

    let { goal, onViewEvidence }: Props = $props();

    function handleRowClick() {
        if (goal.hasEvidence) {
            onViewEvidence(goal);
        }
    }

    function handleKeyDown(e: KeyboardEvent) {
        if (goal.hasEvidence && (e.key === "Enter" || e.key === " ")) {
            e.preventDefault();
            onViewEvidence(goal);
        }
    }

    function getColor() {
        if (goal.verified) {
            return "bg-blue-100";
        } else if (goal.status == "Done") {
            return "bg-emerald-100";
        } else if (goal.status == "In Progress") {
            return "bg-amber-100";
        } else {
            return "";
        }
    }
</script>

<tr
    class="goal-row {getColor()}"
    class:clickable={goal.hasEvidence}
    onclick={handleRowClick}
    onkeydown={handleKeyDown}
    role={goal.hasEvidence ? "button" : undefined}
    tabindex={goal.hasEvidence ? 0 : undefined}
>
    <td class="goal-title">
        <span class="goal-number">{goal.number}</span>
        {goal.title}
    </td>
    <td class="goal-track">
        <TrackBadge tracks={goal.track} />
    </td>
    <td class="goal-status">
        <StatusBadge status={goal.status} />
    </td>
    <td class="goal-verified">
        {goal.verified || "-"}
    </td>
    <td class="goal-project">
        {goal.project?.join(", ") || "-"}
    </td>
    <td class="goal-evidence">
        {#if goal.hasEvidence}
            <button
                class="evidence-btn"
                onclick={(e) => {
                    e.stopPropagation();
                    onViewEvidence(goal);
                }}
            >
                View
            </button>
        {:else}
            <span class="no-evidence">-</span>
        {/if}
    </td>
</tr>

<style>
    .goal-row {
        transition:
            background-color 0.2s,
            scale 0.2s;

        &:hover {
            scale: 1.02;
        }

        &.clickable {
            cursor: pointer;

            &:hover {
                opacity: 0.9;
            }

            &:focus {
                outline: 2px solid var(--color-accent);
                outline-offset: -2px;
            }
        }

        td {
            padding: 1rem 1.5rem;
            text-align: center;
            vertical-align: middle;
        }
    }

    .goal-title {
        text-align: left !important;
        color: #374151;

        .goal-number {
            font-weight: 700;
            color: var(--color-primary);
            margin-right: 0.5rem;
        }
    }

    .goal-verified,
    .goal-project {
        color: #6b7280;
        font-size: 0.875rem;
    }

    .evidence-btn {
        padding: 0.375rem 1rem;
        background: linear-gradient(to right, var(--color-primary), #004165);
        color: white;
        border: none;
        border-radius: 0.375rem;
        font-size: 0.75rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
    }

    .no-evidence {
        color: #d1d5db;
    }
</style>
