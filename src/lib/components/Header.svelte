<script lang="ts">
    import type { Snippet } from "svelte";
    import { user } from "$lib/user.svelte";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
</script>

<header class="header">
    <div class="header-content">
        <div class="title-block">
            <h1>{user}</h1>
            <div class="accent-line"></div>
        </div>
        <p class="subtitle">Learning Goals Portfolio</p>
    </div>

    {@render children()}
</header>

<style>
    .header {
        background: #f3f4f6;
        border: 1px solid rgb(0 0 0 / 0.1);
        border-top-left-radius: 1rem;
        border-top-right-radius: 1rem;
        box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        padding: 2rem;
        margin-top: 2rem;
        position: relative;
    }

    .header-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .title-block {
        display: inline-block;

        h1 {
            font-size: 2.25rem;
            font-weight: 700;
            color: var(--color-primary);
            margin-bottom: 0.5rem;
        }

        .accent-line {
            height: 0.25rem;
            background: var(--color-accent);
            border-radius: 9999px;
        }
    }

    .subtitle {
        margin-top: 1rem;
        font-size: 1.125rem;
        color: #4b5563;
    }

    @media (min-width: 768px) {
        .title-block h1 {
            font-size: 3rem;
        }
    }
</style>
