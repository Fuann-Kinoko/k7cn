from enum import Enum, auto
from jmbStruct import stFontParam, stJimaku
from jmbDefine import gDat

from wand.image import Image
from wand.color import Color
from wand.font import Font
from wand.display import display
from wand.drawing import Drawing

font_path = "HiraginoMinCho-W6.ttc"
SATSU_FLAG = 0x8000
SHI_FLAG = 0x7000

DEFAULT_FACE_SIZE = 142         # scale = 7.5
KATA_FACE_SIZE = 112            # scale = 6
KANA_FACE_SIZE = 104            # scale = 5.5
SPECIAL_FACE_SIZE = 188         # scale = 10
NUM_FACE_SIZE = 112             # scale = 6
QUOTE_FACE_SIZE = 88            # scale = 6

DEFAULT_WIDTH = 35
KATA_WIDTH  = 28
KANA_WIDTH = 26
SPECIAL_WIDTH = 47
NUM_WIDTH = 21
QUOTE_WIDTH = 19

class FontKind(Enum):
    KANJI = auto()
    KATA = auto()
    KANA = auto()
    SPECIAL = auto()
    NUM = auto()
    QUOTE = auto()

    def get_face_size(self) -> int:
        match self:
            case FontKind.KANA:
                return KANA_FACE_SIZE
            case FontKind.KATA:
                return KATA_FACE_SIZE
            case FontKind.KANJI:
                return DEFAULT_FACE_SIZE
            case FontKind.NUM:
                return NUM_FACE_SIZE
            case FontKind.QUOTE:
                return QUOTE_FACE_SIZE
            case FontKind.SPECIAL:
                return SPECIAL_FACE_SIZE
            case _:
                NotImplemented

    def get_width(self) -> int:
        match self:
            case FontKind.KANA:
                return KANA_WIDTH
            case FontKind.KATA:
                return KATA_WIDTH
            case FontKind.KANJI:
                return DEFAULT_WIDTH
            case FontKind.NUM:
                return NUM_WIDTH
            case FontKind.QUOTE:
                return QUOTE_WIDTH
            case FontKind.SPECIAL:
                return SPECIAL_WIDTH
            case _:
                NotImplemented


def check_kind(char: str) -> FontKind:
    if len(char) != 1:
        raise ValueError("Input must be a single character")
    code = ord(char)
    if char == " " or char.isdigit():
        return FontKind.NUM
    elif char == "“" or char == "”":
        return FontKind.QUOTE
    # ひらがな（平假名）
    elif (0x3040 <= code <= 0x309F) or (char in {"、", "。", "，", "．", "・", "ー", "―", "‐", "～", "…", "‥"}):
        return FontKind.KANA
    # カタカナ（片假名）
    elif 0x30A0 <= code <= 0x30FF:
        return FontKind.KATA
    # 特殊字符（如「殺」「死」）
    elif char == "殺" or char == "死":
        return FontKind.SPECIAL
    # 默认认为是汉字
    else:
        return FontKind.KANJI

def register(input: str) -> tuple[dict[int, str], str]:
    counter = 0
    unique_jmk = ""
    int2char_dict = {}
    char2int_dict = {}
    for char in input:
        if char == "、" or char == "。" or char == " ":
            int2char_dict[counter] = " "
            continue
        if char not in char2int_dict:
            unique_jmk += char
            int2char_dict[counter] = char
            char2int_dict[char] = counter
            counter += 1
    int2char_dict[-3] = " "
    return int2char_dict, unique_jmk


def gen_char_image(char: str, info: stFontParam) -> Image:
    assert(len(char) == 1)
    img = Image(width=info.w*4, height=info.h*4, background=Color('transparent'))
    kind = check_kind(char)
    img.font = Font(
        path=font_path,
        color = Color('white'),
        # stroke_color=Color('#d4d4d4'),
        # stroke_width=1,
        size = kind.get_face_size()
    )
    img.gravity = 'center'
    img.caption(text=char)
    return img

def save_preview_jimaku(save_path: str, jimaku: stJimaku, fParams: list[stFontParam], char_ctl_lookup: dict[int, str]):
    char_data = gDat.display_char_data(jimaku.char_data)
    canvas = Image(width=35*4*len(char_data), height=57*4, background=Color('black'))
    current_x = 0
    for i, ctl in enumerate(char_data):
        if (ctl != -3) and ((ctl & SHI_FLAG) or (ctl & SATSU_FLAG)):
            ctl &= 0x0fff
        char = char_ctl_lookup[ctl]
        kind = check_kind(char)
        if char != " ":
            char_info = fParams[ctl]
        else:
            char_info = stFontParam(u=0,v=0,w=21,h=57)
        print(f"ctl = {ctl}; char = {char}; Kind = {kind};\tparams = {char_info}")
        char_img = gen_char_image(char, char_info)
        canvas.composite(char_img, left=current_x, top=0, operator='atop')
        char_img.close()

        # step = char_info.w # DEBUG
        step = kind.get_width()
        if kind in (FontKind.KANJI , FontKind.KATA , FontKind.NUM , FontKind.SPECIAL):
            step += 1
        current_x += step*4

    canvas.crop(0, 0, width=current_x, height=57*4)
    canvas.format='png'
    canvas.save(filename=save_path)
    canvas.close()

def save_char_image(save_path: str, char: str, info: stFontParam):
    img = gen_char_image(char, info)
    img.save(filename=save_path)
    img.close()