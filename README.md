# Azazuley Veira Language Terminal

Azazuley Veira is a standalone terminal-shaped application joining exactly two
engine bodies:

- TardiSHA / GrimChain
- Sydonic Magicae

It is not a host operating-system terminal and it does not execute arbitrary
shell commands.

## Interface language

- **Et Sonyera>** means **the Song Within**.
- **Domus House>** is **the House of the Domus, that which creates the uttering body**.
- **Rabulalia** is **the Cosmic Babble of Creation**.
- **Ailalubar** is the mirrored GrimChain presentation.
- **Azalalia** is **the Language Damons speak**.
- **Ailalaza** is Azalalia's mirrored written-word projection from the same resolved words.
- **Glossolalia** is the forward pronunciation projection from the resolved lexical bodies.
- **Ailalossolg** is the mirrored pronunciation projection from those same resolved lexical bodies.
- **LeySyff | FfysYel** is one paired scripture tab containing two independent exact surfaces: forward LeySyff on the left and mirrored FfysYel on the right. Both are built from complete authored Ostensive utterances, with independent 1–6 utterance paragraph grouping and independent Hebrew paragraph-prefix selection.
- **Definition** is the structured lexical definition view.
- **Canon Glossary** is a static read-only dictionary loaded from `src/sydonic_magicae_translation_matrix/data/aksh/Dictionary.aksh`. It combines the canon terms from `ALQC_GLOSSARY.md` with the glyph dictionary from `DICTIONARY.md` and includes Regia, Breath, Cantillation, and Prosody. It does not import `DICTIONARY_OF_SYMBOLS.md` and is not part of GrimChain/Sydonic execution.

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

## Runtime boundary

Azazuley does not recreate either engine.

`src/azazuley_veira/engines/grimchain.py` binds directly to the bundled
`src/tardisha_grimchain/` package.

`src/azazuley_veira/engines/sydonic.py` binds directly to the bundled
`src/sydonic_magicae_translation_matrix/` package.

There is no host-shell execution path, no PATH discovery, and no alternate
engine fallback.

TardiSHA remains authority for the public Living Domus / GrimChain structure.
Sydonic validates that same public body through TardiSHA before lexical and
grammatical realization.

## Current Sydonic authority

The active runtime authority is the `.aksh` body under:

`src/sydonic_magicae_translation_matrix/data/aksh/`

The current enforced runtime tuple uses thirteen authored authorities:

- `SeeD…Body.aksh`;
- `Axiomyr…Shadow…Locus.aksh`;
- eight ordinary office authorities;
- `ཪ…Phantasmagoria.aksh`;
- `Living_Cadences.aksh`;
- `Enochian…Understandings.aksh`.

`Living_Cadences.aksh` carries Regia, Breath, Cantillation, and Prosody as four authored cadences that remain present regardless of communication style. `Enochian…Understandings.aksh` carries the ten runtime Enochians.

`Axiomyr…Shadow…Locus.aksh` is part of live `AKSH_AUTHORITY_FILES` and provides
the two contextual Axiomyr/Shadow speaking bodies. Required `.aksh` field names are structural; an explicitly present empty field body is valid authored data and remains the empty string through resolution and presentation.

Topology, source identity, source authority, and authored grammar law remain
deterministic. Phantasmagoria resolves through the standard lexical office path.
The semantic execution may carry its selected I/II/III resolution through the
transaction trace, while the later LeySyff and FfysYel scripture presentations
independently choose one exact authored `ostensiveI`, `ostensiveII`, or
`ostensiveIII` for each emitted Phantasmagoria occurrence. Those presentation
choices do not rerun Sydonic grammar or rewrite the authored Ostensive body.

The thirteen files in `AKSH_AUTHORITY_FILES` remain the sole running lexical and office authority. `data/aksh/Dictionary.aksh` is colocated static reference material and is explicitly excluded from engine authority reconciliation.

## Current spoken path

For an Et Sonyera submission:

```text
Et Sonyera>
  -> GrimChain adapter
  -> bundled TardiSHA
  -> public GrimChain validation
  -> Domus House mirror display
  -> Rabulalia exact GrimChain
  -> Ailalubar exact visual/source/font witness
  -> bundled Sydonic
  -> Azalalia authored written-word projection
  -> Ailalaza mirrored written-word projection from the same resolved words
  -> Glossolalia forward pronunciation projection
  -> Ailalossolg mirrored pronunciation projection
  -> LeySyff | FfysYel paired scripture projection
  -> Definition
  -> Canon Glossary (static `aksh/Dictionary.aksh` reference)
```

For a pasted GrimChain, Azazuley first requires TardiSHA's current public Living
Domus structure, then enters the same render path.

## Domus House mirror display

`Domus House>` is active.

Domus House displays four exact 12-glyph presentation fields from the accepted
GrimChain:

- left reflection: reverse of the first 12 glyphs;
- upper center: the first 12 glyphs;
- lower center: the last 12 glyphs;
- right reflection: reverse of the last 12 glyphs.

All four fields use the exact mixed-face GrimChain renderer and size from the
metrics of the faces actually used by those glyphs. This house is presentation
only. Rabulalia, Ailalubar, and Sydonic receive the complete accepted GrimChain.

## Font authority

Azazuley uses two installed runtime font offices. Its private 76-font fantasy/custom body is
`/usr/local/share/fonts/azazuley`; the shared 38-font TardiSHA body is
`/usr/local/share/fonts/tardisha`. TardiSHA remains authoritative for its own
19 hardwired runtime faces.

At application startup, `font_runtime.py` registers both installed bodies with
the current Qt application using `QFontDatabase.addApplicationFont()`. Missing
or unreadable runtime fonts fail explicitly.

The application default is `Noto Sans`.

GrimChain fields use the exact faces in the TardiSHA font office. Authored
lexical spans use their exact `.aksh` family from the combined registered font
body. Application prose remains in the application/prose office.

The font selector changes only `Et Sonyera>`. It may use System Default Font or
any family available through Qt after the production font body is loaded.

## Source shape

```text
Azazuley_Veira_Language_Terminal/
├── LEYSYFF_FFYSYEL_SCRIPTURE_LAYOUT_PLAN.md
├── README.md
├── START_AZAZULEY.py
├── docs/
│   ├── HELP.md
│   ├── README.md
│   ├── finished_plans/
│   ├── dictionaries/
│   └── references/
├── installers/
│   └── linux/
├── src/
│   ├── azazuley_veira/
│   ├── fonts/
│   ├── sydonic_magicae_translation_matrix/
│   └── tardisha_grimchain/
└── tests/
```

The live bytes and current `.aksh` authority describe the active system.
