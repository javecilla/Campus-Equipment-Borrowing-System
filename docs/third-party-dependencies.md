# Third-party dependency inventory

The [README disclosure](../README.md#third-party-packages-and-assets) owns why selected packages/assets are used. This inventory records every locked Python/npm entry, including indirect and optional packages, with license metadata and the dependency introducing it. Source locks remain authoritative; refresh this inventory with dependency changes.

License identifiers come from installed Python distribution metadata/license files and npm lockfile metadata. They do not replace upstream license/NOTICE files. Original team MIT terms do not relabel third-party material.

## Python runtime and development packages

Pins: [requirements.txt](../requirements.txt) and [requirements-dev.txt](../requirements-dev.txt). Runtime means present in the runtime lock; formatter support packages are development-only. Native libraries shipped inside binary wheels retain their supplied notices.

| Package | Version | Role | Introduced by | Declared license |
| --- | --- | --- | --- | --- |
| `asgiref` | 3.12.1 | Runtime | `requirements.txt`, `django` | BSD-3-Clause |
| `click` | 8.5.0 | Development | `djlint` | BSD-3-Clause |
| `cssbeautifier` | 2.0.3 | Development | `djlint` | MIT |
| `django` | 5.2.18 | Runtime | `requirements.txt` | BSD-3-Clause |
| `djlint` | 1.46.6 | Development | `requirements-dev.in` | GPL-3.0-or-later |
| `editorconfig` | 0.17.1 | Development | `cssbeautifier`, `jsbeautifier` | PSF-2.0 |
| `jsbeautifier` | 2.0.3 | Development | `cssbeautifier`, `djlint` | MIT |
| `json5` | 0.17.3 | Development | `djlint` | Apache-2.0 |
| `pathspec` | 1.1.1 | Development | `djlint` | MPL-2.0 |
| `psycopg` | 3.3.6 | Runtime | `requirements.txt` | LGPL-3.0-only |
| `psycopg-binary` | 3.3.6 | Runtime | `requirements.txt` | LGPL-3.0-only |
| `python-dotenv` | 1.2.4 | Runtime | `requirements.txt` | BSD-3-Clause |
| `pyyaml` | 6.0.3 | Development | `djlint` | MIT |
| `regex` | 2026.9.29 | Development | `djlint` | Apache-2.0 AND CNRI-Python |
| `ruff` | 0.17.1 | Development | `requirements-dev.in` | MIT |
| `sqlparse` | 0.6.0 | Runtime | `requirements.txt`, `django` | BSD-3-Clause |
| `tzdata` | 2026.5 | Runtime | `requirements.txt`, `django`, `psycopg` | Apache-2.0 |

## npm runtime, build, and optional packages

Every package entry in [package-lock.json](../package-lock.json) is listed below, including native binaries for other platforms. Optional entries may not be installed locally. All current npm packages support build/development tooling; page JavaScript bundles no third-party runtime package. Build/dev tools do not implement application HTTP endpoints or generate administration pages.

| Lockfile package path | Version | Role | Introduced by | Declared license |
| --- | --- | --- | --- | --- |
| `node_modules/@esbuild/aix-ppc64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/android-arm` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/android-arm64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/android-x64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/darwin-arm64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/darwin-x64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/freebsd-arm64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/freebsd-x64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/linux-arm` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/linux-arm64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/linux-ia32` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/linux-loong64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/linux-mips64el` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/linux-ppc64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/linux-riscv64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/linux-s390x` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/linux-x64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/netbsd-arm64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/netbsd-x64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/openbsd-arm64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/openbsd-x64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/openharmony-arm64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/sunos-x64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/win32-arm64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/win32-ia32` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@esbuild/win32-x64` | 0.28.2 | Build/dev; optional | `esbuild` | MIT |
| `node_modules/@jridgewell/gen-mapping` | 0.3.13 | Build/dev | `@jridgewell/remapping` | MIT |
| `node_modules/@jridgewell/remapping` | 2.3.5 | Build/dev | `@tailwindcss/node` | MIT |
| `node_modules/@jridgewell/resolve-uri` | 3.1.2 | Build/dev | `@jridgewell/trace-mapping` | MIT |
| `node_modules/@jridgewell/sourcemap-codec` | 1.6.0 | Build/dev | `@jridgewell/gen-mapping`, `@jridgewell/trace-mapping`, `magic-string` | MIT |
| `node_modules/@jridgewell/trace-mapping` | 0.3.31 | Build/dev | `@jridgewell/gen-mapping`, `@jridgewell/remapping` | MIT |
| `node_modules/@parcel/watcher` | 2.6.0 | Build/dev | `@tailwindcss/cli` | MIT |
| `node_modules/@parcel/watcher-android-arm64` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-darwin-arm64` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-darwin-x64` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-freebsd-x64` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-linux-arm-glibc` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-linux-arm-musl` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-linux-arm64-glibc` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-linux-arm64-musl` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-linux-x64-glibc` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-linux-x64-musl` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-win32-arm64` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@parcel/watcher-win32-x64` | 2.6.0 | Build/dev; optional | `@parcel/watcher` | MIT |
| `node_modules/@tailwindcss/cli` | 4.3.0 | Build/dev | `package.json (devDependencies)` | MIT |
| `node_modules/@tailwindcss/node` | 4.3.0 | Build/dev | `@tailwindcss/cli` | MIT |
| `node_modules/@tailwindcss/oxide` | 4.3.0 | Build/dev | `@tailwindcss/cli` | MIT |
| `node_modules/@tailwindcss/oxide-android-arm64` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-darwin-arm64` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-darwin-x64` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-freebsd-x64` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-linux-arm-gnueabihf` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-linux-arm64-gnu` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-linux-arm64-musl` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-linux-x64-gnu` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-linux-x64-musl` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-wasm32-wasi` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-wasm32-wasi/node_modules/@emnapi/core` | 1.10.0 | Build/dev; optional | `@tailwindcss/oxide-wasm32-wasi` | MIT |
| `node_modules/@tailwindcss/oxide-wasm32-wasi/node_modules/@emnapi/runtime` | 1.10.0 | Build/dev; optional | `@tailwindcss/oxide-wasm32-wasi` | MIT |
| `node_modules/@tailwindcss/oxide-wasm32-wasi/node_modules/@emnapi/wasi-threads` | 1.2.1 | Build/dev; optional | `@emnapi/core`, `@tailwindcss/oxide-wasm32-wasi` | MIT |
| `node_modules/@tailwindcss/oxide-wasm32-wasi/node_modules/@napi-rs/wasm-runtime` | 1.1.4 | Build/dev; optional | `@tailwindcss/oxide-wasm32-wasi` | MIT |
| `node_modules/@tailwindcss/oxide-wasm32-wasi/node_modules/@tybys/wasm-util` | 0.10.1 | Build/dev; optional | `@napi-rs/wasm-runtime`, `@tailwindcss/oxide-wasm32-wasi` | MIT |
| `node_modules/@tailwindcss/oxide-wasm32-wasi/node_modules/tslib` | 2.8.1 | Build/dev; optional | `@emnapi/core`, `@emnapi/runtime`, `@emnapi/wasi-threads`, `@tailwindcss/oxide-wasm32-wasi`, `@tybys/wasm-util` | 0BSD |
| `node_modules/@tailwindcss/oxide-win32-arm64-msvc` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/@tailwindcss/oxide-win32-x64-msvc` | 4.3.0 | Build/dev; optional | `@tailwindcss/oxide` | MIT |
| `node_modules/ansi-regex` | 6.4.0 | Build/dev | `strip-ansi` | MIT |
| `node_modules/ansi-styles` | 6.2.3 | Build/dev | `wrap-ansi` | MIT |
| `node_modules/chalk` | 5.6.2 | Build/dev | `concurrently` | MIT |
| `node_modules/cliui` | 9.0.1 | Build/dev | `yargs` | ISC |
| `node_modules/concurrently` | 10.0.6 | Build/dev | `package.json (devDependencies)` | MIT |
| `node_modules/detect-libc` | 2.1.2 | Build/dev | `@parcel/watcher`, `lightningcss` | Apache-2.0 |
| `node_modules/emoji-regex` | 10.6.0 | Build/dev | `string-width` | MIT |
| `node_modules/enhanced-resolve` | 5.26.0 | Build/dev | `@tailwindcss/cli`, `@tailwindcss/node` | MIT |
| `node_modules/esbuild` | 0.28.2 | Build/dev | `package.json (devDependencies)` | MIT |
| `node_modules/escalade` | 3.2.0 | Build/dev | `yargs` | MIT |
| `node_modules/get-caller-file` | 2.0.5 | Build/dev | `yargs` | ISC |
| `node_modules/get-east-asian-width` | 1.7.0 | Build/dev | `string-width` | MIT |
| `node_modules/graceful-fs` | 4.2.11 | Build/dev | `enhanced-resolve` | ISC |
| `node_modules/is-extglob` | 2.1.1 | Build/dev | `is-glob` | MIT |
| `node_modules/is-glob` | 4.0.3 | Build/dev | `@parcel/watcher` | MIT |
| `node_modules/jiti` | 2.7.0 | Build/dev | `@tailwindcss/node` | MIT |
| `node_modules/lightningcss` | 1.32.0 | Build/dev | `@tailwindcss/node` | MPL-2.0 |
| `node_modules/lightningcss-android-arm64` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-darwin-arm64` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-darwin-x64` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-freebsd-x64` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-linux-arm-gnueabihf` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-linux-arm64-gnu` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-linux-arm64-musl` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-linux-x64-gnu` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-linux-x64-musl` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-win32-arm64-msvc` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/lightningcss-win32-x64-msvc` | 1.32.0 | Build/dev; optional | `lightningcss` | MPL-2.0 |
| `node_modules/magic-string` | 0.30.21 | Build/dev | `@tailwindcss/node` | MIT |
| `node_modules/mri` | 1.2.0 | Build/dev | `@tailwindcss/cli` | MIT |
| `node_modules/node-addon-api` | 7.1.1 | Build/dev | `@parcel/watcher` | MIT |
| `node_modules/picocolors` | 1.1.1 | Build/dev | `@tailwindcss/cli` | ISC |
| `node_modules/picomatch` | 4.0.7 | Build/dev | `@parcel/watcher` | MIT |
| `node_modules/prettier` | 3.9.10 | Build/dev | `package.json (devDependencies)` | MIT |
| `node_modules/rxjs` | 7.8.2 | Build/dev | `concurrently` | Apache-2.0 |
| `node_modules/shell-quote` | 1.12.0 | Build/dev | `concurrently` | MIT |
| `node_modules/source-map-js` | 1.2.2 | Build/dev | `@tailwindcss/node` | BSD-3-Clause |
| `node_modules/string-width` | 7.2.0 | Build/dev | `cliui`, `wrap-ansi`, `yargs` | MIT |
| `node_modules/strip-ansi` | 7.2.0 | Build/dev | `cliui`, `string-width`, `wrap-ansi` | MIT |
| `node_modules/supports-color` | 10.2.2 | Build/dev | `concurrently` | MIT |
| `node_modules/tailwindcss` | 4.3.0 | Build/dev | `@tailwindcss/cli`, `@tailwindcss/node`, `package.json (devDependencies)` | MIT |
| `node_modules/tapable` | 2.3.3 | Build/dev | `enhanced-resolve` | MIT |
| `node_modules/tree-kill` | 1.2.2 | Build/dev | `concurrently` | MIT |
| `node_modules/tslib` | 2.8.1 | Build/dev | `rxjs` | 0BSD |
| `node_modules/wrap-ansi` | 9.0.2 | Build/dev | `cliui` | MIT |
| `node_modules/y18n` | 5.0.8 | Build/dev | `yargs` | ISC |
| `node_modules/yargs` | 18.0.0 | Build/dev | `concurrently` | MIT |
| `node_modules/yargs-parser` | 22.0.0 | Build/dev | `yargs` | ISC |

All declared dependency and optional-dependency references in this application lock resolve to listed entries, including the optional WASM backend's nested dependencies.

## Supplied assets and optional inspection tooling

| Asset / tool | Declaration / notice | Scope |
| --- | --- | --- |
| DM Sans | [Supplied OFL notice](../static/fonts/DM_Sans/OFL.txt) | Local typography; supplied static/variable font files |
| Poppins | [Supplied OFL notice](../static/fonts/Poppins/OFL.txt) | Local typography; supplied weights/styles |
| Default role avatars | [Admin image](../static/images/default-profile-admin.png), [basic-user image](../static/images/default-profile-user.png); supplied by the user, original source/license not provided | Local account-menu/profile artwork; no claim of team authorship or MIT coverage of third-party artwork |
| @bytebase/dbhub 1.5.0 | MIT; [versioned npm metadata](https://registry.npmjs.org/@bytebase%2Fdbhub/1.5.0) and [upstream repository](https://github.com/bytebase/dbhub) | Optional read-only MCP tool in npm execution cache, outside application locks |

DBHub's published 1.5.0 manifest declares zod ^4.2.0, ssh2 ^1.16.0, dotenv ^16.4.7, express ^4.18.2, ssh-config ^5.0.3, @iarna/toml ^2.2.5, @modelcontextprotocol/node ^2.0.0, and @modelcontextprotocol/server ^2.0.0. Its execution-cache resolution is separate from package-lock.json; this document does not invent resolved versions or a complete lock for that optional tool. Use its linked published dependency/license declarations and DEV.md's pinned launch. It is not bundled with the application.

Node/npm, Python/pip, Git, PostgreSQL, and the optional uv resolver are workstation tools described in DEV.md, not application package entries. Current page JavaScript contains no bundled third-party runtime package. Original font notices stay in static/fonts/.

## Inventory coverage

This snapshot contains 17 pinned Python distributions and 113 npm lock entries. Refresh names, versions, licenses, parent links, optional flags, and counts from actual locks/installed metadata after a dependency change. Check that direct selections have a README rationale and required browser notices remain in the built artifact.
