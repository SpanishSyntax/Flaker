# Flaker ❄️⚡

> **Fast, Modular Nix Development Environments & Instant Project Scaffolding**

Flaker is an opinionated, lightning-fast CLI utility that automates single-file Nix shell creation (`flake.nix`), sets up seamless `.envrc` direnv hooks, and scaffolds modern starter templates for over a dozen languages, frameworks, and typesetting ecosystems.

---

## ✨ Features

- ⚡ **Instant DevShells**: Generates reproducible, multi-platform `flake.nix` and `.envrc` configurations in milliseconds.
- 🗂️ **Zero-Config Scaffolding**: Provides turnkey starter templates across 12+ language ecosystems with modern project structures (`main.py`, `Cargo.toml`, `CMakeLists.txt`, `pom.xml`, etc.).
- 🔗 **Native Runtime Library Injection**: Automatically injects standard C runtime libraries (`stdenv.cc.cc.lib`, `zlib`, `glib`, `libxml2`, `openssl`, `libffi`) into `LD_LIBRARY_PATH` to ensure foreign binaries, Python wheels, and native tools link effortlessly.
- 🦀 **Rust-Overlay Integration**: Seamlessly pulls and activates the `oxalica/rust-overlay` toolchain with `rust-analyzer` when Rust roles are selected.
- 🧠 **Smart Project Root Discovery**: Recursively traverses upwards to locate your existing `.git` or `flake.nix` root, ensuring root-level configurations stay at the root while allowing subfolder scaffolding.
- 🔄 **Direnv Auto-Hook**: Automatically emits `.envrc` and executes `direnv allow` for zero-friction shell loading upon directory entry.
- 🪶 **Pure & Ultra-Lightweight**: Zero external Python dependencies; 100% standard library core with sub-30ms startup.
- 🌐 **Universal Portability**: Run anywhere with zero installation using `nix run github:SpanishSyntax/Flaker`.

---

## 🚀 Quick Start

Run Flaker directly via Nix without installing:

```bash
# Initialize a Python environment with uv, ruff, and ty LSP + project template
nix run github:SpanishSyntax/Flaker -- init python

# Initialize a Rust project with oxalica overlay, rust-analyzer, and cargo
nix run github:SpanishSyntax/Flaker -- init rust

# Combine roles: Rust backend + Next.js web application
nix run github:SpanishSyntax/Flaker -- init rust next

# Generate only flake.nix and .envrc without scaffolding file templates
nix run github:SpanishSyntax/Flaker -- env go

# Only scaffold templates into the current folder
nix run github:SpanishSyntax/Flaker -- scaffold typst
```

---

## 💻 CLI Commands

```text
Usage: flaker <command> <role1> [role2] ...

Commands:
  init      Generate flake.nix, .envrc, and scaffold project templates.
  env       Only generate flake.nix and .envrc at the project root.
  scaffold  Only copy project templates to the current directory.
```

---

## 🧰 Supported Roles & Ecosystems

| Ecosystem | Role | Aliases | Toolchain & LSP | Formatter / Linters |
| :--- | :--- | :--- | :--- | :--- |
| **Rust** | `rust` | `rs` | Oxalica Rust Stable + `rust-analyzer`, `lldb` | `cargo-fmt` |
| **Python** | `python` | `py` | Python 3.14 + `uv`, `ty` | `ruff` (LSP + Formatter) |
| **Math & Visual** | `mathvis` | `mv` | Python 3.14 + `uv`, `ty` | `ruff` + Scientific Stack |
| **Go** | `go` | - | Go + `gopls`, `delve` | `goimports` (`gotools`), `golangci-lint` |
| **C** | `c` | - | GCC, GDB, CMake, Ninja, `clangd` | `clang-format` |
| **C++** | `cpp` | - | GCC, GDB, CMake, Ninja, `clangd` | `clang-format` |
| **Java** | `java` | - | OpenJDK 25, `jdtls`, Maven, Gradle | `google-java-format` |
| **Julia** | `julia` | - | Julia Bin (DifferentialEquations, Makie) | `julia-formatter` |
| **TypeScript / JS**| `ts` | `js` | Bun, `vtsls`, `typescript` | `prettierd` |
| **Svelte** | `svelte` | - | Bun, `svelte-language-server`, `vtsls` | `prettierd` |
| **Vue** | `vue` | - | Bun, `vue-language-server`, `vtsls` | `prettierd` |
| **Next.js** | `next` | `react` | Bun, `vtsls`, `typescript` | `prettierd` |
| **Typst** | `typst` | `typ` | `typst`, `tinymist` (LSP) | `typstyle` |
| **LaTeX** | `latex` | `tex` | `tectonic`, `texlab` (LSP) | `latexindent` |
| **Folio** | `folio` | - | `typst`, `pandoc`, `tinymist` | `typstyle` |

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
    ├── cli.py              # CLI core logic & role registry
    ├── flake.template      # Base devShell template
    └── templates/          # Starter project templates for 12+ ecosystems
        ├── c/
        ├── cpp/
        ├── folio/
        ├── go/
        ├── java/
        ├── julia/
        ├── latex/
        ├── mathvis/
        ├── python/
        ├── rust/
        ├── ts/
        └── typst/
```

---

## 📜 License

MIT © SpanishSyntax
