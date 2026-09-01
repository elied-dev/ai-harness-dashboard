# Application foundation for browser, desktop, and terminal interfaces

## Question

Which minimal cross-platform foundation can share the catalog, discovery, parsing, configuration, and search core across a browser UI, desktop UI, and interactive TUI on macOS, Windows, and Linux while retaining local filesystem and editor/file-manager integration?

## Recommendation

Use a **Go core**, the Go standard library for the local browser server, **Wails v2** for the desktop shell, and **Bubble Tea** for the interactive TUI.

This is the smallest foundation among the credible options because it keeps filesystem access, discovery, parsing, indexing, configuration, and actions in one native-language core while adding only thin interface adapters:

- **Browser:** serve one compiled web frontend and a local API from a loopback-only Go HTTP server. Go's `embed` package can place the frontend assets in the executable, and `net/http` already provides the server and file-serving primitives.[^go-embed][^go-http]
- **Desktop:** package the same frontend build with Wails. Wails wraps Go and a web frontend into one binary, generates TypeScript definitions for exposed Go methods, uses native system rendering engines, and provides native menus and dialogs.[^wails-readme] Its supported targets explicitly include Windows, macOS, and Linux.[^wails-install]
- **Terminal:** call the core in-process from a Bubble Tea program. Bubble Tea is a Go framework for stateful full-window terminal applications based on the Elm architecture.[^bubble-tea]

Do **not** make HTTP the internal core boundary. Define an in-process application service API. The browser transport adapts it to loopback HTTP; Wails bindings adapt it to the desktop frontend; the TUI calls it directly. This keeps domain behavior independent of all three delivery mechanisms and avoids running a local server when only the desktop or TUI is active.

## Proposed boundary

| Layer | Responsibility | Dependency direction |
| --- | --- | --- |
| Catalog core | Assets, placements, adapters, discovery, parsing, indexing, search, configuration, read-only source actions | No GUI, HTTP, Wails, or TUI dependencies |
| Application service | Use cases and interface-neutral result/error types | Depends only on the catalog core |
| Browser adapter | Loopback HTTP API and embedded frontend assets | Depends on the application service |
| Desktop adapter | Wails lifecycle, bindings, dialogs, and OS integration | Depends on the application service |
| TUI adapter | Bubble Tea model, update loop, key handling, and rendering | Depends on the application service |
| Platform launch adapter | Reveal path and launch configured editor without shell interpolation | Implements a narrow core port per OS |

The browser and desktop builds can reuse the same frontend screens while using a small transport interface: HTTP in a normal browser and generated Wails bindings in the desktop shell. Wails explicitly supports calling Go methods from JavaScript and generating TypeScript definitions.[^wails-readme] Its runtime also exposes desktop facilities such as windows, menus, dialogs, browser launching, and clipboard access.[^wails-runtime]

## Why this is the minimal fit

### One core and toolchain for privileged behavior

Go supplies the filesystem/process primitives and HTTP server in its standard library. Static frontend files can be compiled into an `embed.FS`, and `net/http.FileServerFS` can serve an `fs.FS`.[^go-embed][^go-http] Editor and file-manager launchers can use `os/exec` directly rather than introducing a command-runner dependency; `os/exec` intentionally invokes commands without a system shell.[^go-exec]

The same core can therefore be linked into the browser server, Wails desktop executable, and TUI executable. Only the web frontend requires the usual JavaScript build step; Wails already expects a frontend build and bundles the generated assets during its build process.[^wails-build]

### Native desktop without bundling a browser engine

Wails uses the operating system's rendering engine rather than embedding a browser.[^wails-readme] Its installation documentation lists Windows 10/11, macOS, and Linux targets and identifies their native prerequisites, including WebView2 on Windows and WebKitGTK on Linux.[^wails-install] This keeps the desktop shell narrower than Electron while preserving native menus, dialogs, and platform integration.

The cost is a release matrix: desktop builds depend on platform webviews and toolchains. CI must build and smoke-test Windows, macOS, and Linux artifacts separately; packaging and signing remain a later decision rather than being hidden inside the foundation choice.

### A real interactive TUI without a second domain implementation

Bubble Tea supports inline and full-window terminal applications and supplies a state/update/view model suitable for search, lists, details, and keyboard navigation.[^bubble-tea] The TUI should own only interaction state. Catalog state and operations remain in the shared application service.

## Alternatives considered

| Foundation | Strengths | Why it is not the default |
| --- | --- | --- |
| **Rust + Tauri + Ratatui + an HTTP crate** | Tauri uses native webviews, has a privileged Rust core process, central IPC, and a least-privilege model; Ratatui is a flexible Rust TUI crate.[^tauri-start][^tauri-process][^ratatui] | Strong option when memory safety, footprint, or a Rust ecosystem requirement dominates. For this catalog it adds Rust ownership/async and JavaScript-to-Rust integration complexity without removing the web build or three interface adapters. |
| **TypeScript/Node + Electron + Ink** | One language and React-style components across browser, desktop, and terminal. Ink deliberately brings React's component model to CLI applications.[^ink] | Electron embeds Chromium and Node.js and introduces main/renderer/preload processes and IPC.[^electron-intro][^electron-process] That is more runtime and security-boundary machinery than a local read-only catalog needs. React component reuse also does not eliminate the different GUI and terminal interaction models. |
| **Browser server plus TUI, no desktop shell** | Fewest dependencies and easiest distribution. | Does not meet the explicit desktop-application requirement or provide native window, menu, dialog, and packaging behavior. |
| **Independent implementations per interface** | Each interface can use its preferred stack. | Duplicates discovery, parsing, identity, search, and policy behavior—the exact duplication the shared-core requirement rules out. |

## Constraints and risks

1. **The browser endpoint is a trust boundary.** It must bind only to loopback, use a per-launch unguessable capability or equivalent request authentication, validate origins, and shut down with its owning process. The exact policy needs its own decision; “local” alone does not make an HTTP endpoint private.
2. **Wails v2 brings native prerequisites.** Its documentation requires platform-specific webview/toolchain dependencies and Node/NPM for frontend builds.[^wails-install] The release process must prove all three operating systems.
3. **Frontend reuse needs a transport seam.** Browser code cannot call Wails-generated bindings. A small client interface must hide HTTP versus Wails transport without leaking either into screen components.
4. **OS actions remain platform-specific.** Reveal-in-file-manager and editor launch behavior differ by OS. Keep those commands behind a narrow adapter, pass arguments without shell concatenation, and define failure behavior before implementation.
5. **Do not select a large frontend framework here.** The graphical prototype should establish the interaction and accessibility needs first. Wails accepts any web frontend, so this foundation does not require that decision now.[^wails-readme]
6. **Do not add a database by default.** Startup/on-demand scans can begin with an in-memory catalog. Persistence should be introduced only if measured startup or search behavior requires it.

## Decision enabled by this research

Choose **Go + standard-library loopback server + Wails v2 + Bubble Tea**, organized around an in-process application service. Reuse one compiled web frontend between browser and desktop, with separate HTTP and Wails transport adapters. Build and smoke-test native desktop artifacts on each target OS.

## Surfaced decision questions

- What authentication, origin validation, port selection, and lifecycle rules define the local browser API trust boundary?
- Which frontend technology best satisfies the graphical prototype's accessibility and interaction needs without unnecessary runtime weight?
- How will Windows, macOS, and Linux artifacts be packaged, signed/notarized where applicable, updated, and smoke-tested?
- What is the exact behavior and configuration precedence for “open in editor” and “reveal in file manager” on each OS?

## Primary sources

[^go-embed]: Go project, [`embed` package documentation](https://pkg.go.dev/embed).
[^go-http]: Go project, [`net/http` package documentation](https://pkg.go.dev/net/http), including `FileServerFS`.
[^go-exec]: Go project, [`os/exec` package documentation](https://pkg.go.dev/os/exec).
[^wails-readme]: Wails project, [official repository README](https://github.com/wailsapp/wails/blob/master/README.md).
[^wails-install]: Wails project, [Installation and supported platforms](https://wails.io/docs/gettingstarted/installation/).
[^wails-build]: Wails project, [CLI build documentation](https://wails.io/docs/reference/cli/) and [manual build process](https://wails.io/docs/guides/manual-builds/).
[^wails-runtime]: Wails project, [Runtime introduction](https://wails.io/docs/reference/runtime/intro/).
[^bubble-tea]: Charmbracelet, [Bubble Tea official repository README](https://github.com/charmbracelet/bubbletea/blob/main/README.md).
[^tauri-start]: Tauri project, [What is Tauri?](https://v2.tauri.app/start/).
[^tauri-process]: Tauri project, [Process model](https://v2.tauri.app/concept/process-model/).
[^ratatui]: Ratatui project, [official repository README](https://github.com/ratatui/ratatui/blob/main/README.md).
[^electron-intro]: Electron project, [Introduction](https://www.electronjs.org/docs/latest/).
[^electron-process]: Electron project, [Process model](https://www.electronjs.org/docs/latest/tutorial/process-model).
[^ink]: Ink project, [official repository README](https://github.com/vadimdemedes/ink/blob/master/readme.md).
