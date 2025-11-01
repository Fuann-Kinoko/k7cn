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
from jmbTool.jmbStruct import MetaData_JA, stOneSentence, stFontParam, stTex, texStrImage, texMeta
from jmbTool.jmbData import gDat_JA

from wand.image import Image

rsl_pack_exe = "D:/SteamLibrary/steamapps/common/killer7/Tools/no_more_rsl/rslPack.exe"

readonly_ru     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\ru.BIN"
readonly_ranai  = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\ranai.BIN"
readonly_t0     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial00J.BIN"
readonly_t1     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial01J.BIN"
readonly_t2     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial02J.BIN"
readonly_t3     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial03J.BIN"
readonly_t4     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial04J.BIN"
readonly_t5     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial05J.BIN"
readonly_t6     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial06J.BIN"
readonly_t7     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial07J.BIN"
readonly_t8     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial08J.BIN"
readonly_t9     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\tutorialJ\\Tutorial09J.BIN"
readonly_m1     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\panelTutorialJ\\4x_moji_01J.BIN"
readonly_m2     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\panelTutorialJ\\4x_moji_02J.BIN"
readonly_m3     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\panelTutorialJ\\4x_moji_03J.BIN"
readonly_m4     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\panelTutorialJ\\4x_moji_04J.BIN"
readonly_m5     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\panelTutorialJ\\4x_moji_05J.BIN"
readonly_m6     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\tutorial\\panelTutorialJ\\4x_moji_06J.BIN"

extracted_ru     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\ru.BIN"
extracted_ranai  = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\ranai.BIN"
extracted_t0     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial00J.BIN"
extracted_t1     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial01J.BIN"
extracted_t2     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial02J.BIN"
extracted_t3     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial03J.BIN"
extracted_t4     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial04J.BIN"
extracted_t5     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial05J.BIN"
extracted_t6     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial06J.BIN"
extracted_t7     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial07J.BIN"
extracted_t8     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial08J.BIN"
extracted_t9     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ\\Tutorial09J.BIN"
extracted_m1     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\panelTutorialJ\\4x_moji_01J.BIN"
extracted_m2     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\panelTutorialJ\\4x_moji_02J.BIN"
extracted_m3     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\panelTutorialJ\\4x_moji_03J.BIN"
extracted_m4     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\panelTutorialJ\\4x_moji_04J.BIN"
extracted_m5     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\panelTutorialJ\\4x_moji_05J.BIN"
extracted_m6     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\panelTutorialJ\\4x_moji_06J.BIN"
extracted_dir = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ"
extracted_rsl = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\tutorialJ.rsl"
dest_rsl = "D:\\SteamLibrary\\steamapps\\common\\killer7\\tutorial\\tutorialJ.rsl"
extracted_dir2 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\panelTutorialJ"
extracted_rsl2 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\tutorial\\panelTutorialJ.rsl"
dest_rsl2 = "D:\\SteamLibrary\\steamapps\\common\\killer7\\tutorial\\panelTutorialJ.pak"

command = input("提取图片输入y;将修改后的图片封装回去输入n (y/n): ").lower().strip()
if command == "y":
    for r_tex in [
        readonly_ru, readonly_ranai,
        readonly_t0, readonly_t1, readonly_t2, readonly_t3, readonly_t4,
        readonly_t5, readonly_t6, readonly_t7, readonly_t8, readonly_t9,
        readonly_m1, readonly_m2, readonly_m3, readonly_m4, readonly_m5, readonly_m6
    ]:
        target_noext = os.path.join("genTextures", "tutorial", os.path.basename(r_tex)[:-4])
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
    for e_tex in [
        extracted_ru, extracted_ranai,
        extracted_t0, extracted_t1, extracted_t2, extracted_t3, extracted_t4,
        extracted_t5, extracted_t6, extracted_t7, extracted_t8, extracted_t9,
        extracted_m1, extracted_m2, extracted_m3, extracted_m4, extracted_m5, extracted_m6
        ]:
        m_series = False
        if e_tex in [extracted_m1, extracted_m2, extracted_m3, extracted_m4, extracted_m5, extracted_m6]:
            m_series = True

        mod_img_png = os.path.join("genTextures", "tutorial", os.path.basename(e_tex)[:-4] + "_mod.png")
        mod_img_dds = os.path.basename(e_tex)[:-4] + "_mod.dds"
        if not os.path.exists(mod_img_png):
            print(f"图片{mod_img_png}不存在，跳过")
            continue

        print(f"处理{os.path.basename(e_tex)[:-4]}")
        command = [
            "texconv.exe",
            "-f", "R8G8B8A8_UNORM",  # 压缩格式 = 无
            "-ft", "dds",            # 输出文件类型
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
        if not m_series:
            bin_header.w = width    # 这里不需要除以4，属于某些BIN的特例，不代表平时的不需要除以4
            bin_header.h = height   # 这里不需要除以4，属于某些BIN的特例，不代表平时的不需要除以4
        else:
            bin_header.w = width // 4
            bin_header.h = height // 4
        bin_header.dds_size = len(dds_bytes)
        print("bin updated header =", bin_header)

        bin.header = bin_header
        with open(e_tex, 'wb') as bfp:
            bin.write(bfp)

    subprocess.run([rsl_pack_exe, "--overwrite", extracted_dir], check=True)
    shutil.copy2(extracted_rsl, dest_rsl)
    subprocess.run([rsl_pack_exe, "--overwrite", extracted_dir2], check=True)
    shutil.copy2(extracted_rsl2, dest_rsl2)
else:
    print("输入错误")
    exit(1)