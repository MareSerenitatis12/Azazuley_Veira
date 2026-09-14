# Azazuley Veira Internal Architecture

This document records the current internal application boundary. The live
`src/` tree remains authority if this prose ever drifts.

## Bodies and ownership

Azazuley Veira is a PySide6 terminal-shaped application with two bundled engine
bodies:

- `src/tardisha_grimchain/`
- `src/sydonic_magicae_translation_matrix/`

The UI transports exact values into those bodies and renders their returns.
It does not own TardiSHA mathematics or Sydonic lexical/grammar law.

There is no host-shell command route and no alternate engine discovery route.

## Startup

`START_AZAZULEY.py`:

1. points Python at the live `src/` tree;
2. disables Python bytecode writing;
3. removes stale `__pycache__`, `.pyc`, and `.pyo` state;
4. requires PySide6;
5. calls `azazuley_veira.app.run()`.

`app.run()` creates/reuses `QApplication`, loads the installed Azazuley and TardiSHA font offices,
applies the application font, constructs `MainWindow`, and enters the Qt event
loop.

## UI ownership

`src/azazuley_veira/ui/main_window.py` owns:

- GrimChain input;
- Domus Count;
- font selection;
- color controls;
- Import, Export, and Help controls;
- submission routing;
- responsive geometry.

`src/azazuley_veira/ui/terminal.py` owns:

- Et Sonyera;
- Domus House;
- Rabulalia;
- Ailalubar;
- Azalalia;
- Ailalaza;
- Glossolalia;
- Ailalossolg;
- `LeySyff | FfysYel`, backed by two independent exact surfaces;
- Definition;
- Canon Glossary, a static read-only presentation of `src/sydonic_magicae_translation_matrix/data/aksh/Dictionary.aksh`;
- engine-facing text formatting.

`MainWindow` also owns the rotating GrimChain journal/history controls, `.grim` import routing, and the PDF export menu. These are file/presentation concerns and do not duplicate TardiSHA or Sydonic execution.

The journal root is `~/.grimchain/azazuley/grimchains/`: one active `grimchains.bio` plus up to three gzip-compressed rolling `.bio` backups, rotating at 32 MiB. The history dropdown uses `GrimchainHistorySession` with a disposable temporary cache and a Qt lazy model that fetches 40 records at a time. The session keeps its read position while the popup is in use and does not reread already-consumed history. Selection closes the session and removes its temporary cache.

IMPORT parses `.grim` manifests directly. File entries with GrimChains are journaled under their stored manifest path; the trailing manifest GrimChain is journaled under the `.grim` filename. Import validates all extracted GrimChains before appending any of them and does not feed every imported body through the render transaction.

EXPORT is a `QMenu` on the existing Export button. It exports only populated surfaces from the current render transaction: Rabulalia, Ailalubar, Azalalia, Ailalaza, Glossolalia, Ailalossolg, paired LeySyff/FfysYel, Definition, or all populated transaction groups. It never sources historical output from `.bio`. PDF is rendered from the existing exact-surface HarfBuzz layout into `~/.grimchain/azazuley/exports/` using a user-chosen filename. Canon Glossary is excluded from the transaction menu.

A separate first-run/static export ensures `~/.grimchain/azazuley/exports/Canon Glossary.pdf` exists, generated from the already-formatted Canon Glossary exact surface rather than by treating `Dictionary.aksh` as an export document.

## GrimChain boundary

`src/azazuley_veira/engines/grimchain.py` directly imports bundled TardiSHA.

Source text uses TardiSHA's public `living_domus_for_source(...)` callable through
the Azazuley adapter. The preserved CLI adapter remains available for byte-equivalence
regression coverage.

Public-chain acceptance uses
`tardisha_grimchain.domus.parse_public_living_domus()`.

Azazuley does not split or recreate TardiSHA mathematics.

## Sydonic boundary

`src/azazuley_veira/engines/sydonic.py` constructs `SydonicMagicaeEngine` and
uses the public Ailalubar/Aeternum execution boundary for the live render transaction.
The transaction retains the resulting `TranslationResult`, semantic trace, resolved
words, structured Azalalia/Ailalaza/Definition presentation state, forward and mirrored pronunciation projections, and independent completed LeySyff/FfysYel Ostensive presentations. Legacy CLI helpers remain available for focused compatibility surfaces and tests.

## Sydonic runtime authority

Current engine construction calls `require_package_aksh_authority()` and builds
`LexicalResolver` from the package `data/aksh/` directory.

The enforced runtime tuple contains thirteen authorities: SeeD Body,
`Axiomyr…Shadow…Locus.aksh`, eight ordinary office files, Phantasmagoria,
`Living_Cadences.aksh`, and Enochian Understandings. Living Cadences carries
Regia, Breath, Cantillation, and Prosody; Enochian Understandings carries the
ten runtime Enochians. The Axiomyr/Shadow file is a live contextual special
authority in `AKSH_AUTHORITY_FILES`. Required field names are validated structurally. An explicitly present empty field body remains valid authored `""` data through lexical resolution, transaction construction, tracing, and presentation.

The colocated `data/aksh/Dictionary.aksh` file is a static Canon Glossary reference only. It is excluded from `AKSH_AUTHORITY_FILES`, lexical resolution, reconciliation versions, grammar, and render transactions.

Topology, source identity, authority, and authored laws are deterministic.
Phantasmagoria uses the standard `LexicalResolution` office path in Sydonic
execution. LeySyff and FfysYel are later presentation projections: each side
independently chooses one exact authored Ostensive I/II/III body for each emitted
Phantasmagoria occurrence without rerunning grammar or changing source identity.

The engine validates the complete public GrimChain with TardiSHA, lexes the
complete real Aeonic line, executes grammar in one sequential pass, builds the
semantic trace, and renders the spoken return.

SeeD is the ordinary lexical base. Ordinary office utterances accumulate on the
same lexical body in written order.

`ཪ` remains the Phantasmagoria transmutation operator.

`⚶` is the Ouroborose topology operator. Current source carries the real finite
utterance plus an alternating reflected/original mirror corridor mapped back to
the same finite source positions. Reflection changes bearing/traversal, not
source identity.


## Paired LeySyff | FfysYel scripture layout

`Terminal` keeps `leysyff_output` and `ffysyel_output` as two distinct `ExactFontTextEdit` widgets inside one `LeySyff | FfysYel` tab. They meet with zero layout spacing. LeySyff omits its right border and FfysYel supplies the single center edge, producing one visible seam without a divider widget or text character.

Both surfaces receive the same Terminal-owned scripture page height, page gap, margins, and responsive point size. They paginate their own newline-delimited paragraphs independently; a paragraph is atomic and moves intact to the next leaf when it does not fit. The larger content page count sets the shared physical document extent, while the shorter side remains blank on unused leaves. One visible vertical scrollbar drives both internal exact surfaces.

LeySyff is forced LTR and left aligned. FfysYel uses natural bidi and right alignment so the existing Hebrew paragraph prefix sits at the visual right edge. Activating the paired tab refreshes its geometry immediately, so page dimensions are derived from the visible current tab width rather than a stale hidden-widget size.

## Domus House presentation

`Terminal.set_mirror_utterance()` is presentation, not a second execution body.

The house is a four-field presentation of the real body: reversed first 12
glyphs, first 12 glyphs, last 12 glyphs, and reversed last 12 glyphs. No ellipsis
or Axiomyr-centered display window is part of the live law.

Each field uses exact mixed-face GrimChain routing and its geometry is measured
from the rendered glyph faces. Sydonic still receives the complete accepted
GrimChain.

## Font runtime

The source font payload mirrors two installed runtime offices: 76 fantasy/custom
fonts under `src/fonts/azazuley/` and 38 historical/shared fonts under
`src/fonts/tardisha/`. Runtime registration reads `/usr/local/share/fonts/azazuley`
and `/usr/local/share/fonts/tardisha` into the running Qt application.

The application default is Noto Sans.

GrimChain fields use exact physical faces from the installed TardiSHA font office.
Azalalia and Ailalaza render each authored lexical span from its exact .aksh font file.
The font selector changes only Et Sonyera and does not alter engine output.

Qt application-font registration makes the two installed offices available to
the current application process while preserving exact physical font ownership.

## Documentation rule

Current behavior follows the live source and the `.aksh` authority under `data/aksh/`.
