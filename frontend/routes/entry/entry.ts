import { getActor } from '$lib/actor';
import { goto } from '$app/navigation';

export interface EntryPageState {
    principal: string;
}

export async function initializePage(): Promise<EntryPageState> {
    const actor = await getActor();
    const principal = await actor.whoami();
    
    return {
        principal
    };
}

export async function navigateToMain(): Promise<void> {
    await goto('/main');
}
