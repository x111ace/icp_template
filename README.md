# ICP Rust + Svelte Template

Production-ready template for building decentralized applications on the Internet Computer.

## Stack

- **Backend:** Rust canister with stable memory (`ic-stable-structures`)
- **Frontend:** SvelteKit + TypeScript
- **ICP SDK:** dfx for deployment and canister management

## Features

✅ Stable storage (persists across upgrades)  
✅ Memory manager with auto-incrementing IDs  
✅ Principal-based authentication  
✅ Full CRUD operations example  
✅ Auto-generated TypeScript bindings from Candid  
✅ Modular code architecture  

## Prerequisites

### Downloading WSL (if on Windows)



### Using Conda (Recommended)

Do you already have dfx & Rust?:

```bash
# Verify
dfx --version
cargo --version
```

Download dfx and Rust on WSL:

```bash
# Install dfx & Rust
sh -ci "$(curl -fsSL https://internetcomputer.org/install.sh)"
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Do you already have Conda?:

```bash
# Verify
conda --version
```

Download Miniconda3 on WSL:

```bash
# Download Miniconda installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Run installer
bash Miniconda3-latest-Linux-x86_64.sh

# Follow prompts, say 'yes' to init conda

# Reload shell
source ~/.bashrc

# Verify
conda --version

# Clean up installer
rm Miniconda3-latest-Linux-x86_64.sh

# Accept ToS
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

Set-up your project:

```bash
conda create -n icp_project_name python nodejs -y
conda activate icp_project_name

# Install wasm target
rustup target add wasm32-unknown-unknown

# candid-extractor
cargo install candid-extractor

# Python dependencies (for __mgr__.py)
pip install -r requirements.txt
```

## Development Workflow

```bash
# Activate environment
conda activate icp_project_name

# Full rebuild (recommended after any changes)
python __mgr__.py -rb

# Or individually:
python __mgr__.py -fb    # Build frontend only
python __mgr__.py -r     # Restart replica only

# Watch frontend changes (hot reload)
cd frontend && npm run dev

# View Candid UI
dfx canister call backend --candid
```

## Quick Start

```bash
# Activate conda environment (if using conda)
conda activate icp_project_name

# 1. Install dependencies
npm install

# 2. Full rebuild (frontend + replica + deploy)
python __mgr__.py -rb

# Frontend URL will be shown in terminal:
# http://[canister-id].localhost:4943/
```

### Manual Commands (Alternative)

```bash
# Build frontend
cd frontend && npm run build && cd ..

# Start replica and deploy
dfx stop
dfx start --background --clean
dfx deploy
```

## Project Structure

```
icp_rust-svelte_template/
├── backend/
│   ├── lib.rs              # Canister logic
│   ├── Cargo.toml          # Rust dependencies
│   └── backend.did         # Generated Candid interface
├── frontend/
│   ├── lib/
│   │   └── actor.ts        # ICP actor initialization
│   ├── routes/
│   │   ├── entry/
│   │   │   ├── entry.ts    # Entry page logic
│   │   │   ├── +page.svelte
│   │   │   └── styles/
│   │   └── main/
│   │       ├── main.ts     # Main page logic (CRUD)
│   │       ├── +page.svelte
│   │       └── styles/
│   ├── static/             # Static assets
│   ├── app.html            # HTML shell
│   ├── package.json
│   └── svelte.config.js
├── src/declarations/       # Auto-generated (gitignored)
├── dfx.json                # ICP configuration
├── Cargo.toml              # Workspace manifest
└── package.json            # Root scripts
```

## Architecture Patterns

### Modular Pages
Each route has:
- `[name].ts` - Pure functions (API calls, state)
- `+page.svelte` - UI rendering + minimal glue
- `styles/[name]-page.css` - Scoped styles

### Backend Functions
- **Queries** (`#[ic_cdk::query]`) - Read-only, fast
- **Updates** (`#[ic_cdk::update]`) - State-changing, consensus

### Type Safety
Generated TypeScript types from Candid ensure end-to-end type safety.

## Commands Reference

### Manager Script

```bash
# Show project tree
python __mgr__.py -t
# Clean artifacts
python __mgr__.py -c
# Build frontend
python __mgr__.py -fb
# Restart replica
python __mgr__.py -r
# Full rebuild
python __mgr__.py -rb
```

### dfx Commands

```bash
# Deploy specific canister
dfx deploy backend
dfx deploy frontend

# Check canister status
dfx canister status backend

# View canister IDs
dfx canister id backend

# Stop local replica
dfx stop

# Clean restart
dfx start --background --clean
```

## Deploying to Mainnet

```bash
# Get cycles (requires ICP tokens)
dfx wallet --network ic balance

# Deploy to mainnet
dfx deploy --network ic
```

See `BUILD.md` for detailed mainnet deployment guide.

## Extending the Template

**Add new backend functions:**
1. Define in `backend/lib.rs`
2. Run `dfx deploy backend`
3. TypeScript types auto-update in `src/declarations/`

**Add new routes:**
1. Create `frontend/routes/[name]/`
2. Add `[name].ts` for logic
3. Add `+page.svelte` for UI

## Troubleshooting

**"Cannot find declarations"** - Run `dfx generate backend`  
**Port 4943 in use** - Run `dfx stop` then restart  
**Stable memory errors** - Use `dfx start --clean`  

## License

MIT
