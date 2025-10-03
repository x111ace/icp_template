import os, json, shutil, argparse, subprocess, platform

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Platform detection for cross-platform compatibility
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# Colorama for colored terminal output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    RRR = Style.RESET_ALL
    BRT = Style.BRIGHT
    DIM = Style.DIM
    RED = Fore.RED
    GRN = Fore.GREEN
    YLW = Fore.YELLOW
    BLU = Fore.BLUE
    MGN = Fore.MAGENTA
    CYN = Fore.CYAN
except ImportError:
    # Fallback for systems without colorama
    RRR = BRT = DIM = RED = GRN = YLW = BLU = MGN = CYN = ""

# ICP-specific exclusions
JSPROJECT_EXCLUDE = {".svelte-kit", "dist", "node_modules", "package-lock.json", "build"}
ICP_EXCLUDE = {".dfx", "backend.did", "src"}  # src/ contains auto-generated declarations
RSPROJECT_EXCLUDE = {"target", "Cargo.lock", "cargo"}
PYPROJECT_EXCLUDE = {"__pycache__", "venv"}
EXCLUDE_ALL = {".vscode", ".cursor"} | PYPROJECT_EXCLUDE | JSPROJECT_EXCLUDE | RSPROJECT_EXCLUDE | ICP_EXCLUDE

# Tree view exclusions (don't exclude src from tree, only from clean)
TREE_EXCLUDE = EXCLUDE_ALL | {".git"} - {"src"}
TREE_EXCLUDE.add("declarations")  # Hide declarations subfolder in tree

# Language extensions
PROG_LANG_EXTS = {
    ".py": "Python", 
    ".ipynb": "Jupyter Notebook",
    ".rs": "Rust", 
    ".js": "JavaScript", 
    ".ts": "TypeScript", 
    ".c": "C",
    ".cpp": "C++", 
    ".h": "C/C++ Header", 
    ".java": "Java", 
    ".html": "HTML",
    ".css": "CSS", 
    ".sh": "Shell Script",
    ".svelte": "Svelte",
    ".toml": "TOML",
    ".json": "JSON",
    ".md": "Markdown"
}

def project_tree(root_dir: str, output: bool = False) -> str:
    """Generate file tree with stats."""
    tree_lines = []
    stats = {"folders": 0, "files": {"total": 0, "by_type": {}}}

    def count_lines(path: str) -> int:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0

    def process_dir(dir_path: str, prefix: str = ""):
        try:
            entries = sorted(os.listdir(dir_path), 
                           key=lambda e: (os.path.isfile(os.path.join(dir_path, e)), e.lower()))
        except:
            return
        
        entries = [e for e in entries if e not in TREE_EXCLUDE]
        
        for i, entry in enumerate(entries):
            path = os.path.join(dir_path, entry)
            connector = "└── " if i == len(entries) - 1 else "├── "
            
            if os.path.isdir(path):
                stats["folders"] += 1
                tree_lines.append(f"{prefix}{connector}{BRT}{BLU}{entry}{RRR}/")
                extension = "    " if i == len(entries) - 1 else "│   "
                process_dir(path, prefix + extension)
            else:
                stats["files"]["total"] += 1
                ext = os.path.splitext(entry)[1]
                lang = PROG_LANG_EXTS.get(ext)
                
                if lang:
                    lines = count_lines(path)
                    lang_stats = stats["files"]["by_type"].setdefault(lang, {'files': 0, 'lines': 0})
                    lang_stats['files'] += 1
                    lang_stats['lines'] += lines
                    tree_lines.append(f"{prefix}{connector}{entry} :: {GRN}{lines}{RRR} lines")
                else:
                    tree_lines.append(f"{prefix}{connector}{entry}")

    root_label = f"{BLU}{os.path.basename(SCRIPT_DIR)}{RRR}/"
    tree_lines.append(root_label)
    process_dir(SCRIPT_DIR)
    
    if output:
        print(json.dumps(stats, indent=2))
        print("\n".join(tree_lines))
    
    return "\n".join(tree_lines)

def clean_project(output: bool = False):
    """Remove build artifacts and dependencies."""
    if output:
        print(f"{CYN}Cleaning project...{RRR}")
    
    to_remove = []
    for root, dirs, files in os.walk(SCRIPT_DIR, topdown=True):
        for d in list(dirs):
            if d in EXCLUDE_ALL:
                to_remove.append(os.path.join(root, d))
                dirs.remove(d)
    
    for path in to_remove:
        if os.path.exists(path):
            try:
                shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
                if output:
                    print(f"{GRN}Removed: {path}{RRR}")
            except Exception as e:
                if output:
                    print(f"{RED}Failed to remove {path}: {e}{RRR}")
    
    if output:
        print(f"{GRN}Clean complete.{RRR}")

def build_frontend(output: bool = False):
    """Build the SvelteKit frontend."""
    if output:
        print(f"{CYN}Building frontend...{RRR}")
    
    frontend_dir = os.path.join(SCRIPT_DIR, "frontend")
    
    try:
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        if output:
            print(f"{GRN}Frontend build complete.{RRR}")
    except subprocess.CalledProcessError as e:
        if output:
            print(f"{RED}Frontend build failed: {e}{RRR}")
        raise

def restart_replica(output: bool = False):
    """Stop, clean start, and deploy canisters."""
    if output:
        print(f"{CYN}Restarting IC replica...{RRR}")
    
    try:
        subprocess.run(["dfx", "stop"], cwd=SCRIPT_DIR, check=False)
        if output:
            print(f"{YLW}Replica stopped.{RRR}")
        
        subprocess.run(["dfx", "start", "--background", "--clean"], cwd=SCRIPT_DIR, check=True)
        if output:
            print(f"{GRN}Replica started.{RRR}")
        
    except subprocess.CalledProcessError as e:
        if output:
            print(f"{RED}Replica operation failed: {e}{RRR}")
        raise

def deploy_backend(output: bool = False):
    """Deploy the backend canisters."""
    if output:
        print(f"{CYN}Deploying backend...{RRR}")
    
    subprocess.run(["dfx", "deploy"], cwd=SCRIPT_DIR, check=True)
    if output:
        print(f"{GRN}Backend deployed.{RRR}")

def rebuild(output: bool = False):
    """Full rebuild: replica + backend + frontend."""
    if output:
        print(f"{BRT}{CYN}--- Full Rebuild ---{RRR}")
    
    restart_replica(output)      # Start replica
    deploy_backend(output)       # Deploy backend (generates backend.did)
    build_frontend(output)       # Build frontend (uses backend.did)

    if output:
        print(f"{BRT}{GRN}--- Rebuild complete! ---{RRR}")

def main():
    parser = argparse.ArgumentParser(description="ICP Svelte project manager")
    parser.add_argument("-t", "--tree", action="store_true", help="Show project tree")
    parser.add_argument("-c", "--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("-fb", "--frontend", action="store_true", help="Build frontend only")
    parser.add_argument("-r", "--replica", action="store_true", help="Restart replica canisters and deploy")
    parser.add_argument("-rb", "--rebuild", action="store_true", help="Full rebuild (frontend + replica)")
    
    args = parser.parse_args()

    if args.tree:
        project_tree(SCRIPT_DIR, output=True)
    elif args.clean:
        clean_project(output=True)
    elif args.frontend:
        build_frontend(output=True)
    elif args.replica:
        restart_replica(output=True)
        deploy_backend(output=True)
    elif args.rebuild:
        rebuild(output=True)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
