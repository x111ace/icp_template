<script lang="ts">
    import { onMount } from 'svelte';
    import { loadAllItems, createNewItem, initializeState } from './main';
    import type { Item } from 'declarations/backend/backend.did';
    import './styles/main-page.css';

    let items: Item[] = [];
    let loading = true;
    let itemName = '';
    let itemDescription = '';
    let creating = false;

    async function handleLoadItems() {
        loading = true;
        try {
            items = await loadAllItems();
        } catch (err) {
            console.error('Failed to load items:', err);
        } finally {
            loading = false;
        }
    }

    async function handleCreateItem() {
        if (!itemName.trim()) return;
        
        creating = true;
        try {
            const result = await createNewItem(itemName, itemDescription);
            
            if (typeof result === 'string') {
                console.error('Create failed:', result);
            } else {
                items = [...items, result];
                itemName = '';
                itemDescription = '';
            }
        } catch (err) {
            console.error('Failed to create item:', err);
        } finally {
            creating = false;
        }
    }

    onMount(() => {
        handleLoadItems();
    });
</script>

<div class="main-container">
    <h1>ICP Items Manager</h1>
    
    <div class="create-form">
        <h2>Create New Item</h2>
        <input 
            type="text" 
            placeholder="Item name" 
            bind:value={itemName}
            disabled={creating}
        />
        <input 
            type="text" 
            placeholder="Description" 
            bind:value={itemDescription}
            disabled={creating}
        />
        <button on:click={handleCreateItem} disabled={creating || !itemName.trim()}>
            {creating ? 'Creating...' : 'Create Item'}
        </button>
    </div>

    <div class="items-list">
        <h2>All Items ({items.length})</h2>
        {#if loading}
            <p>Loading...</p>
        {:else if items.length === 0}
            <p>No items yet. Create one above!</p>
        {:else}
            <ul>
                {#each items as item (item.id)}
                    <li>
                        <strong>{item.name}</strong>
                        <p>{item.description}</p>
                        <small>Owner: {item.owner.toString().slice(0, 10)}...</small>
                    </li>
                {/each}
            </ul>
        {/if}
    </div>
</div> 