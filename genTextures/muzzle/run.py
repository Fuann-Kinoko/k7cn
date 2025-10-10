import io
import json
import os
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Any

current_dir = Path(__file__).parent
assert os.path.dirname(current_dir) != "muzzle", f"当前目录：{current_dir}\nrun.py这个脚本会被假装linking到各个子文件夹中执行，请在genMuzzle.py中调用它，而不是手动调用"
work_dir_path = current_dir / ".." / ".."         / ".."
#                           muzzle   genTextures    workDir
sys.path.append(str(work_dir_path.resolve()))

import DDSTool
import fontTool
import k7FileList
from jmbTool.jmbStruct import MetaData_JA, stOneSentence, stFontParam, stTex, texStrImage, texMeta, SIChr, SIStr
from jmbTool.jmbData import gDat_JA
from jmbTool.jmbConst import JmkUsage, JmkKind

from wand.image import Image
from wand.color import Color
from wand.font import Font
from wand.drawing import Drawing

lister = k7FileList.FileLister()
# 这个脚本需要从 genMuzzle.py调用

rsl_pack_exe = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Tools\\no_more_rsl\\rslPack.exe"

def extract(rpaths: list[str]):
    for rpath in rpaths:
        target_noext = os.path.join(current_dir, os.path.basename(rpath)[:-4])
        if not os.path.exists(rpath):
            print(f"只读文件不存在：{rpath}")
            raise FileNotFoundError
        with open(rpath, "rb") as fp:
            tex = stTex(fp)
            print("tex header =", tex.header)
            DDSTool.print_info(tex.dds)
            tex.dump(target_noext+".dds")
            bin_dds_img = Image(blob=tex.dds)
            bin_dds_img.format = 'png'
            bin_dds_img.save(filename=target_noext+".png")
            bin_dds_img.close()

def repack(epaths: list[str], edir: str, ersl: str, dest: str):
    for epath in epaths:
        noext = os.path.basename(epath)[:-4]
        modpng = os.path.join(current_dir, "mod", noext + ".png")
        output_dds = os.path.join(work_dir_path, noext + ".dds")
        if not os.path.exists(modpng):
            print(f"用于替换的文件不存在：{modpng}; 跳过")
            continue
        command = [
            "texconv.exe",
            "-f", "R8G8B8A8_UNORM_SRGB",  # 压缩格式 = 无
            "-ft", "dds",            # 输出文件类型
            "-srgb",                 # 输入为 sRGB，输出也为 sRGB
            "-m", "1",               # 禁用 mipmap
            "-y",                    # 覆盖输出文件（不提示）
            modpng,                  # 输入文件
        ]
        subprocess.run(command, check=True)
        print(f"\n成功重建DDS贴图: {output_dds}")
        print(f"压缩格式: None (None)")
        bin = stTex()
        fp = open(output_dds, 'rb')
        dds_bytes = fp.read()
        fp.close()
        os.remove(output_dds)
        bin.dds = dds_bytes

        bin_header = texMeta()
        bin_header.magic = b'\x00'*4
        bin_header.encoding = b'\x06\x00\x00\x00'
        bin_dds_img = Image(filename=modpng)
        width, height = bin_dds_img.size
        bin_dds_img.close()
        bin_header.w = width    # 这里不需要除以4，属于某些BIN的特例，不代表平时的不需要除以4
        bin_header.h = height   # 这里不需要除以4，属于某些BIN的特例，不代表平时的不需要除以4
        bin_header.dds_size = len(dds_bytes)
        print("bin updated header =", bin_header)

        bin.header = bin_header
        with open(epath, 'wb') as bfp:
            bin.write(bfp)
    subprocess.run([rsl_pack_exe, "--overwrite", edir], check=True)
    shutil.copyfile(ersl, dest)

def genmasked(order_name):
    # 1. 找到current_dir中的所有png
    png_files = list(current_dir.glob("*.png"))

    # 创建输出目录
    output_dir = current_dir.parent / "masked"
    print(f"找到 {len(png_files)} 个PNG文件进行处理")

    for png_file in png_files:
        # 3. 每个png进行如下处理
        try:
            with Image(filename=str(png_file)) as img:
                # 3.1 png图像是alpha的，粘贴到同等大小的黑色背景中
                # 创建黑色背景
                with Image(width=img.width, height=img.height, background=Color('black')) as bg:
                    # 将原图像合成到黑色背景上（保留alpha通道）
                    bg.composite(img, 0, 0)

                    # 3.2 将图像看作一个九宫格，中间一格（也就是5）变成纯白
                    # 计算九宫格每个区域的大小
                    cell_width = img.width // 4
                    cell_height = img.height // 4

                    # 中间区域的位置（九宫格的第5格）
                    center_x = cell_width
                    center_y = cell_height
                    center_width = cell_width * 2
                    center_height = cell_height * 2

                    # 如果图像尺寸不能被3整除，调整中间区域大小
                    # if img.width % 3 != 0:
                    #     center_width = img.width - 2 * cell_width
                    # if img.height % 3 != 0:
                    #     center_height = img.height - 2 * cell_height

                    # 在中间区域绘制白色矩形
                    with Drawing() as draw:
                        draw.fill_color = Color('white')
                        draw.rectangle(
                            left=center_x,
                            top=center_y,
                            width=center_width,
                            height=center_height
                        )
                        draw(bg)

                    # 3.3 获取其没有extension的名称，保存至masked目录
                    output_filename = output_dir / f"{png_file.stem}.png"
                    bg.save(filename=str(output_filename))

                    print(f"处理完成: {png_file.name} -> masked/{png_file.name}")

        except Exception as e:
            print(f"处理文件 {png_file.name} 时出错: {e}")

    print(f"所有文件处理完成，输出到: {output_dir}")

def run(order_info):
    # 获取当前文件夹名称（即order名称）
    order_name = order_info["name"]
    readonly_prefix = order_info["readonly_prefix"]
    extracted_prefix = order_info["extracted_prefix"]
    r_muzzles = [f"{readonly_prefix}\\{muzzle}" for muzzle in order_info["muzzles"]]
    e_muzzles = [f"{extracted_prefix}\\{muzzle}" for muzzle in order_info["muzzles"]]

    print(f"正在处理order：{order_name}")
    # print(f"只读路径: {r_muzzles}")
    # print(f"提取路径: {e_muzzles}")
    print("=" * 20)

    # extract(r_muzzles)
    # genmasked(order_name)
    repack(e_muzzles,
        order_info["extracted_dir"],
        order_info["extracted_rsl"],
        order_info["dest_pak"]
    )