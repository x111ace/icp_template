import { getActor } from '$lib/actor';
import type { Item } from 'declarations/backend/backend.did';

export interface MainPageState {
    items: Item[];
    loading: boolean;
    creating: boolean;
}

export async function loadAllItems(): Promise<Item[]> {
    const actor = await getActor();
    return await actor.get_all_items();
}

export async function createNewItem(name: string, description: string): Promise<Item | string> {
    const actor = await getActor();
    const result = await actor.create_item({ name, description });
    
    if ('Ok' in result) {
        return result.Ok;
    } else {
        return result.Err;
    }
}

export async function deleteExistingItem(id: bigint): Promise<string> {
    const actor = await getActor();
    const result = await actor.delete_item(id);
    
    if ('Ok' in result) {
        return result.Ok;
    } else {
        throw new Error(result.Err);
    }
}

export function initializeState(): MainPageState {
    return {
        items: [],
        loading: true,
        creating: false
    };
}
