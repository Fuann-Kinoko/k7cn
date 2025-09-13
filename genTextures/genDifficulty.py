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

from wand.image import Image

rsl_pack_exe = "D:/SteamLibrary/steamapps/common/killer7/Tools/no_more_rsl/rslPack.exe"

readonly_text01 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\titleJ\\text_a_01.bin"
readonly_text02 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\titleJ\\text_a_02.bin"
readonly_text03 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\titleJ\\text_b_01.bin"
readonly_text04 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\titleJ\\text_b_02.bin"
readonly_text_d = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\titleJ\\text_d.bin"
readonly_text_e = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\titleJ\\text_e.bin"
extracted_text01 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\titleJ\\text_a_01.bin"
extracted_text02 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\titleJ\\text_a_02.bin"
extracted_text03 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\titleJ\\text_b_01.bin"
extracted_text04 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\titleJ\\text_b_02.bin"
extracted_text_d = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\titleJ\\text_d.bin"
extracted_text_e = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\titleJ\\text_e.bin"
extracted_dir = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\titleJ"
extracted_rsl = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\titleJ.rsl"
dest_rsl = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\titleJ.pak"

command = input("提取图片输入y;将修改后的图片封装回去输入n (y/n): ").lower().strip()
if command == "y":
    for readonly_text in [readonly_text01, readonly_text02, readonly_text03, readonly_text04, readonly_text_d, readonly_text_e]:
        target_noext = os.path.join("genTextures", "difficulty", os.path.basename(readonly_text)[:-4])
        with open(readonly_text, 'rb') as fp:
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
    for extracted_text in [extracted_text01, extracted_text02, extracted_text03, extracted_text04, extracted_text_d, extracted_text_e]:
        mod_img_png = os.path.join("genTextures", "difficulty", os.path.basename(extracted_text)[:-4] + "_mod.png")
        mod_img_dds = os.path.basename(extracted_text)[:-4] + "_mod.dds"
        if not os.path.exists(mod_img_png):
            print(f"图片{mod_img_png}不存在？")
            exit(1)

        command = [
            "texconv.exe",
            "-f", "R8G8B8A8_UNORM_SRGB",  # 压缩格式 = 无
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
        bin_header.w = width    # 这里不需要除以4，属于某些BIN的特例，不代表平时的不需要除以4
        bin_header.h = height   # 这里不需要除以4，属于某些BIN的特例，不代表平时的不需要除以4
        bin_header.dds_size = len(dds_bytes)
        print("bin updated header =", bin_header)

        bin.header = bin_header
        with open(extracted_text, 'wb') as bfp:
            bin.write(bfp)

    subprocess.run([rsl_pack_exe, "--overwrite", extracted_dir], check=True)
    shutil.copy2(extracted_rsl, dest_rsl)
else:
    print("输入错误")
    exit(1)