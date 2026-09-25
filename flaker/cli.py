import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Role:
    pkgs: list[str]
    hooks: list[str]


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


def build_role_registry(folder_name: str) -> dict[str, Role]:
    return {
        # ------------------------------------------------------------
        # Systems & Compiled Languages
        # ------------------------------------------------------------
        "rust": Role(
            pkgs=[
                '(rust-bin.stable.latest.default.override { extensions = [ "rust-analyzer" ]; })',
                "cargo-expand",
                "lldb",
            ],
            hooks=[
                f"[ -f Cargo.toml ] || cargo init --name {folder_name}",
                fmt_status("🦀", "Rust", "stable toolchain + rust-analyzer"),
            ],
        ),
        "c": Role(
            pkgs=[
                "gcc",
                "gdb",
                "cmake",
                "pkg-config",
                "gnumake",
                "ninja",
                "clang-tools",  # clangd (LSP) + clang-format (Conform)
            ],
            hooks=[fmt_status("⚡", "C", "GCC/Clang + clangd")],
        ),
        "cpp": Role(
            pkgs=[
                "gcc",
                "gdb",
                "cmake",
                "pkg-config",
                "gnumake",
                "ninja",
                "clang-tools",  # clangd (LSP) + clang-format (Conform)
            ],
            hooks=[fmt_status("⚡", "C++", "GCC/Clang + clangd")],
        ),
        "go": Role(
            pkgs=[
                "go",
                "gopls",  # LSP
                "gotools",  # goimports (Conform)
                "golangci-lint",  # Linter
                "delve",  # Debugger
            ],
            hooks=[
                f"[ -f go.mod ] || go mod init {folder_name}",
                fmt_status("🐹", "Go", "Go toolchain + gopls"),
            ],
        ),
        "java": Role(
            pkgs=[
                "jdk25",
                "jdt-language-server",  # LSP
                "google-java-format",  # Formatter (Conform)
                "maven",
                "gradle",
            ],
            hooks=[
                'export JAVA_HOME="${pkgs.jdk25}/lib/openjdk"',
                fmt_status("☕", "Java", "JDK 25 + jdtls"),
            ],
        ),
        # ------------------------------------------------------------
        # Scripting, Data & Scientific
        # ------------------------------------------------------------
        "python": Role(
            pkgs=[
                "python314",
                "uv",
                "ruff",  # LSP, linter & ruff_format (Conform)
                "ty",  # Static type checker LSP
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
        ),
        "mathvis": Role(
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
        ),
        "julia": Role(
            pkgs=[
                '(julia-bin.withPackages [ "ControlSystems" "DifferentialEquations" "GLMakie" "CairoMakie" "LanguageServer" ])',
                "julia-formatter",
            ],
            hooks=[fmt_status("🔵", "Julia", "Julia S&C + Formatter")],
        ),
        # ------------------------------------------------------------
        # Web & Frontend Ecosystem
        # ------------------------------------------------------------
        "ts": Role(
            pkgs=["bun", "vtsls", "typescript", "prettierd"],
            hooks=[fmt_status("🟦", "JS/TS", "Bun + vtsls + prettierd")],
        ),
        "svelte": Role(
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
        ),
        "vue": Role(
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
        ),
        "next": Role(
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
        ),
        # ------------------------------------------------------------
        # Document & Typesetting Workspaces
        # ------------------------------------------------------------
        "typst": Role(
            pkgs=[
                "typst",
                "tinymist",  # LSP
                "typstyle",  # Formatter (Conform)
            ],
            hooks=[
                'export TYPST_ROOT="$PWD"',
                fmt_status("📄", "Typst", "Tinymist LSP + typstyle"),
            ],
        ),
        "latex": Role(
            pkgs=[
                "tectonic",  # Fast rust-based LaTeX engine
                "texlab",  # LSP
                "texlivePackages.latexindent",  # Formatter (Conform)
            ],
            hooks=[
                fmt_status("📜", "LaTeX", "Tectonic + texlab"),
            ],
        ),
        "folio": Role(
            pkgs=[
                "typst",
                "pandoc",
                "tinymist",  # LSP
                "typstyle",
            ],
            hooks=[
                fmt_status("📝", "Folio", "Typst/Pandoc Markdown Engine"),
            ],
        ),
    }


ALIASES = {
    "py": "python",
    "rs": "rust",
    "react": "next",
    "js": "ts",
    "mv": "mathvis",
    "typ": "typst",
    "tex": "latex",
}


def print_help():
    """Prints the CLI usage instructions."""
    print("""\
Usage: flaker <command> <role1> [role2] ...

Commands:
  init      Generate flake.nix, .envrc, and scaffold project templates.
  env       Only generate flake.nix and .envrc at the project root.
  scaffold  Only copy project templates to the current directory.

Available Roles:
  Systems:  rust (rs), c, cpp, go, java
  Data:     python (py), mathvis (mv), julia
  Web:      ts (js), svelte, vue, next (react)
  Docs:     typst (typ), latex (tex), folio

Examples:
  flaker init py           # Setup Python flake + template
  flaker env rust next     # Setup flake for Rust & Next.js
  flaker scaffold folio    # Scaffold Folio files here
""")


def prepare_flake_env(
    project_root: Path,
    resolved_roles: list[str],
    roles_db: dict[str, Role],
    template_path: Path,
    libs_list: str,
):
    """Generates the flake.nix and .envrc at the project root."""
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
        template_content.replace("/* __RUST_INPUT__ */", rust_input)
        .replace("/* __RUST_OVERLAY__ */", rust_overlay)
        .replace("__LIBS_LIST__", libs_list)
        .replace("__PKGS_LIST__", " ".join(selected_pkgs))
        .replace("__SHELL_HOOKS__", "\n          ".join(selected_hooks))
    )

    flake_out = project_root / "flake.nix"
    flake_out.write_text(rendered, encoding="utf-8")

    envrc = project_root / ".envrc"
    if not envrc.exists():
        envrc.write_text("use flake\n")

    # Run direnv allow inside the project root
    subprocess.run(["direnv", "allow"], cwd=project_root, check=False)
    print(f"Success: Generated flake.nix and .envrc at {project_root}")


def scaffold_assets(
    target_dir: Path,
    project_name: str,
    resolved_roles: list[str],
    assets_dir: Path,
):
    """Copies role templates into the target directory (can be a subfolder)."""
    scaffolded_any = False

    for role_key in resolved_roles:
        role_assets_dir = assets_dir / role_key
        if not role_assets_dir.exists():
            continue

        # Walk through sibling files in the template directory
        for template_file in role_assets_dir.glob("**/*"):
            if template_file.is_file():
                if "__pycache__" in template_file.parts or template_file.suffix in (".pyc", ".pyo"):
                    continue

                # Recreate file structure relative to target_dir
                relative_path = template_file.relative_to(role_assets_dir)
                dest_path = target_dir / relative_path

                if not dest_path.exists():
                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                    # Read, interpolate potential project names, and write out cleanly
                    content = template_file.read_text(encoding="utf-8")
                    content = content.replace("__PROJECT_NAME__", project_name)
                    dest_path.write_text(content, encoding="utf-8")
                    scaffolded_any = True

    if scaffolded_any:
        print(f"Success: Scaffolded assets into {target_dir}")


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h", "help"):
        print_help()
        sys.exit(0)

    if len(sys.argv) == 2 and sys.argv[1] in ("--version", "-v", "version"):
        print("flaker 0.1.0")
        sys.exit(0)

    # Require at least flaker, command, and one role
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    raw_roles = sys.argv[2:]

    # Enforce subcommands
    if command not in ("init", "env", "scaffold"):
        print(f"Error: Unknown command '{command}'.\n", file=sys.stderr)
        print_help()
        sys.exit(1)

    pkg_root = Path(__file__).resolve().parent
    fallback_template = pkg_root / "flake.template"
    fallback_assets = pkg_root / "templates"
    default_runtime_libs = "stdenv.cc.cc.lib,zlib,glib,libxml2,openssl,libffi"

    template_path_env = os.environ.get("FLAKE_TEMPLATE")
    template_path = Path(template_path_env) if template_path_env else fallback_template

    assets_dir_env = os.environ.get("FLAKER_ASSETS")
    assets_dir = Path(assets_dir_env) if assets_dir_env else fallback_assets

    libs_list = os.environ.get("LIBS_LIST", default_runtime_libs).replace(",", " ")

    if not template_path.exists():
        print(f"Error: FLAKE_TEMPLATE path invalid or missing: {template_path}", file=sys.stderr)
        sys.exit(1)

    if not assets_dir.exists():
        print(f"Error: FLAKER_ASSETS path invalid or missing: {assets_dir}", file=sys.stderr)
        sys.exit(1)

    # Smart Paths
    current_dir = Path.cwd()
    project_root = find_project_root(current_dir)
    project_name = get_project_name(project_root)

    roles_db = build_role_registry(project_name)
    resolved_roles = [ALIASES.get(r, r) for r in raw_roles]

    if command in ("init", "env"):
        prepare_flake_env(
            project_root=project_root,
            resolved_roles=resolved_roles,
            roles_db=roles_db,
            template_path=template_path,
            libs_list=libs_list,
        )

    if command in ("init", "scaffold"):
        scaffold_assets(
            target_dir=current_dir,
            project_name=project_name,
            resolved_roles=resolved_roles,
            assets_dir=assets_dir,
        )


if __name__ == "__main__":
    main()
