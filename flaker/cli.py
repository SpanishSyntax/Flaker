import os
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Role:
    pkgs: list[str]
    hooks: list[str]
    category: str = "General"
    description: str = ""
    ignores: list[str] = field(default_factory=list)


def get_project_name(root_path: Path) -> str:
    return root_path.name.replace(" ", "_")


def find_project_root(current_dir: Path) -> Path:
    """
    Traverse upwards to find the project root.
    Looks for an existing flake.nix or .git folder.
    Falls back to the current directory if nothing is found.
    """
    for p in [current_dir, *current_dir.parents]:
        if (p / "flake.nix").exists() or (p / ".git").exists():
            return p
    return current_dir


def fmt_status(icon: str, name: str, detail: str = "") -> str:
    """Formats shell status messages with ANSI colors and icons."""
    extra = f" ({detail})" if detail else ""
    return (
        f"printf '\\033[1;34m❄️  [flaker]\\033[0m {icon} "
        f"\\033[1m{name}\\033[0m{extra} active\\n'"
    )


def build_builtin_role_registry(folder_name: str) -> dict[str, Role]:
    return {
        # ------------------------------------------------------------
        # Systems & Compiled Languages
        # ------------------------------------------------------------
        "rust": Role(
            category="Systems",
            description="Stable toolchain + rust-analyzer + lldb",
            pkgs=[
                '(rust-bin.stable.latest.default.override { extensions = [ "rust-analyzer" ]; })',
                "cargo-expand",
                "lldb",
            ],
            hooks=[
                f"[ -f Cargo.toml ] || cargo init --name {folder_name}",
                fmt_status("🦀", "Rust", "stable toolchain + rust-analyzer"),
            ],
            ignores=["target/", "**/*.rs.bk"],
        ),
        "c": Role(
            category="Systems",
            description="GCC/Clang + clangd + cmake + ninja",
            pkgs=[
                "gcc",
                "gdb",
                "cmake",
                "pkg-config",
                "gnumake",
                "ninja",
                "clang-tools",
            ],
            hooks=[fmt_status("⚡", "C", "GCC/Clang + clangd")],
            ignores=["build/", "bin/", "*.o", "*.a", "*.so", "compile_commands.json", ".cache/"],
        ),
        "cpp": Role(
            category="Systems",
            description="GCC/Clang + clangd + cmake + ninja",
            pkgs=[
                "gcc",
                "gdb",
                "cmake",
                "pkg-config",
                "gnumake",
                "ninja",
                "clang-tools",
            ],
            hooks=[fmt_status("⚡", "C++", "GCC/Clang + clangd")],
            ignores=["build/", "bin/", "*.o", "*.a", "*.so", "compile_commands.json", ".cache/"],
        ),
        "go": Role(
            category="Systems",
            description="Go toolchain + gopls + delve",
            pkgs=[
                "go",
                "gopls",
                "gotools",
                "golangci-lint",
                "delve",
            ],
            hooks=[
                f"[ -f go.mod ] || go mod init {folder_name}",
                fmt_status("🐹", "Go", "Go toolchain + gopls"),
            ],
            ignores=["bin/", "dist/"],
        ),
        "zig": Role(
            category="Systems",
            description="Zig compiler + zls LSP",
            pkgs=[
                "zig",
                "zls",
            ],
            hooks=[
                fmt_status("⚡", "Zig", "Zig toolchain + zls"),
            ],
            ignores=["zig-cache/", "zig-out/"],
        ),
        "java": Role(
            category="Systems",
            description="OpenJDK 25 + jdtls + maven/gradle",
            pkgs=[
                "jdk25",
                "jdt-language-server",
                "google-java-format",
                "maven",
                "gradle",
            ],
            hooks=[
                'export JAVA_HOME="${pkgs.jdk25}/lib/openjdk"',
                fmt_status("☕", "Java", "JDK 25 + jdtls"),
            ],
            ignores=["target/", ".gradle/", "build/"],
        ),
        "dotnet": Role(
            category="Systems",
            description=".NET 9 SDK + Omnisharp",
            pkgs=[
                "dotnet-sdk_9",
                "omnisharp-roslyn",
            ],
            hooks=[
                'export DOTNET_ROOT="${pkgs.dotnet-sdk_9}"',
                fmt_status("🔷", ".NET", ".NET 9 SDK + Omnisharp"),
            ],
            ignores=["bin/", "obj/"],
        ),
        # ------------------------------------------------------------
        # Scripting, Data & Scientific
        # ------------------------------------------------------------
        "python": Role(
            category="Data & Scientific",
            description="Python 3.14 + uv + ruff + ty",
            pkgs=[
                "python314",
                "uv",
                "ruff",
                "ty",
            ],
            hooks=[
                "export UV_PYTHON_DOWNLOADS=never",
                "[ -f pyproject.toml ] && uv sync",
                (
                    "[ -f requirements.txt ] && [ ! -d .venv ] && "
                    "uv venv && uv pip install -r requirements.txt"
                ),
                "[ -d .venv ] && source .venv/bin/activate",
                fmt_status("🐍", "Python", "uv + ruff + ty"),
            ],
            ignores=["__pycache__/", "*.py[cod]", ".venv/", ".ruff_cache/", "dist/", "build/", "*.egg-info/"],
        ),
        "mathvis": Role(
            category="Data & Scientific",
            description="Python 3.14 + scientific computation stack",
            pkgs=[
                "python314",
                "uv",
                "ruff",
                "ty",
            ],
            hooks=[
                "export UV_PYTHON_DOWNLOADS=never",
                "[ -f pyproject.toml ] && uv sync",
                "[ -d .venv ] && source .venv/bin/activate",
                fmt_status("📐", "Mathvis", "πthon 3.14 + Scientific Stack"),
            ],
            ignores=["__pycache__/", "*.py[cod]", ".venv/", ".ruff_cache/", "dist/", "build/"],
        ),
        "julia": Role(
            category="Data & Scientific",
            description="Julia S&C + Formatter",
            pkgs=[
                '(julia-bin.withPackages [ "ControlSystems" "DifferentialEquations" "GLMakie" "CairoMakie" "LanguageServer" ])',
                "julia-formatter",
            ],
            hooks=[fmt_status("🔵", "Julia", "Julia S&C + Formatter")],
            ignores=[],
        ),
        # ------------------------------------------------------------
        # Web & Frontend Ecosystem
        # ------------------------------------------------------------
        "ts": Role(
            category="Web & Frontend",
            description="TypeScript/JS + Bun + vtsls + prettierd",
            pkgs=["bun", "vtsls", "typescript", "prettierd"],
            hooks=[fmt_status("🟦", "JS/TS", "Bun + vtsls + prettierd")],
            ignores=["node_modules/", "dist/"],
        ),
        "svelte": Role(
            category="Web & Frontend",
            description="Svelte 5 + Bun + svelte-ls",
            pkgs=[
                "bun",
                "nodePackages.svelte-language-server",
                "vtsls",
                "typescript",
                "prettierd",
            ],
            hooks=[
                "[ -f package.json ] || bun create svelte@latest .",
                fmt_status("🟧", "Svelte 5", "Bun + svelte-ls"),
            ],
            ignores=["node_modules/", ".svelte-kit/", "build/"],
        ),
        "vue": Role(
            category="Web & Frontend",
            description="Vue + Bun + vue-ls",
            pkgs=[
                "bun",
                "vue-language-server",
                "vtsls",
                "typescript",
                "prettierd",
            ],
            hooks=[
                "[ -f package.json ] || bun create vue@latest",
                fmt_status("🟢", "Vue", "Bun + vue-ls"),
            ],
            ignores=["node_modules/", "dist/"],
        ),
        "next": Role(
            category="Web & Frontend",
            description="Next.js + Bun + vtsls",
            pkgs=[
                "bun",
                "vtsls",
                "typescript",
                "prettierd",
            ],
            hooks=[
                "[ -f package.json ] || bun create next-app",
                fmt_status("⚛️ ", "Next.js", "Bun + vtsls"),
            ],
            ignores=["node_modules/", ".next/", "out/"],
        ),
        # ------------------------------------------------------------
        # Functional Ecosystem
        # ------------------------------------------------------------
        "gleam": Role(
            category="Functional",
            description="Gleam + Erlang runtime + rebar3",
            pkgs=["gleam", "erlang", "rebar3"],
            hooks=[
                fmt_status("🌸", "Gleam", "Gleam + Erlang runtime"),
            ],
            ignores=["build/"],
        ),
        "elixir": Role(
            category="Functional",
            description="Elixir + Mix + elixir-ls",
            pkgs=["elixir", "elixir-ls"],
            hooks=[
                fmt_status("💧", "Elixir", "Elixir + Mix + elixir-ls"),
            ],
            ignores=["_build/", "deps/"],
        ),
        "haskell": Role(
            category="Functional",
            description="GHC + Cabal + HLS + Ormolu",
            pkgs=[
                "ghc",
                "cabal-install",
                "haskell-language-server",
                "hlint",
                "ormolu",
            ],
            hooks=[
                fmt_status("λ ", "Haskell", "GHC + Cabal + HLS + Ormolu"),
            ],
            ignores=["dist-newstyle/", ".cabal-sandbox/"],
        ),
        # ------------------------------------------------------------
        # Document & Typesetting Workspaces
        # ------------------------------------------------------------
        "typst": Role(
            category="Typesetting",
            description="Typst + Tinymist LSP + typstyle",
            pkgs=[
                "typst",
                "tinymist",
                "typstyle",
            ],
            hooks=[
                'export TYPST_ROOT="$PWD"',
                fmt_status("📄", "Typst", "Tinymist LSP + typstyle"),
            ],
            ignores=[],
        ),
        "latex": Role(
            category="Typesetting",
            description="Tectonic + texlab + latexindent",
            pkgs=[
                "tectonic",
                "texlab",
                "texlivePackages.latexindent",
            ],
            hooks=[
                fmt_status("📜", "LaTeX", "Tectonic + texlab"),
            ],
            ignores=["*.aux", "*.log", "*.out", "*.toc", "*.synctex.gz", "*.fdb_latexmk", "*.fls"],
        ),
        "folio": Role(
            category="Typesetting",
            description="Typst/Pandoc Markdown Document Engine",
            pkgs=[
                "typst",
                "pandoc",
                "tinymist",
                "typstyle",
            ],
            hooks=[
                fmt_status("📝", "Folio", "Typst/Pandoc Markdown Engine"),
            ],
            ignores=[],
        ),
        # ------------------------------------------------------------
        # Cloud & Infrastructure
        # ------------------------------------------------------------
        "ops": Role(
            category="DevOps & Cloud",
            description="Docker Compose + Lazydocker + K8s tooling",
            pkgs=[
                "docker-compose",
                "lazydocker",
                "kubectl",
                "kubernetes-helm",
                "k9s",
                "dive",
            ],
            hooks=[
                fmt_status("🐳", "DevOps", "Docker + K8s tooling"),
            ],
            ignores=[],
        ),
    }


BUILTIN_ALIASES = {
    "py": "python",
    "rs": "rust",
    "react": "next",
    "js": "ts",
    "mv": "mathvis",
    "typ": "typst",
    "tex": "latex",
    "hs": "haskell",
    "cs": "dotnet",
    "csharp": "dotnet",
    "devops": "ops",
    "docker": "ops",
    "ex": "elixir",
}


def load_user_config() -> tuple[dict[str, Role], dict[str, str], list[Path]]:
    """Loads custom roles, aliases, and templates from ~/.config/flaker/roles.toml."""
    config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "flaker"
    roles_file = config_dir / "roles.toml"
    extra_roles: dict[str, Role] = {}
    extra_aliases: dict[str, str] = {}
    custom_asset_dirs: list[Path] = [config_dir / "templates"]

    if roles_file.exists():
        try:
            with open(roles_file, "rb") as f:
                data = tomllib.load(f)
            for role_key, role_data in data.get("roles", {}).items():
                extra_roles[role_key] = Role(
                    pkgs=role_data.get("pkgs", []),
                    hooks=role_data.get("hooks", []),
                    category=role_data.get("category", "Custom"),
                    description=role_data.get("description", "Custom user role"),
                    ignores=role_data.get("ignores", []),
                )
            for alias_key, target_role in data.get("aliases", {}).items():
                extra_aliases[alias_key] = target_role
        except Exception as e:
            print(f"Warning: Failed to parse user config at {roles_file}: {e}", file=sys.stderr)

    return extra_roles, extra_aliases, custom_asset_dirs


def resolve_nixpkgs_url(channel: str | None) -> str:
    """Translates a channel alias or full URL into a flake-compatible nixpkgs URL."""
    if not channel or channel in ("26.05", "nixos-26.05"):
        return "github:NixOS/nixpkgs/nixos-26.05"
    if channel in ("unstable", "nixpkgs-unstable"):
        return "github:NixOS/nixpkgs/nixpkgs-unstable"
    if channel == "nixos-unstable":
        return "github:NixOS/nixpkgs/nixos-unstable"
    if channel.startswith("github:") or channel.startswith("git+") or "/" in channel:
        return channel
    return f"github:NixOS/nixpkgs/nixos-{channel}"


def print_help():
    """Prints the CLI usage instructions."""
    print("""\
Usage: flaker <command> [roles...] [options]
       flaker [options]

Commands:
  init         Generate flake.nix, .envrc, .gitignore, and scaffold templates.
  env          Only generate flake.nix, .envrc, and .gitignore.
  scaffold     Only copy project templates to the current directory.
  list         List all available roles, categories, and aliases.
  info <role>  Display detailed information for a specific role.
  interactive  Launch interactive role and command selector.

Options:
  -f, --force          Overwrite existing files without confirmation prompts.
  -n, --dry-run        Preview generated files in stdout without writing.
  -c, --channel NAME   Nixpkgs channel (default: nixos-26.05, e.g. unstable, 24.11).
  --no-git             Do not automatically stage generated files with 'git add'.
  -h, --help           Show this help message and exit.
  -v, --version        Show version and exit.

Examples:
  flaker init py           # Setup Python flake, .envrc, .gitignore, and template
  flaker env rust next     # Setup flake for Rust & Next.js without scaffolding
  flaker scaffold folio    # Scaffold Folio files into current folder
  flaker init zig -c unstable --dry-run  # Preview Zig flake on unstable channel
  flaker list              # View all registered language roles & aliases
""")


def display_roles_list(roles_db: dict[str, Role], aliases: dict[str, str]) -> None:
    """Prints a formatted terminal table of all registered roles."""
    reverse_aliases: dict[str, list[str]] = {}
    for alias, target in aliases.items():
        reverse_aliases.setdefault(target, []).append(alias)

    print("\n\033[1;34m❄️  FLAKER ROLES REGISTRY\033[0m")
    print("=" * 96)
    print(f"{'ROLE':<12} {'ALIASES':<10} {'CATEGORY':<20} {'DESCRIPTION':<50}")
    print("-" * 96)

    # Group roles by category
    categories: dict[str, list[str]] = {}
    for r_key, role in roles_db.items():
        categories.setdefault(role.category, []).append(r_key)

    for cat in sorted(categories.keys()):
        for r_key in sorted(categories[cat]):
            role = roles_db[r_key]
            alias_str = ", ".join(reverse_aliases.get(r_key, []))
            print(f"\033[1m{r_key:<12}\033[0m {alias_str:<10} {role.category:<20} {role.description:<50}")

    print("=" * 96)
    print("Run '\033[1mflaker info <role>\033[0m' for packages, hooks, and starter files.\n")


def display_role_info(role_name: str, roles_db: dict[str, Role], aliases: dict[str, str], assets_dirs: list[Path]) -> None:
    """Displays detailed configuration and packages for a given role."""
    resolved_name = aliases.get(role_name, role_name)
    if resolved_name not in roles_db:
        print(f"Error: Unknown role '{role_name}'. Run 'flaker list' to see available roles.", file=sys.stderr)
        sys.exit(1)

    role = roles_db[resolved_name]
    rev_aliases = [a for a, t in aliases.items() if t == resolved_name]

    print(f"\n\033[1;34m❄️  Role Information: {resolved_name}\033[0m")
    print("=" * 72)
    print(f"  Category    : {role.category}")
    print(f"  Aliases     : {', '.join(rev_aliases) if rev_aliases else 'none'}")
    print(f"  Summary     : {role.description}")
    print("\n  Packages Included in DevShell:")
    for pkg in role.pkgs:
        print(f"    • {pkg}")

    print("\n  Shell Activation Hooks:")
    for hook in role.hooks:
        print(f"    • {hook}")

    # Inspect template files
    template_files: list[str] = []
    for adir in assets_dirs:
        rdir = adir / resolved_name
        if rdir.exists():
            for f in rdir.glob("**/*"):
                if f.is_file() and "__pycache__" not in f.parts and f.suffix not in (".pyc", ".pyo"):
                    template_files.append(str(f.relative_to(rdir)))

    print("\n  Starter Template Files:")
    if template_files:
        for tf in template_files:
            print(f"    📄 {tf}")
    else:
        print("    (No template files for this role; env-only)")

    if role.ignores:
        print("\n  Default .gitignore Rules:")
        for ign in role.ignores:
            print(f"    🚫 {ign}")

    print("=" * 72 + "\n")


def update_gitignore(
    project_root: Path,
    resolved_roles: list[str],
    roles_db: dict[str, Role],
    dry_run: bool = False,
) -> bool:
    """Creates or updates .gitignore with standard Nix/direnv and role-specific ignores."""
    gitignore_path = project_root / ".gitignore"
    existing_content = ""
    if gitignore_path.exists():
        existing_content = gitignore_path.read_text(encoding="utf-8")

    existing_lines = {line.strip() for line in existing_content.splitlines() if line.strip() and not line.strip().startswith("#")}

    new_sections: list[str] = []

    # Base Nix & Direnv rules
    base_rules = [".direnv/", "result", "result-*"]
    missing_base = [r for r in base_rules if r not in existing_lines]
    if missing_base:
        new_sections.append("# Nix & Direnv\n" + "\n".join(missing_base))

    # Role-specific rules
    for r in resolved_roles:
        if r in roles_db and roles_db[r].ignores:
            missing = [ign for ign in roles_db[r].ignores if ign not in existing_lines]
            if missing:
                new_sections.append(f"# {roles_db[r].category} ({r})\n" + "\n".join(missing))

    if not new_sections:
        return False

    append_text = "\n\n" + "\n\n".join(new_sections) + "\n"
    if dry_run:
        print(f"\n=== [DRY RUN] .gitignore additions ==={append_text}")
        return True

    final_content = (existing_content.rstrip() + append_text).lstrip()
    gitignore_path.write_text(final_content, encoding="utf-8")
    print(f"Success: Updated .gitignore at {project_root}")
    return True


def stage_git_files(project_root: Path, files: list[str]):
    """Automatically runs 'git add' on created files if inside a git repository."""
    if not (project_root / ".git").exists():
        return
    try:
        valid_files = [f for f in files if (project_root / f).exists()]
        if valid_files:
            subprocess.run(
                ["git", "add"] + valid_files,
                cwd=project_root,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"❄️  Auto-staged {', '.join(valid_files)} with git add")
    except Exception:
        pass


def prepare_flake_env(
    project_root: Path,
    resolved_roles: list[str],
    roles_db: dict[str, Role],
    template_path: Path,
    libs_list: str,
    nixpkgs_url: str,
    force: bool = False,
    dry_run: bool = False,
    auto_git: bool = True,
) -> bool:
    """Generates the flake.nix and .envrc at the project root."""
    flake_out = project_root / "flake.nix"
    envrc_out = project_root / ".envrc"

    if not force and not dry_run and flake_out.exists():
        if sys.stdin.isatty():
            try:
                ans = input(f"⚠️  flake.nix already exists at {project_root}. Overwrite? [y/N]: ").strip().lower()
                if ans not in ("y", "yes"):
                    print("Aborted: existing flake.nix was preserved.")
                    return False
            except (KeyboardInterrupt, EOFError):
                print("\nAborted.")
                return False
        else:
            print(f"Error: {flake_out} already exists. Pass --force to overwrite.", file=sys.stderr)
            sys.exit(1)

    selected_pkgs: list[str] = []
    selected_hooks: list[str] = []

    for role_key in resolved_roles:
        if role_key in roles_db:
            role = roles_db[role_key]
            selected_pkgs.extend(role.pkgs)
            selected_hooks.extend(role.hooks)
        else:
            selected_pkgs.append(role_key)

    has_rust = "rust" in resolved_roles

    rust_input = (
        '    rust-overlay.url = "github:oxalica/rust-overlay";\n'
        '    rust-overlay.inputs.nixpkgs.follows = "nixpkgs";'
        if has_rust
        else ""
    )
    rust_overlay = (
        "overlays = [ inputs.rust-overlay.overlays.default ];" if has_rust else ""
    )

    template_content = template_path.read_text(encoding="utf-8")

    rendered = (
        template_content.replace("__NIXPKGS_URL__", nixpkgs_url)
        .replace("/* __RUST_INPUT__ */", rust_input)
        .replace("/* __RUST_OVERLAY__ */", rust_overlay)
        .replace("__LIBS_LIST__", libs_list)
        .replace("__PKGS_LIST__", " ".join(selected_pkgs))
        .replace("__SHELL_HOOKS__", "\n          ".join(selected_hooks))
    )

    if dry_run:
        print(f"\n=== [DRY RUN] Generated flake.nix (Channel: {nixpkgs_url}) ===")
        print(rendered)
        print("=== [DRY RUN] Generated .envrc ===")
        print("use flake\n")
        update_gitignore(project_root, resolved_roles, roles_db, dry_run=True)
        return True

    flake_out.write_text(rendered, encoding="utf-8")

    if not envrc_out.exists():
        envrc_out.write_text("use flake\n", encoding="utf-8")

    update_gitignore(project_root, resolved_roles, roles_db, dry_run=False)

    # Run direnv allow inside the project root
    subprocess.run(["direnv", "allow"], cwd=project_root, check=False)
    print(f"Success: Generated flake.nix and .envrc at {project_root}")

    if auto_git:
        stage_git_files(project_root, ["flake.nix", ".envrc", ".gitignore"])

    return True


def scaffold_assets(
    target_dir: Path,
    project_name: str,
    resolved_roles: list[str],
    assets_dirs: list[Path],
    dry_run: bool = False,
):
    """Copies role templates into the target directory."""
    scaffolded_any = False

    for role_key in resolved_roles:
        found_in_dir = False
        for adir in assets_dirs:
            role_assets_dir = adir / role_key
            if not role_assets_dir.exists():
                continue

            found_in_dir = True
            for template_file in role_assets_dir.glob("**/*"):
                if template_file.is_file():
                    if "__pycache__" in template_file.parts or template_file.suffix in (".pyc", ".pyo"):
                        continue

                    relative_path = template_file.relative_to(role_assets_dir)
                    dest_path = target_dir / relative_path

                    if dry_run:
                        print(f"[DRY RUN] Would scaffold {relative_path} into {dest_path}")
                        scaffolded_any = True
                        continue

                    if not dest_path.exists():
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        content = template_file.read_text(encoding="utf-8")
                        content = content.replace("__PROJECT_NAME__", project_name)
                        dest_path.write_text(content, encoding="utf-8")
                        scaffolded_any = True

            if found_in_dir:
                break

    if scaffolded_any and not dry_run:
        print(f"Success: Scaffolded assets into {target_dir}")


def run_interactive_mode(roles_db: dict[str, Role], aliases: dict[str, str]) -> tuple[str, list[str]]:
    """Interactive role and command selector for TTY sessions."""
    print("\n\033[1;34m❄️  Flaker Interactive Stack Selector\033[0m")
    print("=" * 72)
    print("Select stack / roles by number (space or comma-separated, e.g. '1 8'):\n")

    sorted_roles = sorted(roles_db.keys())
    for idx, r in enumerate(sorted_roles, 1):
        role = roles_db[r]
        rev_a = [a for a, t in aliases.items() if t == r]
        alias_str = f"({rev_a[0]})" if rev_a else ""
        print(f"  [\033[1m{idx:>2}\033[0m] {r:<10} {alias_str:<8} \033[90m[{role.category}]\033[0m {role.description}")

    print("=" * 72)

    try:
        selection = input("\nSelection: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)

    if not selection:
        print("No roles selected. Exiting.")
        sys.exit(0)

    chosen_roles: list[str] = []
    tokens = selection.replace(",", " ").split()
    for tok in tokens:
        if tok.isdigit():
            i = int(tok)
            if 1 <= i <= len(sorted_roles):
                chosen_roles.append(sorted_roles[i - 1])
        else:
            tok_lower = tok.lower()
            resolved = aliases.get(tok_lower, tok_lower)
            if resolved in roles_db:
                chosen_roles.append(resolved)
            else:
                chosen_roles.append(tok_lower)

    if not chosen_roles:
        print("No valid roles recognized. Exiting.")
        sys.exit(1)

    print(f"\nChosen roles: \033[1m{', '.join(chosen_roles)}\033[0m")
    print("Command:")
    print("  [1] init     (flake.nix + .envrc + .gitignore + project starter templates)")
    print("  [2] env      (flake.nix + .envrc + .gitignore only)")
    print("  [3] scaffold (project starter templates only)")

    try:
        cmd_in = input("Choice [1]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)

    cmd_map = {"1": "init", "2": "env", "3": "scaffold", "init": "init", "env": "env", "scaffold": "scaffold"}
    chosen_cmd = cmd_map.get(cmd_in, "init")
    return chosen_cmd, chosen_roles


def main() -> None:
    # Basic flags
    if len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h", "help"):
        print_help()
        sys.exit(0)

    if len(sys.argv) == 2 and sys.argv[1] in ("--version", "-v", "version"):
        print("flaker 0.2.0")
        sys.exit(0)

    # Smart Paths & Asset Discovery
    pkg_root = Path(__file__).resolve().parent
    fallback_template = pkg_root / "flake.template"
    fallback_assets = pkg_root / "templates"
    default_runtime_libs = "stdenv.cc.cc.lib,zlib,glib,libxml2,openssl,libffi"

    template_path_env = os.environ.get("FLAKE_TEMPLATE")
    template_path = Path(template_path_env) if template_path_env else fallback_template

    assets_dir_env = os.environ.get("FLAKER_ASSETS")
    primary_assets_dir = Path(assets_dir_env) if assets_dir_env else fallback_assets

    libs_list = os.environ.get("LIBS_LIST", default_runtime_libs).replace(",", " ")

    # Load custom configuration from ~/.config/flaker/roles.toml
    user_roles, user_aliases, custom_asset_dirs = load_user_config()
    all_asset_dirs = custom_asset_dirs + [primary_assets_dir]

    current_dir = Path.cwd()
    project_root = find_project_root(current_dir)
    project_name = get_project_name(project_root)

    roles_db = build_builtin_role_registry(project_name)
    roles_db.update(user_roles)

    aliases = dict(BUILTIN_ALIASES)
    aliases.update(user_aliases)

    # Parse arguments
    args = sys.argv[1:]

    # Handle 'flaker list'
    if args and args[0] in ("list", "ls"):
        display_roles_list(roles_db, aliases)
        sys.exit(0)

    # Handle 'flaker info <role>'
    if args and args[0] in ("info", "show"):
        if len(args) < 2:
            print("Error: Missing role name for 'flaker info'. Example: flaker info python", file=sys.stderr)
            sys.exit(1)
        display_role_info(args[1], roles_db, aliases, all_asset_dirs)
        sys.exit(0)

    # Flags extraction
    force = False
    dry_run = False
    auto_git = True
    channel = None

    filtered_args: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-f", "--force"):
            force = True
        elif arg in ("-n", "--dry-run"):
            dry_run = True
        elif arg == "--no-git":
            auto_git = False
        elif arg in ("-c", "--channel"):
            if i + 1 < len(args):
                channel = args[i + 1]
                i += 1
            else:
                print("Error: --channel requires a channel name or url.", file=sys.stderr)
                sys.exit(1)
        elif arg.startswith("--channel="):
            channel = arg.split("=", 1)[1]
        elif arg in ("--help", "-h"):
            print_help()
            sys.exit(0)
        else:
            filtered_args.append(arg)
        i += 1

    # Interactive trigger if no arguments provided in a TTY
    command = ""
    raw_roles: list[str] = []

    if not filtered_args:
        if sys.stdin.isatty():
            command, raw_roles = run_interactive_mode(roles_db, aliases)
        else:
            print_help()
            sys.exit(1)
    elif filtered_args[0] == "interactive":
        command, raw_roles = run_interactive_mode(roles_db, aliases)
    else:
        command = filtered_args[0]
        raw_roles = filtered_args[1:]

        # If subcommand given without roles in a TTY (e.g. 'flaker init')
        if command in ("init", "env", "scaffold") and not raw_roles:
            if sys.stdin.isatty():
                _, raw_roles = run_interactive_mode(roles_db, aliases)
            else:
                print(f"Error: Missing roles for command '{command}'. Example: flaker {command} python", file=sys.stderr)
                sys.exit(1)

    # Enforce valid commands
    if command not in ("init", "env", "scaffold"):
        print(f"Error: Unknown command '{command}'.\n", file=sys.stderr)
        print_help()
        sys.exit(1)

    if not template_path.exists():
        print(f"Error: FLAKE_TEMPLATE path invalid or missing: {template_path}", file=sys.stderr)
        sys.exit(1)

    nixpkgs_url = resolve_nixpkgs_url(channel)
    resolved_roles = [aliases.get(r.lower(), r.lower()) for r in raw_roles]

    if command in ("init", "env"):
        success = prepare_flake_env(
            project_root=project_root,
            resolved_roles=resolved_roles,
            roles_db=roles_db,
            template_path=template_path,
            libs_list=libs_list,
            nixpkgs_url=nixpkgs_url,
            force=force,
            dry_run=dry_run,
            auto_git=auto_git,
        )
        if not success:
            sys.exit(0)

    if command in ("init", "scaffold"):
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dirs=all_asset_dirs,
            dry_run=dry_run,
        )


if __name__ == "__main__":
    main()
