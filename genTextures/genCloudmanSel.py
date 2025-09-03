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
from wand.color import Color

rsl_pack_exe = "D:/SteamLibrary/steamapps/common/killer7/Tools/no_more_rsl/rslPack.exe"

readonly_q1        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\panel\\020301J\\q1J.BIN"
readonly_q2        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\panel\\020301J\\q2J.BIN"
readonly_q3        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\panel\\020301J\\q3J.BIN"
readonly_q4        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\panel\\020301J\\q4J.BIN"
readonly_q5        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\panel\\020301J\\q5J.BIN"
readonly_q6        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\panel\\020301J\\q6J.BIN"
readonly_q7        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\panel\\020301J\\q7J.BIN"

extracted_q1        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\020301J\\q1J.BIN"
extracted_q2        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\020301J\\q2J.BIN"
extracted_q3        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\020301J\\q3J.BIN"
extracted_q4        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\020301J\\q4J.BIN"
extracted_q5        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\020301J\\q5J.BIN"
extracted_q6        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\020301J\\q6J.BIN"
extracted_q7        = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\020301J\\q7J.BIN"
extracted_dir = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\020301J"
extracted_rsl = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\panel\\020301J.rsl"
dest_rsl = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\panel\\020301J.pak"

command = input("提取图片输入y;将修改后的图片封装回去输入n (y/n): ").lower().strip()
if command == "y":
    for r_tex in [readonly_q1, readonly_q2, readonly_q3, readonly_q4, readonly_q5, readonly_q6, readonly_q7]:
        target_noext = os.path.join("genTextures", "cloudmanPanel", os.path.basename(r_tex)[:-4])
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
    for e_tex in [extracted_q1, extracted_q2, extracted_q3, extracted_q4, extracted_q5, extracted_q6, extracted_q7]:
        mod_img_png = os.path.join("genTextures", "cloudmanPanel", os.path.basename(e_tex)[:-4] + "_mod.png")
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
        bin_header.w = width    # 这里不需要除以4，属于某些BIN的特例，不代表平时的不需要除以4
        bin_header.h = height   # 这里不需要除以4，属于某些BIN的特例，不代表平时的不需要除以4
        bin_header.dds_size = len(dds_bytes)
        print("bin updated header =", bin_header)

        bin.header = bin_header
        with open(e_tex, 'wb') as bfp:
            bin.write(bfp)

    subprocess.run([rsl_pack_exe, "--overwrite", extracted_dir], check=True)
    shutil.copy2(extracted_rsl, dest_rsl)
else:
    print("输入错误")
    exit(1)