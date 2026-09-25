# Flaker ❄️⚡

> **Fast, Modular Nix Development Environments & Instant Project Scaffolding**

Flaker is an opinionated, lightning-fast CLI utility that automates single-file Nix shell creation (`flake.nix`), sets up seamless `.envrc` direnv hooks, generates language-aware `.gitignore` files, and scaffolds modern starter templates for over 20 languages, frameworks, and cloud ecosystems.

---

## ✨ Features

- ⚡ **Instant DevShells**: Generates reproducible, multi-platform `flake.nix` and `.envrc` configurations in milliseconds.
- 🗂️ **Zero-Config Scaffolding**: Provides turnkey starter templates across 20+ language ecosystems with modern project structures (`main.py`, `Cargo.toml`, `build.zig`, `CMakeLists.txt`, `pom.xml`, etc.).
- 🛡️ **Overwrite Protection (`-f / --force`)**: Protects existing configurations from accidental overwrites with confirmation prompts.
- 🌿 **Automatic Git Staging**: Detects Git repositories and automatically stages generated files (`git add flake.nix .envrc .gitignore`) so Nix Flakes recognize them immediately.
- 🚫 **Smart `.gitignore` Generation**: Appends standard Nix/direnv ignores (`.direnv/`, `result`) and role-specific cache/build directories (`.venv/`, `target/`, `node_modules/`, `zig-cache/`, `_build/`, etc.).
- 🌐 **Configurable Nixpkgs Channels (`-c / --channel`)**: Easily switch between `nixos-26.05`, `unstable`, `24.11`, or custom flake URIs on the fly.
- 🔍 **Discovery & Inspection (`list` & `info`)**: Browse all available roles, categories, and aliases, or inspect exact packages, LSPs, and shell hooks before scaffolding.
- 🧭 **Interactive Stack Selector (`interactive`)**: Run `flaker` with no arguments in any terminal for a clean interactive menu to choose stacks and commands.
- 🧩 **Extensible User Roles (`~/.config/flaker/roles.toml`)**: Define custom organization or project roles without modifying Flaker's code.
- 🔗 **Native Runtime Library Injection**: Automatically injects standard C runtime libraries (`stdenv.cc.cc.lib`, `zlib`, `glib`, `libxml2`, `openssl`, `libffi`) into `LD_LIBRARY_PATH`.
- 🦀 **Rust-Overlay Integration**: Seamlessly pulls and activates the `oxalica/rust-overlay` toolchain with `rust-analyzer` when Rust roles are selected.
- 🪶 **Pure & Ultra-Lightweight**: Zero external Python dependencies; 100% standard library core with sub-30ms startup.

---

## 🚀 Quick Start

Run Flaker directly via Nix without installing:

```bash
# Interactive mode (launches terminal stack selector)
nix run github:SpanishSyntax/Flaker

# Initialize a Python environment with uv, ruff, and ty LSP + project template
nix run github:SpanishSyntax/Flaker -- init python

# Initialize a Zig project with zls and build.zig
nix run github:SpanishSyntax/Flaker -- init zig

# Combine roles: Rust backend + Next.js frontend + DevOps containers
nix run github:SpanishSyntax/Flaker -- init rust next ops

# Target nixpkgs-unstable channel
nix run github:SpanishSyntax/Flaker -- init go -c unstable

# Dry-run preview without writing files
nix run github:SpanishSyntax/Flaker -- init rust --dry-run

# View all available roles and categories
nix run github:SpanishSyntax/Flaker -- list
```

---

## 💻 CLI Commands & Options

```text
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
```

---

## 🧰 Supported Roles & Ecosystems

| Ecosystem | Role | Aliases | Toolchain & LSP | Formatter / Linters |
| :--- | :--- | :--- | :--- | :--- |
| **Rust** | `rust` | `rs` | Oxalica Rust Stable + `rust-analyzer`, `lldb` | `cargo-fmt` |
| **Zig** | `zig` | - | Zig Compiler + `zls` (LSP) | Built-in `zig fmt` |
| **Python** | `python` | `py` | Python 3.14 + `uv`, `ty` | `ruff` (LSP + Formatter) |
| **Math & Visual** | `mathvis` | `mv` | Python 3.14 + `uv`, `ty` | `ruff` + Scientific Stack |
| **Go** | `go` | - | Go + `gopls`, `delve` | `goimports` (`gotools`), `golangci-lint` |
| **C** | `c` | - | GCC, GDB, CMake, Ninja, `clangd` | `clang-format` |
| **C++** | `cpp` | - | GCC, GDB, CMake, Ninja, `clangd` | `clang-format` |
| **Java** | `java` | - | OpenJDK 25, `jdtls`, Maven, Gradle | `google-java-format` |
| **.NET / C#** | `dotnet` | `cs`, `csharp` | .NET 9 SDK + Omnisharp | `dotnet format` |
| **Gleam** | `gleam` | - | Gleam + Erlang runtime + `rebar3` | `gleam format` |
| **Elixir** | `elixir` | `ex` | Elixir + Mix + `elixir-ls` | `mix format` |
| **Haskell** | `haskell` | `hs` | GHC + Cabal + `haskell-language-server` | `ormolu`, `hlint` |
| **Julia** | `julia` | - | Julia Bin (DifferentialEquations, Makie) | `julia-formatter` |
| **TypeScript / JS**| `ts` | `js` | Bun, `vtsls`, `typescript` | `prettierd` |
| **Svelte** | `svelte` | - | Bun, `svelte-language-server`, `vtsls` | `prettierd` |
| **Vue** | `vue` | - | Bun, `vue-language-server`, `vtsls` | `prettierd` |
| **Next.js** | `next` | `react` | Bun, `vtsls`, `typescript` | `prettierd` |
| **Typst** | `typst` | `typ` | `typst`, `tinymist` (LSP) | `typstyle` |
| **LaTeX** | `latex` | `tex` | `tectonic`, `texlab` (LSP) | `latexindent` |
| **Folio** | `folio` | - | `typst`, `pandoc`, `tinymist` | `typstyle` |
| **DevOps & Cloud** | `ops` | `devops`, `docker` | `docker-compose`, `lazydocker`, `kubectl`, `helm`, `k9s`, `dive` | - |

---

## 🧩 Custom User Roles (`~/.config/flaker/roles.toml`)

You can define your own project roles and aliases without modifying Flaker. Create `~/.config/flaker/roles.toml`:

```toml
[roles.ocaml]
category = "Functional"
description = "OCaml compiler + dune + utop + ocaml-lsp"
pkgs = ["ocaml", "dune_3", "ocamlPackages.utop", "ocamlPackages.ocaml-lsp"]
hooks = ["printf '🐫 OCaml environment active\\n'"]
ignores = ["_build/"]

[aliases]
ml = "ocaml"
```

Flaker will automatically merge your custom roles into `flaker list`, `flaker info`, and all scaffolding commands. You can also place custom starter templates inside `~/.config/flaker/templates/<role_name>/`.

---

## 🛠️ Home Manager Configuration

Add Flaker to your `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flaker = {
      url = "github:SpanishSyntax/Flaker";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flaker, ... }: {
    homeConfigurations.user = home-manager.lib.homeManagerConfiguration {
      modules = [
        flaker.homeManagerModules.default
        {
          programs.flaker.enable = true;
        }
      ];
    };
  };
}
```

Once enabled, `flaker` is directly accessible in your interactive shell.

---

## 📁 Repository Structure

```text
Flaker/
├── flake.nix               # Flake package & Home Manager module definition
├── pyproject.toml          # Standard PEP 517 / 621 Python project packaging
├── MANIFEST.in             # Manifest guaranteeing template asset bundling
├── LICENSE                 # MIT License
├── README.md               # Documentation & usage guide
└── flaker/
    ├── __init__.py         # Package metadata
    ├── __main__.py         # python -m flaker entrypoint
    ├── cli.py              # CLI core logic, role registry, TUI & git engine
    ├── flake.template      # Base devShell template
    └── templates/          # Starter project templates for 20+ ecosystems
        ├── c/
        ├── cpp/
        ├── dotnet/
        ├── elixir/
        ├── folio/
        ├── gleam/
        ├── go/
        ├── haskell/
        ├── java/
        ├── julia/
        ├── latex/
        ├── mathvis/
        ├── ops/
        ├── python/
        ├── rust/
        ├── ts/
        ├── typst/
        └── zig/
```

---

## 📜 License

MIT © SpanishSyntax
