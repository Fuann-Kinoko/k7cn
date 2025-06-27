from typing import Dict
from jmbStruct import stFontParam

from wand.image import Image
from wand.color import Color
from wand.font import Font
from wand.display import display
from wand.drawing import Drawing

def parse_chardat_value(value: int) -> dict:
    JIMAKU_NO_FONT = 0xffff
    JIMAKU_RETURN = 0xfffe
    JIMAKU_SPACE_H = 0xfffd  # 半角空格
    JIMAKU_SPACE_Z = 0xfffc  # 全角空格
    JIMAKU_FLAG_SATSU = 0x8000  # 「殺」字符标志
    JIMAKU_FLAG_SHI = 0x7000    # 「死」字符标志
    """解析单个 chardat 值，返回结构化信息"""
    result = {
        "raw_value": value,
        "is_special": False,
        "is_satsu": False,
        "is_shi": False,
        "char_type": None,
        "char_code": None,
    }

    # 检查特殊字符
    if value == JIMAKU_NO_FONT:
        result.update({"is_special": True, "char_type": "NO_FONT"})
    elif value == JIMAKU_RETURN:
        result.update({"is_special": True, "char_type": "RETURN"})
    elif value == JIMAKU_SPACE_H:
        result.update({"is_special": True, "char_type": "SPACE_HALF"})
    elif value == JIMAKU_SPACE_Z:
        result.update({"is_special": True, "char_type": "SPACE_FULL"})
    else:
        # 检查是否包含特殊标志
        if value & JIMAKU_FLAG_SATSU:
            result.update({"is_satsu": True, "char_code": value & 0x0fff})
        elif value & JIMAKU_FLAG_SHI:
            result.update({"is_shi": True, "char_code": value & 0x0fff})
        else:
            result["char_code"] = value

    return result

def register(jmk : str) -> tuple[Dict, str]:
    counter = 0
    unique_jmk = ""
    char_dict = {}
    for char in jmk:
        if char == "、" or char == "。" or char == " ":
            char_dict[char] = "SPC"
            continue
        if char not in char_dict:
            unique_jmk += char
            char_dict[char] = counter
            counter += 1
    return char_dict, unique_jmk

def transpile(lookup: dict, input : str) -> list[int]:
    return [lookup[ch] for ch in input]

# fParams = [stFontParam(u=0, v=0, w=26, h=57), stFontParam(u=26, v=0, w=26, h=57), stFontParam(u=52, v=0, w=26, h=57), stFontParam(u=78, v=0, w=35, h=57), stFontParam(u=114, v=0, w=26, h=57), stFontParam(u=140, v=0, w=26, h=57), stFontParam(u=166, v=0, w=28, h=57), stFontParam(u=195, v=0, w=28, h=57), stFontParam(u=224, v=0, w=35, h=57), stFontParam(u=260, v=0, w=28, h=57), stFontParam(u=289, v=0, w=35, h=57), stFontParam(u=325, v=0, w=35, h=57), stFontParam(u=361, v=0, w=35, h=57), stFontParam(u=397, v=0, w=35, h=57), stFontParam(u=433, v=0, w=26, h=57), stFontParam(u=459, v=0, w=35, h=57), stFontParam(u=0, v=57, w=26, h=57), stFontParam(u=26, v=57, w=26, h=57), stFontParam(u=52, v=57, w=26, h=57), stFontParam(u=78, v=57, w=21, h=57), stFontParam(u=100, v=57, w=21, h=57), stFontParam(u=122, v=57, w=35, h=57), stFontParam(u=158, v=57, w=35, h=57), stFontParam(u=194, v=57, w=26, h=57), stFontParam(u=220, v=57, w=26, h=57), stFontParam(u=246, v=57, w=26, h=57), stFontParam(u=272, v=57, w=26, h=57), stFontParam(u=298, v=57, w=26, h=57), stFontParam(u=324, v=57, w=35, h=57), stFontParam(u=360, v=57, w=35, h=57), stFontParam(u=396, v=57, w=47, h=57), stFontParam(u=444, v=57, w=26, h=57), stFontParam(u=470, v=57, w=26, h=57), stFontParam(u=0, v=114, w=35, h=57), stFontParam(u=36, v=114, w=26, h=57), stFontParam(u=62, v=114, w=35, h=57), stFontParam(u=98, v=114, w=26, h=57), stFontParam(u=124, v=114, w=26, h=57), stFontParam(u=150, v=114, w=26, h=57), stFontParam(u=176, v=114, w=26, h=57), stFontParam(u=202, v=114, w=28, h=57), stFontParam(u=231, v=114, w=35, h=57), stFontParam(u=267, v=114, w=35, h=57), stFontParam(u=303, v=114, w=35, h=57), stFontParam(u=339, v=114, w=26, h=57), stFontParam(u=365, v=114, w=35, h=57), stFontParam(u=401, v=114, w=35, h=57), stFontParam(u=437, v=114, w=35, h=57), stFontParam(u=473, v=114, w=26, h=57), stFontParam(u=0, v=171, w=26, h=57), stFontParam(u=26, v=171, w=26, h=57), stFontParam(u=52, v=171, w=26, h=57), stFontParam(u=78, v=171, w=19, h=57), stFontParam(u=97, v=171, w=35, h=57), stFontParam(u=133, v=171, w=26, h=57), stFontParam(u=159, v=171, w=35, h=57), stFontParam(u=195, v=171, w=19, h=57), stFontParam(u=214, v=171, w=26, h=57), stFontParam(u=240, v=171, w=35, h=57), stFontParam(u=276, v=171, w=35, h=57), stFontParam(u=312, v=171, w=35, h=57), stFontParam(u=348, v=171, w=35, h=57), stFontParam(u=384, v=171, w=35, h=57), stFontParam(u=420, v=171, w=35, h=57), stFontParam(u=456, v=171, w=26, h=57), stFontParam(u=0, v=228, w=35, h=57), stFontParam(u=36, v=228, w=26, h=57), stFontParam(u=62, v=228, w=26, h=57), stFontParam(u=88, v=228, w=35, h=57), stFontParam(u=124, v=228, w=35, h=57), stFontParam(u=160, v=228, w=35, h=57), stFontParam(u=196, v=228, w=35, h=57)]
# jimaku = "そこが巣だこのアパートが？連中の群れだ調べでは、14匹が棲みついている全部、殺っていいのか？1匹は、生け捕りにしてくれココの親玉が居るはずだ情報は？会えばわかるさ“笑う顔”とは決定的に違う了解した神に笑いを…悪魔に慈悲を…"
fParams = [
    stFontParam(u=0, v=0, w=35, h=57),
    stFontParam(u=36, v=0, w=35, h=57),
    stFontParam(u=72, v=0, w=35, h=57),
    stFontParam(u=108, v=0, w=35, h=57),
]
jimaku = "中文測試"
char_dict, unique_jimaku = register(jimaku)

print(unique_jimaku)
print(len(unique_jimaku))

JIMAKU_TEX_WIDTH = 512
gFontSize = 57
gJC = None
gDat = None

font_path = "HiraginoMinCho-W6.ttc"
# font_path = "HiraginoMin-W4.ttf"
face = Font(path=font_path, color = Color('white'), stroke_color=Color('#d4d4d4'), stroke_width=1)

# print("====")
# line = 0
# current_x = 0
# for i, char in enumerate(unique_jimaku):
#     w = fParams[i].w
#     h = fParams[i].h
#     with Image(width=w*4, height=h*4, background=Color('transparent')) as canvas:
#         canvas.font = face
#         canvas.gravity = 'center'
#         canvas.caption(text=char)
#         canvas.save(filename=f'output{i}.png')
#         # display(canvas)
#     # TODO: 换行


full = "そこが巣だこのアパートが？連中の群れだ調べでは、14匹が棲みついている全部、殺っていいのか？1匹は、生け捕りにしてくれココの親玉が居るはずだ情報は？会えばわかるさ“笑う顔”とは決定的に違う了解した神に笑いを…悪魔に慈悲を…"
full_dict, full_unique = register(full)
print("+sent 0")
print("そこが巣だ", transpile(full_dict, "そこが巣だ"))
print("このアパートが？", transpile(full_dict, "このアパートが？"))
print("+sent 1")
print("連中の群れだ", transpile(full_dict, "連中の群れだ"))
print("調べでは、14匹が棲みついている", transpile(full_dict, "調べでは、14匹が棲みついている"))
print("+sent 2")
print("全部、殺っていいのか？", transpile(full_dict, "全部、殺っていいのか？"))
print("+sent 3")
print("1匹は、生け捕りにしてくれ", transpile(full_dict, "1匹は、生け捕りにしてくれ"))
print("ココの親玉が居るはずだ", transpile(full_dict, "ココの親玉が居るはずだ"))