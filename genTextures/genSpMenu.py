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
from jmbStruct import MetaData_JA, stOneSentence, stFontParam, stTex, texStrImage, texMeta
from jmbData import gDat_JA
from jmbConst import JmkUsage

from wand.image import Image
from wand.color import Color
from wand.font import Font

def gen_char_img(char: str) -> Image:
    usage = JmkUsage.Default
    assert(len(char) == 1)
    kind = fontTool.check_kind(char, usage)
    if kind == fontTool.FontKind.SPECIAL:
        kind = fontTool.FontKind.KANJI
    scale = 36 / 57 # current 36 HEIGHT vs default 57 HEIGHT
    img = Image(width=38*4, height=36*4, background=Color('transparent'))
    font_size   = kind.get_face_size(usage, extra_scale=1.1)
    print(f"char = {char}, kind = {kind}, usage = {usage}")
    print(f"\tfont_size = {font_size}")

    font_path = fontTool.Font_SourceHan
    img.font = Font(
        path=font_path,
        color = Color('white'),
        # stroke_color=Color('#d4d4d4'),
        # stroke_width=1,
        size = font_size
    )
    img.gravity = 'center'
    img.caption(text=char)
    # if char == "具" or char == "鸽":
    #     img.roll(y=-7)
    # else:
    img.roll(y=-6)
    return img

rsl_pack_exe = "D:/SteamLibrary/steamapps/common/killer7/Tools/no_more_rsl/rslPack.exe"

readonly_item_0    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\sub\\SpecialJ\\4x_moji_aJ.BIN"
readonly_item_1    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\sub\\SpecialJ\\4x_moji_iJ.BIN"
readonly_item_2    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\sub\\SpecialJ\\4x_moji_teJ.BIN"
readonly_item_3    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\sub\\SpecialJ\\4x_moji_muJ.BIN"
readonly_memo_0    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\sub\\SpecialJ\\4x_moji_meJ.BIN"
readonly_memo_1    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\sub\\SpecialJ\\4x_moji_moJ.BIN"
readonly_hato_0    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\sub\\SpecialJ\\4x_moji_haJ.BIN"
readonly_hato_1    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\sub\\SpecialJ\\4x_moji_toJ.BIN"
readonly_sore      = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\sub\\SpecialJ\\mojiJ.BIN"

extracted_item_0    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ\\4x_moji_aJ.BIN"
extracted_item_1    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ\\4x_moji_iJ.BIN"
extracted_item_2    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ\\4x_moji_teJ.BIN"
extracted_item_3    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ\\4x_moji_muJ.BIN"
extracted_memo_0    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ\\4x_moji_meJ.BIN"
extracted_memo_1    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ\\4x_moji_moJ.BIN"
extracted_hato_0    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ\\4x_moji_haJ.BIN"
extracted_hato_1    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ\\4x_moji_toJ.BIN"
extracted_sore      = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ\\mojiJ.BIN"
extracted_dir = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ"
extracted_rsl = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\sub\\SpecialJ.rsl"
dest_pak = "D:\\SteamLibrary\\steamapps\\common\\killer7\\sub\\SpecialJ.pak"

command = input("提取图片输入y;将修改后的图片封装回去输入n (y/n): ").lower().strip()
if command == "y":
    for r_tex in [  readonly_item_0, readonly_item_1, readonly_item_2, readonly_item_3,
                    readonly_memo_0, readonly_memo_1, readonly_hato_0, readonly_hato_1,
                    readonly_sore]:
        target_noext = os.path.join("genTextures", "spMenu", os.path.basename(r_tex)[:-4])
        with open(r_tex, 'rb') as fp:
            is_stri = fp.read(4) == b'STRI'
            fp.seek(0)
            if is_stri:
                strimage = texStrImage(fp)
                tex = strimage.tex
            else:
                tex = stTex(fp)
            print("tex header =", tex.header)
            DDSTool.print_info(tex.dds)
            tex.dump(target_noext+".dds")
            bin_dds_img = Image(blob=tex.dds)
            bin_dds_img.format = 'png'
            bin_dds_img.save(filename=target_noext+".png")
            bin_dds_img.close()
elif command == "n":
    orignal = "アイテムメモハト"
    translation = "　道具　笔记信鸽"
    for idx, e_tex in enumerate([   extracted_item_0, extracted_item_1, extracted_item_2, extracted_item_3,
                                    extracted_memo_0, extracted_memo_1, extracted_hato_0, extracted_hato_1]):
        mod_img_png = os.path.join("genTextures", "spMenu", os.path.basename(e_tex)[:-4] + "_mod.png")
        mod_img_dds = os.path.basename(e_tex)[:-4] + "_mod.dds"
        gen_img = gen_char_img(translation[idx])
        gen_img.format = 'png'
        gen_img.save(filename=mod_img_png)
        gen_img.close()
        if not os.path.exists(mod_img_png):
            print(f"图片{mod_img_png}不存在，跳过")
            continue

        print(f"处理{os.path.basename(e_tex)[:-4]}")
        command = [
            "texconv.exe",
            "-f", "B8G8R8A8_UNORM",  # 压缩格式 = 无
            "-ft", "dds",            # 输出文件类型
            "-srgb",                 # 输入为 sRGB，输出也为 sRGB
            "-m", "1",               # 禁用 mipmap
            "-y",                    # 覆盖输出文件（不提示）
            mod_img_png,             # 输入文件
        ]
        subprocess.run(command, check=True)
        print(f"\n成功重建DDS贴图: {mod_img_dds}")
        print(f"压缩格式: None (None)")

        bin = stTex()
        fp = open(mod_img_dds, 'rb')
        dds_bytes = fp.read()
        fp.close()
        os.remove(mod_img_dds)
        bin.dds = dds_bytes

        bin_header = texMeta()
        bin_header.magic = b'\x00'*4
        bin_header.encoding = b'\x06\x00\x00\x00'
        bin_dds_img = Image(filename=mod_img_png)
        width, height = bin_dds_img.size
        bin_dds_img.close()
        bin_header.w = width // 4
        bin_header.h = height // 4
        bin_header.dds_size = len(dds_bytes)
        print("bin updated header =", bin_header)

        bin.header = bin_header
        with open(e_tex, 'wb') as bfp:
            bin.write(bfp)

    for e_tex in [extracted_sore]:
        mod_img_png = os.path.join("genTextures", "spMenu", os.path.basename(e_tex)[:-4] + "_mod.png")
        mod_img_dds = os.path.basename(e_tex)[:-4] + "_mod.dds"
        if not os.path.exists(mod_img_png):
            print(f"图片{mod_img_png}不存在，跳过")
            continue

        print(f"处理{os.path.basename(e_tex)[:-4]}")
        command = [
            "texconv.exe",
            "-f", "B8G8R8A8_UNORM",  # 压缩格式 = 无
            "-ft", "dds",            # 输出文件类型
            "-srgb",                 # 输入为 sRGB，输出也为 sRGB
            "-m", "1",               # 禁用 mipmap
            "-y",                    # 覆盖输出文件（不提示）
            mod_img_png,             # 输入文件
        ]
        subprocess.run(command, check=True)
        print(f"\n成功重建DDS贴图: {mod_img_dds}")
        print(f"压缩格式: None (None)")

        bin = stTex()
        fp = open(mod_img_dds, 'rb')
        dds_bytes = fp.read()
        fp.close()
        os.remove(mod_img_dds)
        bin.dds = dds_bytes

        bin_header = texMeta()
        bin_header.magic = b'\x00'*4
        bin_header.encoding = b'\x06\x00\x00\x00'
        bin_dds_img = Image(filename=mod_img_png)
        width, height = bin_dds_img.size
        bin_dds_img.close()
        bin_header.w = width
        bin_header.h = height
        bin_header.dds_size = len(dds_bytes)
        print("bin updated header =", bin_header)

        bin.header = bin_header
        with open(e_tex, 'wb') as bfp:
            bin.write(bfp)

    subprocess.run([rsl_pack_exe, "--overwrite", extracted_dir], check=True)
    shutil.copy2(extracted_rsl, dest_pak)
else:
    print("输入错误")
    exit(1)