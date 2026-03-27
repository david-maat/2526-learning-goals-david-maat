<script lang="ts">
    import "./layout.css";
    import favicon from "$lib/assets/favicon.ico";
    import { user } from "$lib/user.svelte";

    let { children } = $props();
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
    <title>{user} | Learning Goals</title>
    <meta
        name="description"
        content="Learning Goals Portfolio for Thomas More Geel - Digital Innovation"
    />
</svelte:head>

{@render children()}
