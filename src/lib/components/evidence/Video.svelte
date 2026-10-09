<script lang="ts">
    interface Props {
        src: string;
        caption?: string;
        controls?: boolean;
        autoplay?: boolean;
        loop?: boolean;
        muted?: boolean;
    }

    let {
        src,
        caption,
        controls = true,
        autoplay = false,
        loop = false,
        muted = false,
    }: Props = $props();

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

<figure class="evidence-video">
    <video src={resolvedSrc} {controls} {autoplay} {loop} {muted} playsinline>
        <track kind="captions" />
        Your browser does not support video playback.
    </video>
    {#if caption}
        <figcaption>{caption}</figcaption>
    {/if}
</figure>

<style>
    .evidence-video {
        margin: 1.5rem 0;
        text-align: center;

        video {
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
