import io
import json
import os
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Any

current_dir = Path(__file__).parent
assert os.path.dirname(current_dir) != "map", f"当前目录：{current_dir}\nrun.py这个脚本会被假装linking到各个子文件夹中执行，请在genMapFont.py中调用它，而不是手动调用"
work_dir_path = current_dir / ".." / ".."         / ".."
#                             map    genTextures    workDir
sys.path.append(str(work_dir_path.resolve()))

import DDSTool
import fontTool
import k7FileList
from jmbStruct import MetaData_JA, stOneSentence, stFontParam, stTex, texStrImage, texMeta, SIChr, SIStr
from jmbData import gDat_JA
from jmbConst import JmkUsage, JmkKind

from wand.image import Image
from wand.color import Color
from wand.font import Font
from wand.drawing import Drawing

print_info:Any # extern
lister = k7FileList.FileLister()
# 这个脚本需要从 genMapFont.py调用

rsl_pack_exe = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Tools\\no_more_rsl\\rslPack.exe"

def gen_default_chr(char: str, addx, height, cur_x = 0, cur_y = 0, dy = 0) -> SIChr:
    addw = 1
    c = SIChr()
    c.code = ord(char)
    c.code2 = ord(char)
    c.x = cur_x
    c.y = cur_y
    c.w = addx
    c.h = height
    c.dx = 0
    c.dy = dy
    c.addx = addx
    assert addw == 1
    c.addw = b'\x01'
    return c

def gen_default_image(char: str) -> tuple[Image, int, int]:
    usage = JmkUsage.Default
    assert(len(char) == 1)
    kind = fontTool.check_kind(char, usage)
    if kind == fontTool.FontKind.SPECIAL:
        kind = fontTool.FontKind.KANJI
    scale = 30 / 57 # current 30 HEIGHT vs default 57 HEIGHT
    img_width   = 8 * kind.get_width(usage, ch = char, extra_scale=scale)
    img_height  = 4 * kind.get_height(usage, ch = char,extra_scale=scale)
    font_size   = kind.get_face_size(usage, extra_scale=scale * 1.64)
    print(f"char = {char}, kind = {kind}, usage = {usage}")
    print(f"\twidth = {img_width}, height = {img_height}, font_size = {font_size}")
    import PIL.Image as PILImage
    import PIL.ImageDraw as PILImageDraw
    import PIL.ImageFont as PILImageFont
    pil_img = PILImage.new("RGBA", (img_width, img_height), color=(0,0,0,0))
    pil_font = PILImageFont.truetype("SourceHanSerifCN-Bold.ttf", font_size)
    pil_draw = PILImageDraw.Draw(pil_img)
    bbox = pil_draw.textbbox((0, 0), char, font=pil_font)
    text_width = int(bbox[2] - bbox[0])
    text_height = int(bbox[3] - bbox[1])
    pil_draw.text((-bbox[0], -bbox[1]), char, font=pil_font, fill='white')
    # DEBUG: 边界框
    # pil_draw.rectangle([0, 0, text_width, text_height], outline='red', width=1)
    print(f"\trectangle: width={text_width}, height={text_height}, dy={int(bbox[1])}")
    img_buffer = io.BytesIO()
    pil_img.save(img_buffer, format='PNG')
    img_blob = img_buffer.getvalue()
    pil_img.close()
    img = Image(blob=img_blob)
    img.crop(left=0, top=0, width=text_width, height=img_height)
    return img, text_height, int(bbox[1])-32

def dump(map_name: str, strimage: texStrImage):
    strimage.tex.dump(os.path.join(current_dir, map_name + ".dds"))
    print(f"{current_dir}: 导出 {map_name}.dds")

def register(json_data:list[list[str]]) -> list[str]:
    all_text = ''.join(lister.flatten_list(json_data))
    unique_chars = set()
    regs = []
    for char in all_text:
        if char in unique_chars:
            continue
        unique_chars.add(char)
        regs.append(char)
    return regs

def gen_ori(map_name: str, strimage: texStrImage, output_path):
    ori:list[list[str]] = []
    strs:list[str] = []
    chars:list[str] = []
    for chb_idx in strimage.chb:
        chars.append(f"{chr(chb_idx.code)}")
    for sistr in strimage.str:
        cur_str:list[str] = []
        for chb_idx in sistr.strIndex:
            if chb_idx == -1:
                break
            cur_str.append(chars[chb_idx])
        strs.append("".join(cur_str))
    for pack in strimage.strpack:
        cur_pack:list[str] = []
        for sistr_idx in pack.strIndex:
            if sistr_idx == -1:
                break
            cur_pack.append(strs[sistr_idx])
        ori.append(cur_pack)
    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(ori, fp, ensure_ascii=False, indent=2)
    print(f"{current_dir}: 导出{map_name}_ori.json")

def update(map_name: str, strimage: texStrImage, input_path):
    with open(input_path, "r", encoding="utf-8") as fp:
        translation = json.load(fp)
    BLOCK_HEIGHT = 30
    PACK_NUM = len(strimage.strpack)
    STR_NUM = len(lister.flatten_list(translation))
    moji = register(translation)
    moji_lut = {char: idx for idx, char in enumerate(moji)}
    assert PACK_NUM == strimage.header.strPackNum
    strimage.header.strNum = STR_NUM
    strimage.header.chrNum = len(moji)

    # 更新 pack 信息
    unq_str_idx_for_pak = 0
    for pak_idx, pak in enumerate(strimage.strpack):
        strs_in_pak = translation[pak_idx]
        new_ctls = []
        for i in range(len(strs_in_pak)):
            new_ctls.append(unq_str_idx_for_pak)
            unq_str_idx_for_pak += 1
        new_ctls.append(-1)
        new_ctls.extend([0] * (31 - len(new_ctls)))
        assert len(new_ctls) == 31
        pak.strIndex = new_ctls
    del unq_str_idx_for_pak

    # 更新 str 信息
    flatten_trans = lister.flatten_list(translation)
    strimage.str = []
    for sistr_idx in range(STR_NUM):
        cur_str = SIStr()
        sistr_text = flatten_trans[sistr_idx]
        new_ctls = []
        for char in sistr_text:
            ctl = moji_lut[char]
            new_ctls.append(ctl)
        new_ctls.append(-1)
        new_ctls.extend([0] * (129 - len(new_ctls)))
        assert len(new_ctls) == 129
        cur_str.strIndex = new_ctls
        strimage.str.append(cur_str)

    # 更新 tex 以及 chr 信息
    gCurX = 0
    gCurY = 0
    gMaxWidth = 0
    gCurLineCharCnt = 0
    WIDTH_CAPACITY = 3 if 3*(1+(len(moji) // 3)) < 4*(1+(len(moji) // 4)) else 4
    canvas = Image(
        width   = 4 * WIDTH_CAPACITY * BLOCK_HEIGHT,
        height  = 4 * (3 + len(moji)//WIDTH_CAPACITY) * BLOCK_HEIGHT,
        background=Color('transparent'))
    strimage.chb = []
    for ch in moji:
        if gCurLineCharCnt >= WIDTH_CAPACITY:
            gCurX = 0
            gCurY += BLOCK_HEIGHT
            gCurLineCharCnt = 0

        c_img, bbox_h, dy = gen_default_image(ch)
        w,h = c_img.size
        assert h == BLOCK_HEIGHT * 4
        canvas.composite(c_img, left=gCurX*4, top=gCurY*4)
        c_img.close()

        c = gen_default_chr(ch, w // 4, bbox_h // 4, gCurX, gCurY, dy = dy // 4)
        strimage.chb.append(c)

        gCurX += w // 4
        gCurLineCharCnt += 1
        gMaxWidth = max(gMaxWidth, gCurX)
    canvas.crop(0, 0, width=gMaxWidth*4, height=(gCurY + BLOCK_HEIGHT)*4)
    canvas.format='png'
    updated_img_path = os.path.join(current_dir, map_name + "_mod.png")
    canvas.save(filename=os.path.join(current_dir, updated_img_path))
    canvas.close()

    command = [
        "texconv.exe",
        "-f", "BC7_UNORM_SRGB",  # 压缩格式
        "-ft", "dds",            # 输出文件类型
        "-srgb",                 # 输入为 sRGB，输出也为 sRGB
        "-m", "1",               # 禁用 mipmap
        "-y",                    # 覆盖输出文件（不提示）
        updated_img_path,        # 输入文件
    ]
    subprocess.run(command, check=True)
    output_dds = os.path.join(work_dir_path, map_name + "_mod.dds")
    fp = open(output_dds, 'rb')
    dds_bytes = fp.read()
    fp.close()
    os.remove(output_dds)
    bin_dds_img = Image(blob=dds_bytes)
    width, height = bin_dds_img.size
    bin_dds_img.close()
    strimage.tex.header.w = width // 4
    strimage.tex.header.h = height // 4
    strimage.tex.header.dds_size = len(dds_bytes)
    # 组装
    strimage.tex.dds = dds_bytes
    return strimage

def run(map_data):
    # 获取当前文件夹名称（即地图名称）
    map_name = map_data["name"]
    readonly_sti = map_data["readonly_sti"]
    fp = open(readonly_sti, "rb")
    assert fp.read(4) == b'STRI', "invalid file format"
    fp.seek(0)
    strimage = texStrImage(fp)
    fp.close()

    # 执行 dump 操作
    # dump()

    # print 基本信息
    print_info(strimage)

    # 生成 ori.json
    # json_ori_path = os.path.join(current_dir, map_name + "_ori.json")
    # gen_ori(map_name, strimage, json_ori_path)

    # 读入 trans.json 修改strimage 打包并返回
    json_trans_path = os.path.join(current_dir, map_name + "_trans.json")
    updated_strimage = update(map_name, strimage, json_trans_path)
    extracted_path = map_data["extracted_sti"]
    with open(extracted_path, "wb") as fp:
        updated_strimage.write(fp)
    print(f"{current_dir}: 导出{map_name}的sti")
    print_info(updated_strimage)
    extracted_dir = map_data["extracted_dir"]
    extracted_rsl = map_data["extracted_rsl"]
    dest_pak = map_data["dest_pak"]
    subprocess.run([rsl_pack_exe, "--overwrite", extracted_dir], check=True)
    shutil.copy2(extracted_rsl, dest_pak)