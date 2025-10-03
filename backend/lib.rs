use candid::{CandidType, Principal};
use ic_cdk::api::{time, msg_caller};
use ic_stable_structures::{storable::Bound,
    DefaultMemoryImpl, StableBTreeMap, StableCell, Storable,
    memory_manager::{MemoryId, MemoryManager, VirtualMemory},
};
use serde::{Deserialize, Serialize};
use std::cell::RefCell;
use std::borrow::Cow;

// Type aliases for stable storage
type Memory = VirtualMemory<DefaultMemoryImpl>;
type ItemId = u64;

// ==================== Data Structures ====================

#[derive(CandidType, Serialize, Deserialize, Clone)]
pub struct Item {
    pub id: ItemId,
    pub owner: Principal,
    pub name: String,
    pub description: String,
    pub created_at: u64,
    pub updated_at: u64,
}

#[derive(CandidType, Serialize, Deserialize)]
pub struct CreateItemRequest {
    pub name: String,
    pub description: String,
}

#[derive(CandidType, Serialize, Deserialize)]
pub struct UpdateItemRequest {
    pub id: ItemId,
    pub name: String,
    pub description: String,
}

// ==================== Storable Implementation ====================

impl Storable for Item {
    fn to_bytes(&self) -> Cow<'_, [u8]> {
        Cow::Owned(serde_json::to_vec(self).expect("failed to serialize Item"))
    }

    fn from_bytes(bytes: Cow<[u8]>) -> Self {
        serde_json::from_slice(&bytes).expect("failed to deserialize Item")
    }

    const BOUND: Bound = Bound::Unbounded;
}

// ==================== Memory Manager ====================

thread_local! {
    static MEMORY_MANAGER: RefCell<MemoryManager<DefaultMemoryImpl>> =
        RefCell::new(MemoryManager::init(DefaultMemoryImpl::default()));

    static ID_COUNTER: RefCell<StableCell<u64, Memory>> = RefCell::new(
        StableCell::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(0))),
            0
        ).expect("failed to initialize ID counter")
    );

    static ITEMS: RefCell<StableBTreeMap<ItemId, Item, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(1)))
        )
    );
}

// ==================== Helper Functions ====================

fn get_caller() -> Principal { msg_caller() }

fn next_id() -> ItemId {
    ID_COUNTER.with(|counter| {
        let mut counter = counter.borrow_mut();
        let id = *counter.get();
        counter.set(id + 1).expect("failed to increment ID");
        id
    })
}

// ==================== Public API ====================

#[ic_cdk::query]
fn whoami() -> String { get_caller().to_string() }

#[ic_cdk::query]
fn get_all_items() -> Vec<Item> {
    ITEMS.with(|items| {
        items
            .borrow()
            .iter()
            .map(|(_, item)| item)
            .collect()
    })
}

#[ic_cdk::query]
fn get_my_items() -> Vec<Item> {
    let caller = get_caller();
    ITEMS.with(|items| {
        items
            .borrow()
            .iter()
            .filter(|(_, item)| item.owner == caller)
            .map(|(_, item)| item)
            .collect()
    })
}

#[ic_cdk::query]
fn get_item(id: ItemId) -> Result<Item, String> {
    ITEMS.with(|items| {
        items
            .borrow()
            .get(&id)
            .ok_or_else(|| format!("Item {} not found", id))
    })
}

#[ic_cdk::update]
fn create_item(req: CreateItemRequest) -> Result<Item, String> {
    let caller = get_caller();
    let id = next_id();
    let now = time();

    let item = Item {
        id,
        owner: caller,
        name: req.name,
        description: req.description,
        created_at: now,
        updated_at: now,
    };

    ITEMS.with(|items| {
        items.borrow_mut().insert(id, item.clone());
    });

    Ok(item)
}

#[ic_cdk::update]
fn update_item(req: UpdateItemRequest) -> Result<Item, String> {
    let caller = get_caller();

    ITEMS.with(|items| {
        let mut items = items.borrow_mut();
        
        let existing = items
            .get(&req.id)
            .ok_or_else(|| format!("Item {} not found", req.id))?;

        if existing.owner != caller {
            return Err("Only the owner can update this item".to_string());
        }

        let updated = Item {
            id: existing.id,
            owner: existing.owner,
            name: req.name,
            description: req.description,
            created_at: existing.created_at,
            updated_at: time(),
        };

        items.insert(req.id, updated.clone());
        Ok(updated)
    })
}

#[ic_cdk::update]
fn delete_item(id: ItemId) -> Result<String, String> {
    let caller = get_caller();

    ITEMS.with(|items| {
        let mut items = items.borrow_mut();
        
        let existing = items
            .get(&id)
            .ok_or_else(|| format!("Item {} not found", id))?;

        if existing.owner != caller {
            return Err("Only the owner can delete this item".to_string());
        }

        items.remove(&id);
        Ok(format!("Item {} deleted successfully", id))
    })
}

// Export Candid interface
ic_cdk::export_candid!();
