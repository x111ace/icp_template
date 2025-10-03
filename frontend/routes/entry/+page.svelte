<script lang="ts">
    import { onMount } from 'svelte';
    import { initializePage, navigateToMain } from './entry';
    import './styles/entry-page.css';

    let principal = '';

    onMount(async () => {
        const state = await initializePage();
        principal = state.principal;
    });
</script>

<div class="entry-page-container">
    <h1>ICP + Svelte Template</h1>
    <p class="principal-display">Your Principal: <span class="principal-value">{principal || 'Loading...'}</span></p>
    <button on:click={navigateToMain} class="centered-button">Enter Main Page</button>
</div>
