# Azazuley Veira Language Terminal

> **FONT STACK REQUIRED BEFORE INSTALLING AZAZULEY**
>
> Install the standalone font-stack installer for your operating system **before** installing or launching Azazuley Veira. Azazuley does not bundle the font stack inside the application installer.
>
> The required font stack provides the exact physical `azazuley` and `tardisha` font bodies used by Azazuley for authored fantasy faces, GrimChain coverage, exact HarfBuzz layout, and TardiSHA rendering. These are runtime authorities, not optional decoration. Without them Azazuley will refuse to treat the font authority as complete and exact rendering cannot be guaranteed.
>
> The font installer only creates the lowercase `azazuley` and `tardisha` font directories, copies the supplied fonts, and refreshes the host font registry/cache. It does not delete, replace, or modify unrelated system fonts.
>
> Use the matching standalone font installer first:
> - Linux/Ubuntu: `installers/linux_ubuntu/azazuley-font-stacks_1.0.0_all.deb`
> - Windows: `installers/windows/azazuley-font-stacks-1.0.0-windows.exe`
> - macOS: `installers/mac/azazuley-font-stacks-1.0.0-macos.pkg`

> Before the first word wakes,
> the house is already listening.
> Light waits behind the tongue.

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

> Names become doorways.
> Each door keeps its own weather;
> none borrows another sky.

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

> Gray stone around night,
> teal fire beneath the surface,
> many rooms, one breath.

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
- an Export menu for GrimChained Bio, the complete current translation PDF, and Canon Glossary PDF;
- Help;
- the `Domus House>` mirror display;
- Rabulalia, Ailalubar, Azalalia, Ailalaza, Glossolalia, Ailalossolg, `LeySyff | FfysYel`, Definition, and Canon Glossary output tabs.

`START_AZAZULEY.py` is the development launcher. It runs the live `src/` tree, suppresses Python bytecode writing, requires PySide6, then enters `azazuley_veira.app.run()`.

When Et Sonyera creates a GrimChain, the requested Domus Count is normally the final visible depth. In the rare case that the finite body contains only Enochian grammar and no Real speaking body, Sydonic asks TardiSHA for the next coordinate of that same witnessed GrimChain, one depth at a time, until a speaking body exists. The complete unfolded GrimChain becomes the visible body, the rendered body, and the journaled body. No opening glyphs are hidden, shifted, replaced, or translated from an unseen continuation.

Once a complete GrimChain already exists—whether typed directly, loaded from history, or brought back from a saved body—it enters the direct GrimChain path. It is not unfolded again merely because Enochian bearings appear near an edge; existing Aeternum law resolves those bearings through the complete finite body.

## GrimChain journal and history

> Footprints cross old snow.
> The path most recently walked
> rises to the front.

Accepted/generated GrimChains are journaled under `~/.grimchain/azazuley/grimchains/`.
The active `grimchains.bio` rotates at 32 MiB and retains up to three gzip-compressed rolling backups named `grimchains.1.bio`, `grimchains.2.bio`, and `grimchains.3.bio`. Backup files appear only after real rotations; empty placeholders are not created.

Each record stores the time it was logged, its user-input label, and the exact GrimChain. Direct GrimChain submissions use the typed GrimChain as the user-input value. Et Sonyera submissions use the original source text. Imported `.grim` manifests use each entry path as the user-input value, while the manifest trailing GrimChain is recorded under the `.grim` filename itself.

History is an ordered recent-history set keyed by the exact GrimChain body. A new chain is added once at the newest position. Reusing an existing exact chain does not create a duplicate record: its existing record is promoted to the newest position, its associated `User input` is preserved, and its recency timestamp is refreshed. Promotion searches both the active journal and rotated compressed generations. Legacy duplicates created by older append-only behavior are displayed once, newest-first, and are physically consolidated when that chain is used again.

The top-left GrimChain History control reads retained history without rerunning TardiSHA or Sydonic. Opening it starts a disposable lazy session that exposes 40 unique chains at a time, newest first. Further scrolling fetches the next 40 from the same session state. Rotated backup generations are copied/decompressed into temporary session storage only if scrolling reaches them. Selecting a history entry loads its exact GrimChain into the GrimChain input without translating it merely because it was selected. Submitting that loaded chain translates the complete stored body through the ordinary direct path and promotes that chain to the newest history position instead of adding another copy.

## Import and export

> A sealed book returns.
> One echo rests beneath it;
> two lanterns leave whole.

IMPORT accepts `.grim` manifest files. All contained GrimChains are structurally parsed and validated before any record from that import is written to the `.bio` journal. Entries without a GrimChain are ignored. Importing does not render every contained chain through the terminal. If an imported exact GrimChain already exists in history, it is promoted rather than duplicated.

EXPORT writes beneath `~/.grimchain/azazuley/exports/` and has three actions:

- **Export GrimChained Bio (.shk)** — exports the active, unarchived `grimchains.bio` without modifying the live journal, then appends exactly one final newline containing only the GrimChain of that `.bio` at the current user `Domus Count>`.
- **Export Words & Definitions (PDF)** — exports the complete current rendered translation body in this order: Rabulalia, Ailalubar, Azalalia, Ailalaza, Glossolalia, Ailalossolg, `LeySyff/FfysYel`, Definition.
- **Export Canon Glossary (PDF)** — exports Canon Glossary separately from the current translation PDF.

The translation PDF begins each section on a fresh PDF page. Each section is framed with the literal Azazuley binding glyph and its exact section name:

```text
⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟
Rabulalia
⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟

<VALUE>
```

The same framing is used for Ailalubar, Azalalia, Ailalaza, Glossolalia, Ailalossolg, `LeySyff/FfysYel`, Definition, and the separate Canon Glossary PDF. The exported values are painted from the existing exact rendered surfaces; the framing does not replace or rewrite their text.

Both PDFs are completed through TardiSHA's public PDF self-return using the current user `Domus Count>`—the same authority as `grimchain NUMBER --pdf-embed PDF`. The embedded GrimChain is verified as part of the PDF return. Read-only output fields remain selectable and copyable for users who want their own text documents; those manual copies are separate from Azazuley's export formats.

> The page leaves the chamber,
> carrying its own returning song.

## Copyright

Copyright (C), 2026. Ahnend, Magus. All Rights Reserved
witchofalways@gmail.com
---
Zenodo: https://zenodo.org/records/18942850
PhilPapers: https://philpeople.org/profiles/elliot-woff
SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6589998
DOI: https://doi.org/10.5281/zenodo.18942850
GitHub Working Code: https://github.com/MareSerenitatis12
Youtube Podcast https://www.youtube.com/@theimpossibleboy13
