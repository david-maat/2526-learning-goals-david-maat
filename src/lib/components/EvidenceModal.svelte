<script lang="ts">
    import type { LearningGoal } from "$lib/types";
    import type { Component } from "svelte";
    import ProjectInfo from "./ProjectInfo.svelte";

    interface Props {
        goal: LearningGoal | null;
        EvidenceComponent?: Component | null;
        isLoading?: boolean;
        hideProjectDrawer?: boolean;
        onClose: () => void;
    }

    let {
        goal,
        EvidenceComponent = null,
        isLoading = false,
        hideProjectDrawer = false,
        onClose,
    }: Props = $props();

    import { setContext } from "svelte";

    // Create a reactive context object
    // Initialize with default values, they will be updated via the effect
    const evidenceContext = $state({ categoryNumber: 0, goalNumber: "" });
    setContext("evidence", evidenceContext);

    $effect(() => {
        if (goal) {
            evidenceContext.categoryNumber = goal.categoryNumber;
            evidenceContext.goalNumber = goal.number;
        }
    });

    function handleBackdropClick(e: MouseEvent) {
        if (e.target === e.currentTarget) {
            onClose();
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === "Escape") {
            onClose();
        }
    }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if goal}
    <div
        class="modal-backdrop"
        onclick={handleBackdropClick}
        onkeydown={handleKeydown}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabindex="-1"
    >
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modal-title">{goal.number} {goal.title}</h2>
                <button class="close-btn" onclick={onClose} aria-label="Close">
                    x
                </button>
            </div>
            <div class="modal-body">
                {#if goal.project && goal.project.length > 0 && !hideProjectDrawer}
                    <div class="projects-container">
                        {#each goal.project as projectName}
                            <ProjectInfo {projectName} />
                        {/each}
                    </div>
                {/if}

                {#if isLoading}
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Loading evidence...</p>
                    </div>
                {:else if EvidenceComponent}
                    <EvidenceComponent />
                {:else}
                    <p class="no-evidence">No evidence provided yet.</p>
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
    .modal-backdrop {
        position: fixed;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgb(0 0 0 / 0.6);
        backdrop-filter: blur(4px);
        z-index: 900;
    }

    .modal-content {
        position: relative;
        width: 91.666667%;
        max-width: 86rem;
        max-height: 80vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
    }

    .modal-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        padding: 1rem 1.5rem;
        background: linear-gradient(to right, var(--color-primary), #004165);

        h2 {
            font-size: 1.25rem;
            font-weight: 700;
            color: white;
            margin: 0;
        }
    }

    .close-btn {
        padding: 0.25rem 0.75rem;
        background: none;
        border: none;
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        cursor: pointer;
        border-radius: 0.5rem;
        transition: color 0.2s;

        &:hover {
            color: #fca5a5;
        }
    }

    .modal-body {
        padding: 0 1.5rem;
        flex: 1 1 auto;
        overflow-y: auto;
        color: #374151;
        line-height: 1.625;
        padding-top: 1.5rem;

        .projects-container {
            margin-bottom: 2rem;
        }

        :global(h1),
        :global(h2),
        :global(h3) {
            color: var(--color-primary);
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }

        :global(h1) {
            font-size: 1.5rem;
        }

        :global(h2) {
            font-size: 1.25rem;
        }

        :global(p) {
            margin-bottom: 1rem;
        }

        :global(ul),
        :global(ol) {
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }

        :global(code) {
            font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Monaco', 'Consolas', monospace;
            font-variant-ligatures: contextual;
            background-color: #f3f4f6;
            color: #00293F;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            font-size: 0.85em;
            border: 1px solid #e5e7eb;
        }

        :global(pre) {
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 2.5rem 1rem 1rem 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
            font-size: 0.9rem;
            line-height: 1.6;
            position: relative;
            box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
        }

        :global(pre)::before {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1.5rem;
            background: #252526;
            color: #969696;
            font-size: 0.7rem;
            padding: 0 1rem;
            display: flex;
            align-items: center;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid #333;
        }

        :global(pre code) {
            background: transparent;
            color: inherit;
            padding: 0;
            border-radius: 0;
            font-size: inherit;
            border: none;
        }

        :global(a) {
            color: var(--color-accent);
            text-decoration: underline;
            transition: color 0.2s;

            &:hover {
                color: #fca5a5;
            }
        }
    }

    .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        padding: 3rem;
        color: #6b7280;
    }

    .spinner {
        width: 2.5rem;
        height: 2.5rem;
        border: 3px solid #e5e7eb;
        border-top-color: var(--color-accent);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .no-evidence {
        color: #9ca3af;
        font-style: italic;
        text-align: center;
        padding: 2rem;
    }

    @media (min-width: 768px) {
        .modal-header h2 {
            font-size: 1.5rem;
        }
    }
</style>
