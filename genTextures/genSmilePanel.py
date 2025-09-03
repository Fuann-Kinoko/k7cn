import json
import os
import shutil
import sys
import subprocess
from pathlib import Path

current_dir = Path(__file__).parent
work_dir_path = current_dir / ".."
sys.path.append(str(work_dir_path.resolve()))

import DDSTool
import fontTool
from jmbStruct import MetaData_JA, stOneSentence, stFontParam, stTex, texStrImage, texMeta, SIChr
from jmbData import gDat_JA

from wand.image import Image
from wand.color import Color
from wand.font import Font

def print_info(st: texStrImage):
    print(st.header)
    for i in range(st.header.strPackNum):
        print(st.strpack[i])
    for i in range(st.header.strNum):
        print(st.str[i])
    for i in range(st.header.chrNum):
        print(f"[{i}] {st.chb[i]}")
    print(f"{st.tex.header.w=}, {st.tex.header.h=}, {st.tex.header.dds_size=}")
    print(f"{len(st.tex.dds)=}")
    print(st.tex.header)
    print("="*20)

def gen_char_image(char: str, width, height) -> Image:
    assert(len(char) == 1)
    img = Image(width=width*4, height=height*4, background=Color('transparent'))
    font_path = "MS_Gothic_SC.ttf"
    img.font = Font(
        path=font_path,
        color = Color('white'),
        size = height*4
    )
    img.gravity = 'center'
    img.caption(text=char)
    OFFSET = -4
    img.roll(y=OFFSET)
    return img

def gen_default_chr(char: str, cur_x = 0, cur_y = 0) -> SIChr:
    addx = BLOCK_HEIGHT
    addw = 1
    c = SIChr()
    c.code = ord(char)
    c.code2 = ord(char)
    c.x = cur_x
    c.y = cur_y
    c.w = addx
    c.h = addx
    c.dx = 0
    c.dy = 0
    c.addx = addx
    assert addw == 1
    c.addw = b'\x01'
    return c

rsl_pack_exe = "D:/SteamLibrary/steamapps/common/killer7/Tools/no_more_rsl/rslPack.exe"

readonly_sti = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\panel\\055500J\\keyboardJ.sti"

extracted_sti = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\055500J\\keyboardJ.sti"
extracted_dir = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\055500J"
extracted_rsl = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\055500J.rsl"
dest_rsl = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\panel\\055500J.pak"

smile_json = os.path.join("genTextures", "smilePanel", "smile.json")

fp = open(readonly_sti, "rb")
assert fp.read(4) == b'STRI', "invalid file format"
fp.seek(0)
strimage = texStrImage(fp)
fp.close()

print_info(strimage)

# 前面 0~40 这41个字符都最好不要动，因为是英文字母和特殊字符
START_CHAR = 41
unique_cnt = 0
unique_chars = set()
char2ctl = dict()
ctl2char = dict()

def register(ch: str):
    global unique_chars, unique_cnt, char2ctl, ctl2char
    if ch not in unique_chars:
        char2ctl[ch] = unique_cnt
        ctl2char[unique_cnt] = ch
        unique_cnt += 1
        unique_chars.add(ch)

predefined_chars = " 1234567890-QWERTYUIOPASDFGHJKLZXCVBNM,.?"
for ch in predefined_chars:
    register(ch)
assert unique_cnt == START_CHAR
with open(smile_json, "r", encoding="utf-8") as jsonf:
    data = json.load(jsonf)
    assert isinstance(data, list), "json格式不对"
    g_sent_i = 0
    for pack in data:
        assert isinstance(pack, list), "json格式不对"
        for sent in pack:
            assert isinstance(sent, str), "json格式不对"
            ch_i = 0
            for ch in sent:
                register(ch)
                strimage.str[g_sent_i].strIndex[ch_i] = char2ctl[ch]
                ch_i += 1
            strimage.str[g_sent_i].strIndex[ch_i] = -1
            ch_i += 1
            while ch_i < 129:
                strimage.str[g_sent_i].strIndex[ch_i] = 0
                ch_i += 1
            g_sent_i += 1

BLOCK_HEIGHT = 39
gCurX = 0
gCurY = 3 * BLOCK_HEIGHT
gCurLineCharCnt = 0
WIDTH_CAPACITY = 8
canvas = Image(
    width   = 4 * strimage.tex.header.w,
    height  = 4 * (strimage.tex.header.h + (len(unique_chars)//8)*BLOCK_HEIGHT),
    background=Color('transparent'))
# with open(os.path.join(current_dir, "smilePanel", "keyboardJ.dds"), "wb") as ddsfp:
#     ddsfp.write(strimage.tex.dds)
with Image(blob=strimage.tex.dds) as orig:
    orig.crop(0, 0, width=strimage.tex.header.w*4, height=BLOCK_HEIGHT*4*4)
    canvas.composite(orig, left=0, top=0)

strimage.chb = strimage.chb[:START_CHAR]
for char_ctl in range(START_CHAR, unique_cnt):
    ch = ctl2char[char_ctl]
    if gCurLineCharCnt >= WIDTH_CAPACITY:
        gCurX = 0
        gCurY += BLOCK_HEIGHT
        gCurLineCharCnt = 0
    c = gen_default_chr(ch, gCurX, gCurY)
    strimage.chb.append(c)
    c_img = gen_char_image(ch, BLOCK_HEIGHT, BLOCK_HEIGHT)
    canvas.composite(c_img, left=gCurX*4, top=gCurY*4, operator='copy')
    c_img.close()
    gCurX += BLOCK_HEIGHT
    gCurLineCharCnt += 1
canvas.crop(0, 0, width=strimage.tex.header.w*4, height=(gCurY + BLOCK_HEIGHT)*4)
canvas.format='png'
canvas.save(filename=os.path.join(current_dir, "smilePanel", "keyboardJ_mod.png"))
canvas.close()

command = [
    "texconv.exe",
    "-f", "BC7_UNORM_SRGB",  # 压缩格式
    "-ft", "dds",            # 输出文件类型
    "-srgb",                 # 输入为 sRGB，输出也为 sRGB
    "-m", "1",               # 禁用 mipmap
    "-y",                    # 覆盖输出文件（不提示）
    os.path.join(current_dir, "smilePanel", "keyboardJ_mod.png"),        # 输入文件
]
subprocess.run(command, check=True)
strimage_ddstex = stTex()
fp = open("keyboardJ_mod.dds", 'rb')
dds_bytes = fp.read()
fp.close()
dds_header = texMeta()
dds_header.magic = b'GCT0'
dds_header.encoding = b'\x00\x00\x00\x01'
bin_dds_img = Image(blob=dds_bytes)
width, height = bin_dds_img.size
bin_dds_img.close()
dds_header.w = width // 4
dds_header.h = height // 4
dds_header.dds_size = len(dds_bytes)
# 组装
strimage_ddstex.header = dds_header
strimage_ddstex.dds = dds_bytes
strimage.tex = strimage_ddstex
strimage.header.chrNum = unique_cnt

print("=== 修改后 ===")
print_info(strimage)

with open(extracted_sti, "wb") as fp:
    strimage.write(fp)
    print(f"write to {extracted_sti}")

subprocess.run([rsl_pack_exe, "--overwrite", extracted_dir], check=True)
shutil.copy2(extracted_rsl, dest_rsl)