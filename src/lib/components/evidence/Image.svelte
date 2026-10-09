<script lang="ts">
    interface Props {
        src: string;
        alt?: string;
        caption?: string;
    }

    let { src, alt = "", caption }: Props = $props();

    import { getContext } from "svelte";
    import { resolveAssetPath, resolveProjectAssetPath } from "$lib/assets";

    const context = getContext("evidence") as
        | { categoryNumber: number; goalNumber: string }
        | undefined;

    const projectContext = getContext("project") as
        | { projectName: string }
        | undefined;

    let resolvedSrc = $derived.by(() => {
        if (src.startsWith("http://") || src.startsWith("https://")) return src;
        if (src.startsWith("/") || src.startsWith("\\")) return src;

        // Try project context first
        if (projectContext) {
            const resolved = resolveProjectAssetPath(src);
            if (resolved) return resolved;
        }

        // Fallback to evidence context
        if (context) {
            const resolved = resolveAssetPath(
                context.categoryNumber,
                context.goalNumber,
                src,
            );
            if (resolved) return resolved;
        }

        console.warn(`Could not resolve asset: ${src}`);
        return src;
    });
</script>

<figure class="evidence-image">
    <img src={resolvedSrc} {alt} loading="lazy" />
    {#if caption}
        <figcaption>{caption}</figcaption>
    {/if}
</figure>

<style>
    .evidence-image {
        margin: 1.5rem 0;
        text-align: center;

        img {
            max-width: 100%;
            height: auto;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }

        figcaption {
            margin-top: 0.5rem;
            font-size: 0.875rem;
            color: #6b7280;
            font-style: italic;
        }
    }
</style>
