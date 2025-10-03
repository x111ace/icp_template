import { Actor, HttpAgent } from '@dfinity/agent';
import { idlFactory } from 'declarations/backend';
import type { _SERVICE } from 'declarations/backend/backend.did';
import { browser } from '$app/environment';

let actor: _SERVICE | null = null;

export async function getActor(): Promise<_SERVICE> {
    if (actor) return actor;

    const canisterId = process.env.CANISTER_ID_BACKEND as string;
    const host = process.env.DFX_NETWORK === 'ic' 
        ? 'https://ic0.app' 
        : 'http://127.0.0.1:4943';

    const agent = new HttpAgent({ host });

    // Fetch root key for local development
    if (process.env.DFX_NETWORK !== 'ic' && browser) {
        await agent.fetchRootKey().catch(err => {
            console.warn('Unable to fetch root key:', err);
        });
    }

    actor = Actor.createActor<_SERVICE>(idlFactory, {
        agent,
        canisterId,
    });

    return actor;
}
