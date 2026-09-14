# Azazuley Veira Language Terminal

> **FONT STACK REQUIRED BEFORE INSTALLING AZAZULEY**
>
> Install the standalone font-stack installer for your operating system **before** installing or launching Azazuley Veira. Azazuley does not bundle the font stack inside the application installer.
>
> The required font stack provides the exact physical `azazuley` and `tardisha` font bodies used by Azazuley for authored fantasy faces, GrimChain coverage, exact HarfBuzz layout, and TardiSHA rendering. These are runtime authorities, not optional decoration. Without them Azazuley will refuse to treat the font authority as complete and exact rendering cannot be guaranteed.
>
> The font installer only creates the lowercase `azazuley` and `tardisha` font directories, copies the supplied fonts, and refreshes the host font registry/cache. It does not delete, replace, or modify unrelated system fonts.

> Use the matching standalone font installer first:
> - Linux/Ubuntu: `installers/linux_ubuntu/azazuley-font-stacks_1.0.0_all.deb`
> - Windows: `installers/windows/azazuley-font-stacks-1.0.0-windows.exe`
> - macOS: `installers/mac/azazuley-font-stacks-1.0.0-macos.pkg`
>
## Invocation

> Et Sonyera, open the inward song.
> Let the Domus gather what can be uttered.
> Let Rabulalia arrive before meaning has learned to stand still.
> Let Ailalubar answer from the other face of the same breath.
> Let Azalalia speak where the ordinary tongue gives way.
> Let Ailalaza return the word through its shadow.
> Let Glossolalia carry the mouth beyond the page,
> and Ailalossolg bring the echo home altered but unbroken.
> Between LeySyff and FfysYel, let the scripture keep both lamps burning.

Azazuley Veira joins TardiSHA / GrimChain and Sydonic Magicae inside a terminal-shaped instrument for utterance, reflection, scripture, and return. It is meant to be entered, listened to, and discovered in motion.

## Interface language

Azazuley uses its own names throughout the interface:

- `Et Sonyera>`
- `Domus House>`
- Rabulalia
- Ailalubar
- Azalalia
- Ailalaza
- Glossolalia
- Ailalossolg
- `LeySyff | FfysYel`
- Definition
- Canon Glossary

The interface is intended to be encountered through use rather than explained in advance.

## Current application body

The live application is under `src/azazuley_veira/` and uses PySide6 / Qt.

The visible body contains:

- a worn gray outer body;
- a dark terminal field;
- teal terminal text and glow;
- an editable `Et Sonyera>` source field;
- an independent `GrimChain>` input field;
- a `Domus Count>` field;
- a font selector attached only to `Et Sonyera>`;
- color controls;
- a lazy GrimChain history dropdown backed by the rotating `.bio` journal;
- `.grim` Import;
- a per-tab / Export All PDF menu for the currently rendered transaction;
- Help;
- the `Domus House>` mirror display;
- Rabulalia, Ailalubar, Azalalia, Ailalaza, Glossolalia, Ailalossolg, `LeySyff | FfysYel`, Definition, and Canon Glossary output tabs.

`START_AZAZULEY.py` is the development launcher. It runs the live `src/` tree,
suppresses Python bytecode writing,
requires PySide6, then enters `azazuley_veira.app.run()`.

## GrimChain journal and history

Accepted/generated GrimChains are journaled under `~/.grimchain/azazuley/grimchains/`.
The active `grimchains.bio` rotates at 32 MiB and retains up to three gzip-compressed rolling backups named `grimchains.1.bio`, `grimchains.2.bio`, and `grimchains.3.bio`. Backup files appear only after real rotations; empty placeholders are not created.

Each record stores the time it was logged, its user-input label, and the exact GrimChain. Direct GrimChain submissions use the typed GrimChain as the user-input value. Et Sonyera submissions use the original source text. Imported `.grim` manifests use each entry path as the user-input value, while the manifest trailing GrimChain is recorded under the `.grim` filename itself.

The top-left GrimChain History control reads this retained journal without rerunning TardiSHA or Sydonic. Opening it starts a disposable lazy session that exposes 40 records at a time, newest first. Further scrolling fetches the next 40 from the same session state. Rotated backup generations are copied/decompressed into temporary session storage only if scrolling reaches them. Selecting a history entry loads its GrimChain into the GrimChain input without rendering or logging it again; the temporary session is then discarded.

## Import and export

IMPORT accepts `.grim` manifest files. All contained GrimChains are structurally parsed and validated before any record from that import is appended to the `.bio` journal. Entries without a GrimChain are ignored. Importing does not render every contained chain through the terminal.

User-triggered EXPORT is a dropdown for the currently rendered transaction only. Available actions are Rabulalia, Ailalubar, Azalalia, Ailalaza, Glossolalia, Ailalossolg, the paired `LeySyff | FfysYel` view, Definition, and Export All. Empty transaction surfaces cannot be exported. Export never reads historical bodies from `.bio`.

PDF is the standard export format. The save dialog starts in `~/.grimchain/azazuley/exports/`, the user chooses the filename, and `.pdf` is added when omitted. `LeySyff | FfysYel` exports as one paired rendered view. Export All writes the populated current transaction views into one PDF. Users may also select/copy text from read-only viewer surfaces into their own `.txt`, `.md`, `.odt`, or other documents; those formats are user-created copies rather than Azazuley export formats.

Canon Glossary is deliberately separate from transaction export. On first application initialization, `~/.grimchain/azazuley/exports/Canon Glossary.pdf` is created from the formatted Canon Glossary render surface if it does not already exist. This static PDF is not produced from `.bio` and is not an Export-menu transaction item.
