<script lang="ts">
    interface Props {
        src: string;
        alt?: string;
        caption?: string;
    }

    let { src, alt = "", caption }: Props = $props();

    import { getContext } from "svelte";
    import { resolveAssetPath } from "$lib/assets";

    const context = getContext("evidence") as
        | { categoryNumber: number; goalNumber: string }
        | undefined;

    let resolvedSrc = $derived.by(() => {
        if (!context) return src;
        if (src.startsWith("http://") || src.startsWith("https://")) return src;

        const resolved = resolveAssetPath(
            context.categoryNumber,
            context.goalNumber,
            src,
        );
        if (!resolved) {
            console.warn(
                `Could not resolve asset: ${src} for goal ${context.goalNumber}`,
            );
            return src;
        }
        return resolved;
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
