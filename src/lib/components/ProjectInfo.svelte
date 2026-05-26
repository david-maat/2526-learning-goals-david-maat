<script lang="ts">
    import { projectModules } from "$lib/loadGoals";
    import { setContext } from "svelte";
    import { slide } from "svelte/transition";

    interface Props {
        projectName: string;
    }

    let { projectName }: Props = $props();

    // Find the module that matches the project name reactively
    let moduleKey = $derived(
        Object.keys(projectModules).find((key) =>
            key.endsWith(`/${projectName}.svx`),
        ),
    );
    let projectModule = $derived(moduleKey ? projectModules[moduleKey] : null);

    let isOpen = $state(false);

    $effect(() => {
        if (projectModule?.metadata?.startsOpened) {
            isOpen = true;
        }
    });

    setContext("project", {
        get projectName() {
            return projectName;
        },
    });
</script>

{#if projectModule}
    <div
        class="mb-6 overflow-hidden rounded-2xl border transition-all duration-300 ease-in-out {isOpen
            ? 'border-[#00293F]/20 bg-white shadow-lg -translate-y-0.5'
            : 'border-[#00293F]/10 bg-white/70 shadow-sm backdrop-blur-md'}"
    >
        <button
            class="group flex w-full cursor-pointer items-center justify-between transition-colors hover:bg-gray-100 duration-200 gap-4 p-4 text-left"
            onclick={() => (isOpen = !isOpen)}
            aria-expanded={isOpen}
        >
            <div class="flex items-center gap-4">
                <div
                    class="flex h-10 w-10 items-center justify-center rounded-xl bg-gray-100 text-[#00293F] transition-all duration-200 group-hover:scale-110"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><path
                            d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z"
                        /><path
                            d="M3 9V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4"
                        /><path d="M12 12v4" /><path d="M9 14h6" /></svg
                    >
                </div>
                <div class="flex flex-col">
                    <span
                        class="text-[0.7rem] font-semibold uppercase tracking-wider text-gray-500"
                        >Project</span
                    >
                    <h3 class="text-base my-0.5! font-bold text-[#00293F]">
                        {projectName}
                    </h3>
                </div>
            </div>
            <div class="flex items-center gap-3">
                {#if projectModule.metadata.duration}
                    <span
                        class="whitespace-nowrap rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-600"
                    >
                        {projectModule.metadata.duration}
                    </span>
                {/if}
                <div
                    class="text-gray-400 transition-transform duration-300 {isOpen
                        ? 'rotate-180 text-[#00293F]'
                        : ''}"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"><path d="m6 9 6 6 6-6" /></svg
                    >
                </div>
            </div>
        </button>

        {#if isOpen}
            <div
                class="border-t border-gray-100"
                transition:slide={{ duration: 300 }}
            >
                <div class="p-6">
                    <div class="project-content-inner">
                        <projectModule.default />
                    </div>
                </div>
            </div>
        {/if}
    </div>
{:else}
    <!-- <div
        class="mb-6 rounded-xl border border-dashed border-rose-500 bg-rose-50 p-4 text-sm text-rose-700"
    >
        <p>
            Metadata for project "<strong>{projectName}</strong>" missing in
            <code>/learning_goals/projects/</code>
        </p>
    </div> -->
{/if}

<style>
    .project-content-inner {
        :global(h1) {
            display: none;
        }

        :global(h2) {
            font-size: 1.125rem;
            margin-top: 0;
            color: #00293f;
            font-weight: 700;
            margin-bottom: 0.75rem;
        }

        :global(p) {
            font-size: 0.95rem;
            color: #4b5563;
            margin-bottom: 1rem;
        }
    }
</style>
