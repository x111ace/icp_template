<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    
    onMount(() => {
        goto('/entry', { replaceState: true });
    });
</script>

<p>Loading...</p>
