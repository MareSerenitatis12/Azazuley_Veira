# Azazuley Veira

Azazuley Veira is a terminal-shaped application for the bundled TardiSHA
GrimChain and Sydonic Magicae bodies. It is not a general operating-system
shell.

## Et Sonyera>

**Et Sonyera** means **the Song Within**.

Enter source text here and press Enter to send the exact text through bundled
TardiSHA GrimChain. If `Domus Count>` contains a value, that value is passed as
the explicit visible middle selection before `--string`.

The font selector sits on the Et Sonyera label row. It changes only Et Sonyera.
A selection changes the selected text; otherwise the chosen font becomes the
current format for typing from the cursor.

## GrimChain>

Paste an existing complete GrimChain here and press Enter.

Azazuley requires TardiSHA's current public Living Domus structure before the
body is accepted. This is structural recognition of the public GrimChain. It is
not source-file recomputation or manifest verification.

Malformed input is rejected before Sydonic rendering.

## Domus Count>

Enter the visible Domus Middle value passed to bundled GrimChain when Et Sonyera
creates a new body.

Submitting Domus Count while Et Sonyera contains text re-submits the current
song through GrimChain with that count.

## Domus House>

**Domus House** is the visible mirror presentation of the accepted GrimChain.

The house shows four exact 12-glyph fields from the accepted GrimChain:

- left reflection: reverse of the first 12 glyphs;
- upper center: the first 12 glyphs;
- lower center: the last 12 glyphs;
- right reflection: reverse of the last 12 glyphs.

The four fields use exact mixed-face GrimChain rendering and fit from the actual
rendered glyph metrics. They are presentation only. Rabulalia, Ailalubar, and Sydonic receive the complete
accepted GrimChain.

## Output tabs

**Rabulalia** is **the Cosmic Babble of Creation**. It displays the complete
accepted/generated GrimChain.

**Ailalubar** displays the exact visual mirror witness for the complete accepted
GrimChain, including source-position and exact font-routing authority.

### Prosody and Cantillation

**Prosody** is the underlying Unicode/code-point order and its source coordinates.
Mixed right-to-left and left-to-right writing systems can cause the natural visual
order presented on screen to differ from that stored order.

**Cantillation** is that deterministic natural visual character sequence presented
to the reader. Ailalubar performs exactly one textual reflection by reversing the
source string once. The resulting string is then rendered normally: every character
keeps its Unicode identity and exact physical font, and each font shapes normally
under HarfBuzz and its own writing-system rules. Natural bidirectional layout
determines where those unchanged characters appear.

Sydonic translates Cantillation: the same natural visual character sequence a human
encounters in Ailalubar. It does not substitute the hidden Prosody/code-point order
as translation order. The visual sequence retains an exact mapping back to the
original Prosody source coordinates so translation provenance remains auditable.

Fonts and glyphs are never artificially reversed, flipped, or replaced to manufacture
Cantillation. Ailalubar does not substitute mirrored Unicode counterparts or invent
per-font direction rules.

**Azalalia** is **the Language Damons speak**. It displays the forward authored
written-word projection, with the 𑁦 breath separator between resolved words.

**Ailalaza** displays the reverse projection of those same resolved authored words.
It does not perform a second translation.

**Glossolalia** displays the forward pronunciation projection from the resolved lexical bodies.

**Ailalossolg** displays the mirrored pronunciation projection from those same resolved lexical bodies.

**LeySyff | FfysYel** is one paired scripture tab containing two independent exact text surfaces. LeySyff is the forward Ostensive projection on the left. FfysYel is the mirrored Ostensive projection on the right. Each side independently selects complete authored Ostensive utterances, groups them into paragraphs of 1–6 complete utterances, and chooses one Hebrew paragraph-prefix character from the authored presentation pool. The two sides share physical scripture-page geometry and one vertical scrollbar but keep independent paragraph boundaries, page counts, prefixes, and text lengths.

LeySyff is forced left-to-right and left aligned. FfysYel uses natural bidirectional layout and right alignment so each Hebrew paragraph prefix appears at the visual beginning of its paragraph on the right. The two exact boxes touch directly and form one center seam; there is no inserted divider character in either text body.

An explicitly present empty `.aksh` field is valid authored data. Its runtime value remains the empty string and the corresponding presentation remains empty. Only structural absence of a required field name is an authority failure.

**Definition** displays the structured authored lexical definition view.

**Canon Glossary** is the static dictionary reference shown after Definition. It reads only `aksh/Dictionary.aksh`, which contains the canon glossary and glyph-dictionary material from `ALQC_GLOSSARY.md` and `DICTIONARY.md`, plus Regia, Breath, Cantillation, and Prosody. `DICTIONARY_OF_SYMBOLS.md` is not part of this tab. The glossary does not participate in GrimChain generation, Sydonic translation, or render transactions.

All engine output fields are read-only but remain selectable and copyable.

## Font selector

The first item is **System Default Font**. The remaining choices are families
available through Qt after the installed `/usr/local/share/fonts/azazuley` and
`/usr/local/share/fonts/tardisha` runtime offices have loaded.

Changing the selector changes only Et Sonyera. It does not change GrimChain,
Domus House, Rabulalia, Ailalubar, Azalalia, Ailalaza, Glossolalia, Ailalossolg,
`LeySyff | FfysYel`, Definition, Canon Glossary, labels, tabs, buttons, geometry, or engine meaning.

Engine-facing GrimChain glyph fields use the exact mapped TardiSHA physical font file.
Azalalia and Ailalaza apply each authored lexical span from its exact .aksh font file
and source authority.

## Colors

The COLORS menu changes the terminal background, font color, and outer body
background. These are presentation settings only.

## GrimChain History

The dropdown at the upper left shows retained GrimChains from the local journal, newest first. The journal lives under `~/.grimchain/azazuley/grimchains/` and consists of the active `grimchains.bio` plus up to three compressed rolling `.bio` backups. The active journal rotates at 32 MiB.

Opening the dropdown starts a temporary history-reading session. It loads 40 records at a time and fetches the next 40 as you continue scrolling. It keeps the current read state while the dropdown is in use instead of rereading the same journal data. Older compressed generations are opened only if scrolling reaches them. Selecting an entry places that exact GrimChain into `GrimChain>`; it does not translate or log the chain again merely because it was selected. The temporary history cache is then discarded, and the next open starts again with the newest records.

## Import

IMPORT accepts `.grim` manifest files. Each manifest entry that contains a GrimChain is validated and written to the local `.bio` journal using that entry's stored path as `User input`. Directory entries or other manifest records without a GrimChain do not create journal records. The standalone GrimChain at the end of the `.grim` belongs to the manifest itself and is journaled with the `.grim` filename as `User input`.

Because `.grim` files contain no journal timestamp, the timestamp stored in `.bio` is the time the import is logged. All GrimChains from the selected import are validated before any of them are appended. Importing a manifest does not render each imported chain through the translation viewer.

## Export

EXPORT is a dropdown for the current rendered Chain and translation only. It never exports from `.bio` history.

The menu provides per-view PDF export for Rabulalia, Ailalubar, Azalalia, Ailalaza, Glossolalia, Ailalossolg, `LeySyff | FfysYel`, and Definition, plus **Export All**. Empty views are unavailable. `LeySyff | FfysYel` exports as the paired rendered view. Export All includes only the populated views from the current transaction.

The default and supported application export format is PDF. The save dialog opens in `~/.grimchain/azazuley/exports/`; choose the filename and `.pdf` is added if omitted. The PDF is painted from the viewer's existing exact rendered layout, including the current exact font/glyph presentation.

Canon Glossary is not part of transaction export. Azazuley separately creates `~/.grimchain/azazuley/exports/Canon Glossary.pdf` from the formatted Canon Glossary viewer on first initialization if that PDF is not already present.

Read-only output fields remain selectable and copyable, so you can copy text into your own `.txt`, `.md`, `.odt`, or other document if desired. Those are manual copies rather than Azazuley export formats.

## Help

HELP opens this document inside the application.

Azazuley's authored terms remain unchanged by the English help surface.
