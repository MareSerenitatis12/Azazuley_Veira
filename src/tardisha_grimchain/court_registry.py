"""court_registry.py — ADDITIVE Living Domus construction (plan v12 §11.5, §3).

The complete 144-Court body C = G x G. Court C_i,j has address 12i+j, a single
Court glyph kappa(C_i,j), a name element, and governing/hyperbolic indices.
Courts are DERIVED from an ordered Goetic pair, never sampled or randomized.
Data validated against the plan table: 144 unique addresses, 144 unique single
code-point glyphs, every glyph == its U+ scalar, every address == 12i+j.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .canon import GLYPH_BODY, law


GOETIC_NAME: Final[dict[str, str]] = {
    '⏣': 'Fetu',
    '⬡': 'Kal',
    '✡': 'Babdh',
    '⚝': 'Ahn',
    '❂': 'Vel',
    'ꙮ': 'Sor',
    '❈': 'Koth',
    '⧗': 'Dreh',
    '⊛': 'Rhea',
    '❄': 'Zhek',
    '⚛': 'Shav',
    '⌬': 'Trig',
}


@dataclass(frozen=True, slots=True)
class CourtRecord:
    address: int
    i: int
    j: int
    glyph: str
    name_element: str
    codepoint: int

    def __post_init__(self) -> None:
        if isinstance(self.address, bool) or not isinstance(self.address, int):
            raise TypeError("Court address must be an integer")
        if isinstance(self.i, bool) or not isinstance(self.i, int):
            raise TypeError("Court governing index i must be an integer")
        if isinstance(self.j, bool) or not isinstance(self.j, int):
            raise TypeError("Court alternating index j must be an integer")
        if not 0 <= self.i < 12 or not 0 <= self.j < 12:
            raise ValueError("Court indices i and j must each be in [0,11]")
        if self.address != 12 * self.i + self.j:
            raise ValueError("Court address must equal 12*i+j")
        if not isinstance(self.glyph, str) or len(self.glyph) != 1:
            raise TypeError("Court glyph must be exactly one Unicode code point")
        if isinstance(self.codepoint, bool) or not isinstance(self.codepoint, int):
            raise TypeError("Court codepoint must be an integer")
        if ord(self.glyph) != self.codepoint:
            raise ValueError("Court glyph and codepoint do not agree")
        if not isinstance(self.name_element, str) or not self.name_element:
            raise TypeError("Court name element must be a non-empty string")

        supplied = (
            self.address, self.i, self.j, self.glyph,
            self.name_element, self.codepoint,
        )
        if supplied != _COURT_ROWS[self.address]:
            raise ValueError("CourtRecord contradicts the sealed 144-Court registry")



_COURT_ROWS: Final[tuple[tuple[int, int, int, str, str, int], ...]] = (
    (  0,  0,  0, 'އ', 'Ahl', 0x787),
    (  1,  0,  1, 'ށ', 'Suhn', 0x781),
    (  2,  0,  2, 'ނ', 'Nerh', 0x782),
    (  3,  0,  3, 'ރ', 'Rish', 0x783),
    (  4,  0,  4, 'ޱ', 'Borha', 0x7B1),
    (  5,  0,  5, 'ޅ', 'Lhahm', 0x785),
    (  6,  0,  6, 'ކ', 'Keth', 0x786),
    (  7,  0,  7, 'ވ', 'Vehm', 0x788),
    (  8,  0,  8, 'މ', 'Mahd', 0x789),
    (  9,  0,  9, 'ފ', 'Furh', 0x78A),
    ( 10,  0, 10, 'ދ', 'Drah', 0x78B),
    ( 11,  0, 11, 'ތ', 'Thera', 0x78C),
    ( 12,  1,  0, 'ᛁ', 'Kura', 0x16C1),
    ( 13,  1,  1, 'ᛂ', 'Lur', 0x16C2),
    ( 14,  1,  2, '⌑', 'Thar', 0x2311),
    ( 15,  1,  3, 'ᛄ', 'Rin', 0x16C4),
    ( 16,  1,  4, 'ᛇ', 'Nar', 0x16C7),
    ( 17,  1,  5, 'ᛉ', 'Fel', 0x16C9),
    ( 18,  1,  6, 'ᛊ', 'Har', 0x16CA),
    ( 19,  1,  7, 'ᛋ', 'Mer', 0x16CB),
    ( 20,  1,  8, 'ᛌ', 'Lor', 0x16CC),
    ( 21,  1,  9, 'ᛍ', 'Per', 0x16CD),
    ( 22,  1, 10, 'ᛎ', 'Zhil', 0x16CE),
    ( 23,  1, 11, 'ᛏ', 'Clar', 0x16CF),
    ( 24,  2,  0, 'ᚠ', 'Hir', 0x16A0),
    ( 25,  2,  1, 'ᚢ', 'Kor', 0x16A2),
    ( 26,  2,  2, 'ᚦ', 'Var', 0x16A6),
    ( 27,  2,  3, 'ᚨ', 'Pyr', 0x16A8),
    ( 28,  2,  4, 'ᚱ', 'Sor', 0x16B1),
    ( 29,  2,  5, 'ᚲ', 'Alc', 0x16B2),
    ( 30,  2,  6, 'ᚷ', 'Nur', 0x16B7),
    ( 31,  2,  7, 'ᚹ', 'Sat', 0x16B9),
    ( 32,  2,  8, 'ᚺ', 'Oro', 0x16BA),
    ( 33,  2,  9, 'ᚾ', 'Bon', 0x16BE),
    ( 34,  2, 10, 'ᚿ', 'Tir', 0x16BF),
    ( 35,  2, 11, 'ᛃ', 'Far', 0x16C3),
    ( 36,  3,  0, '≾', 'Abdh', 0x227E),
    ( 37,  3,  1, '᭨', 'Nym', 0x1B68),
    ( 38,  3,  2, '᭡', 'Loh', 0x1B61),
    ( 39,  3,  3, '⛧', 'Xir', 0x26E7),
    ( 40,  3,  4, '𝀖', 'Ohl', 0x1D016),
    ( 41,  3,  5, '༺', 'Pir', 0xF3A),
    ( 42,  3,  6, '᭢', 'Roeh', 0x1B62),
    ( 43,  3,  7, '⦾', 'Sen', 0x29BE),
    ( 44,  3,  8, '⦽', 'Uth', 0x29BD),
    ( 45,  3,  9, '𝀵', 'Fae', 0x1D035),
    ( 46,  3, 10, '𝀟', 'Kha', 0x1D01F),
    ( 47,  3, 11, '༻', 'Psei', 0xF3B),
    ( 48,  4,  0, 'ⴰ', 'Vera', 0x2D30),
    ( 49,  4,  1, 'ⴱ', 'Tar', 0x2D31),
    ( 50,  4,  2, 'ⴳ', 'Ghem', 0x2D33),
    ( 51,  4,  3, 'ⴷ', 'Drel', 0x2D37),
    ( 52,  4,  4, 'ⴼ', 'Ful', 0x2D3C),
    ( 53,  4,  5, 'ⴽ', 'Ker', 0x2D3D),
    ( 54,  4,  6, 'ⵀ', 'Hohm', 0x2D40),
    ( 55,  4,  7, 'ⵃ', 'Hrah', 0x2D43),
    ( 56,  4,  8, 'ⵄ', 'Ara', 0x2D44),
    ( 57,  4,  9, 'ⵇ', 'Qel', 0x2D47),
    ( 58,  4, 10, 'ⵉ', 'Irn', 0x2D49),
    ( 59,  4, 11, 'ⵊ', 'Jen', 0x2D4A),
    ( 60,  5,  0, 'ꠇ', 'Fi', 0xA807),
    ( 61,  5,  1, 'ꠈ', 'Lun', 0xA808),
    ( 62,  5,  2, 'ꠉ', 'Varu', 0xA809),
    ( 63,  5,  3, 'ꠊ', 'Senh', 0xA80A),
    ( 64,  5,  4, '⎉', 'Kos', 0x2389),
    ( 65,  5,  5, 'ꠌ', 'Ramh', 0xA80C),
    ( 66,  5,  6, 'ꠍ', 'Tis', 0xA80D),
    ( 67,  5,  7, 'ꠎ', 'Vey', 0xA80E),
    ( 68,  5,  8, 'ꠏ', 'Srih', 0xA80F),
    ( 69,  5,  9, 'ꠐ', 'Hrin', 0xA810),
    ( 70,  5, 10, 'ꠑ', 'Yon', 0xA811),
    ( 71,  5, 11, 'ꠒ', 'Thal', 0xA812),
    ( 72,  6,  0, '🝏', 'Kel', 0x1F74F),
    ( 73,  6,  1, '🜁', 'Sens', 0x1F701),
    ( 74,  6,  2, '🜃', 'Linn', 0x1F703),
    ( 75,  6,  3, '🜄', 'Brim', 0x1F704),
    ( 76,  6,  4, '🜅', 'Inn', 0x1F705),
    ( 77,  6,  5, '🜆', 'Subh', 0x1F706),
    ( 78,  6,  6, '🜇', 'Well', 0x1F707),
    ( 79,  6,  7, '🜈', 'Met', 0x1F708),
    ( 80,  6,  8, '🜉', 'Kesh', 0x1F709),
    ( 81,  6,  9, '🜊', 'Soth', 0x1F70A),
    ( 82,  6, 10, '🜋', 'Rhun', 0x1F70B),
    ( 83,  6, 11, '🜌', 'Delh', 0x1F70C),
    ( 84,  7,  0, '𒀀', 'Na', 0x12000),
    ( 85,  7,  1, '𒀭', 'Ur', 0x1202D),
    ( 86,  7,  2, '𒁀', 'Nih', 0x12040),
    ( 87,  7,  3, '𒂊', 'Azh', 0x1208A),
    ( 88,  7,  4, '𒄑', 'Hol', 0x12111),
    ( 89,  7,  5, '𒅆', 'Gur', 0x12146),
    ( 90,  7,  6, '𒆠', 'Ves', 0x121A0),
    ( 91,  7,  7, '𒇽', 'Rim', 0x121FD),
    ( 92,  7,  8, '𒉌', 'Drem', 0x1224C),
    ( 93,  7,  9, '𒊕', 'Oth', 0x12295),
    ( 94,  7, 10, '𒋗', 'Izh', 0x122D7),
    ( 95,  7, 11, '𒌋', 'Sun', 0x1230B),
    ( 96,  8,  0, 'ⶀ', 'Kia', 0x2D80),
    ( 97,  8,  1, 'ⶁ', 'Zohm', 0x2D81),
    ( 98,  8,  2, 'ⶂ', 'Ther', 0x2D82),
    ( 99,  8,  3, 'ⶃ', 'Drun', 0x2D83),
    (100,  8,  4, 'ⶄ', 'Felh', 0x2D84),
    (101,  8,  5, 'ⶅ', 'Ral', 0x2D85),
    (102,  8,  6, 'ⶆ', 'Krah', 0x2D86),
    (103,  8,  7, 'ⶇ', 'Andh', 0x2D87),
    (104,  8,  8, 'ⶈ', 'Debh', 0x2D88),
    (105,  8,  9, 'ⶉ', 'Kol', 0x2D89),
    (106,  8, 10, 'ⶊ', 'Fral', 0x2D8A),
    (107,  8, 11, 'ⶋ', 'Hush', 0x2D8B),
    (108,  9,  0, '𐤠', 'Hin', 0x10920),
    (109,  9,  1, '𐤡', 'Ser', 0x10921),
    (110,  9,  2, '𐤢', 'Harma', 0x10922),
    (111,  9,  3, '𐤣', 'Torh', 0x10923),
    (112,  9,  4, '𐤤', 'Pel', 0x10924),
    (113,  9,  5, '𐤥', 'Khir', 0x10925),
    (114,  9,  6, '𐤦', 'Ryth', 0x10926),
    (115,  9,  7, '𐤧', 'Melu', 0x10927),
    (116,  9,  8, '𐤨', 'Phaz', 0x10928),
    (117,  9,  9, '𐤩', 'Lokh', 0x10929),
    (118,  9, 10, '𐤪', 'Nod', 0x1092A),
    (119,  9, 11, '𐤫', 'Umel', 0x1092B),
    (120, 10,  0, '𐠀', 'Dohm', 0x10800),
    (121, 10,  1, '𐠁', 'Rist', 0x10801),
    (122, 10,  2, '𐠂', 'Tran', 0x10802),
    (123, 10,  3, '𐠃', 'Korh', 0x10803),
    (124, 10,  4, '𐠄', 'Skyh', 0x10804),
    (125, 10,  5, '𐠅', 'Ster', 0x10805),
    (126, 10,  6, '𐠝', 'Poss', 0x1081D),
    (127, 10,  7, '𐠞', 'Poru', 0x1081E),
    (128, 10,  8, '𐠈', 'Dorm', 0x10808),
    (129, 10,  9, '𐠜', 'Trev', 0x1081C),
    (130, 10, 10, '𐠋', 'Limh', 0x1080B),
    (131, 10, 11, '𐠌', 'Hinge', 0x1080C),
    (132, 11,  0, '𐔀', 'Tzig', 0x10500),
    (133, 11,  1, '𐔁', 'Pehl', 0x10501),
    (134, 11,  2, '𐔂', 'Duth', 0x10502),
    (135, 11,  3, '𐔃', 'Coma', 0x10503),
    (136, 11,  4, '𐔄', 'Meru', 0x10504),
    (137, 11,  5, '𐔅', 'Stab', 0x10505),
    (138, 11,  6, '𐔆', 'Hopa', 0x10506),
    (139, 11,  7, '𐔇', 'Conti', 0x10507),
    (140, 11,  8, '𐔈', 'Resth', 0x10508),
    (141, 11,  9, '𐔉', 'Sil', 0x10509),
    (142, 11, 10, '𐔊', 'Slun', 0x1050A),
    (143, 11, 11, '𐔋', 'Etern', 0x1050B),
)

_COURTS: Final[tuple[CourtRecord, ...]] = tuple(CourtRecord(*row) for row in _COURT_ROWS)

if len(_COURTS) != 144:
    raise RuntimeError('Court body must contain exactly 144 Courts')
for _r in _COURTS:
    if _r.address != 12 * _r.i + _r.j:
        raise RuntimeError(f'Court address {_r.address} != 12i+j')
    if ord(_r.glyph) != _r.codepoint:
        raise RuntimeError(f'Court glyph {_r.glyph!r} != U+{_r.codepoint:X}')
if len({_r.address for _r in _COURTS}) != 144:
    raise RuntimeError('Court addresses must be unique 0..143')
if len({_r.glyph for _r in _COURTS}) != 144:
    raise RuntimeError('Court glyphs must be unique')


def _pos(g: str) -> int:
    law(g)
    return GLYPH_BODY.index(g)


def court_record(address: int) -> CourtRecord:
    if isinstance(address, bool) or not isinstance(address, int):
        raise TypeError("Court address must be an integer")
    if not 0 <= address < 144:
        raise ValueError(f'Court address out of range: {address}')
    return _COURTS[address]


def court_from_goetics(g_i: str, g_j: str) -> CourtRecord:
    """C_i,j = sole Court at address 12i+j (plan §3.5). Deterministic; no draw."""
    return _COURTS[12 * _pos(g_i) + _pos(g_j)]





def gov_glyph(rec: CourtRecord) -> str:
    return GLYPH_BODY[rec.i]


def alt_glyph(rec: CourtRecord) -> str:
    return GLYPH_BODY[rec.j]


def court_ordinal(rec: CourtRecord) -> int:
    """Ordinal within governing row = hyperbolic-parent index + 1 (plan §3.5)."""
    return rec.j + 1


def full_name(rec: CourtRecord) -> str:
    return GOETIC_NAME[GLYPH_BODY[rec.i]] + rec.name_element
