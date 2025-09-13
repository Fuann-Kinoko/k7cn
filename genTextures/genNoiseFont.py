from tqdm import tqdm
import io
import json
import os
from pprint import pprint
import shutil
import sys
import subprocess
from pathlib import Path
from collections import Counter

import numpy as np

current_dir = Path(__file__).parent
work_dir_path = current_dir / ".."
sys.path.append(str(work_dir_path.resolve()))

import DDSTool
import fontTool
from jmbStruct import MetaData_JA, stOneSentence, stFontParam, stTex, texStrImage, texMeta, oldGCTex
from jmbData import gDat_JA

from wand.image import Image
from wand.color import Color
from wand.font import Font

readonly_noise_kana     = "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\fonts\\noisefontkana.jmb"
extracted_noise_kana    = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\fonts\\noisefontkana.jmb"
dest_jmb = "D:\\SteamLibrary\\steamapps\\common\\killer7\\fonts\\noisefontkana.jmb"

def I4_dump(tex: oldGCTex, output_path: str):
    # blockWidth = 8, blockHeight = 8, bitsPerPixel = 4
    # so 1 byte contains 2 pixels
    width = tex.header_w
    height = tex.header_h
    blk_cnt = (width // 8) * (height // 8)
    bytes_per_blk = 32
    pixel_per_blk = 64  # blkHeight * blkWidth
    cur_blk = 0

    # 创建全零的像素数组
    px = np.zeros(width * height, dtype=np.uint8)

    for blk_y in range(0, height, 8):
        for blk_x in range(0, width, 8):
            st = cur_blk * bytes_per_blk
            ed = st + bytes_per_blk
            cur_blk += 1

            # 确保不越界
            if ed > len(tex.texture):
                print(f"block {cur_blk} is out of range, texture length = {len(tex.texture)}")
                break

            blk_bytes = tex.texture[st:ed]
            # print(f"dumping blk {cur_blk} from {st} to {ed}, bytes = {blk_bytes}")

            # 解析块中的像素
            blk_pxs = []
            for blk_byte in blk_bytes:
                # 每个字节包含2个4位像素，需要扩展到8位 (0-15 -> 0-255)
                pixel1 = ((blk_byte & 0xF0) >> 4) * 17  # 0-15 -> 0-255
                pixel2 = (blk_byte & 0x0F) * 17         # 0-15 -> 0-255
                blk_pxs.extend([pixel1, pixel2])

            # 将块像素放入正确位置
            for i in range(len(blk_pxs)):
                px_x = blk_x + (i % 8)
                px_y = blk_y + (i // 8)

                if px_x < width and px_y < height:
                    px_idx = px_y * width + px_x
                    px[px_idx] = blk_pxs[i]

    print(f"dumping to {output_path}")
    print(f"total pixels: {len(px)}, blocks processed: {cur_blk}")

    # 使用Wand创建并保存图像
    image_data = px.reshape(height, width)
    with Image(width=width, height=height, background=Color('black')) as img:
        img.type = 'grayscale'
        img.import_pixels(channel_map='I', storage='char', data=image_data.tobytes())
        img.save(filename=output_path)
        print(f"Image saved to {output_path} with size {width}x{height}")

def I4_encode(pixels, width, height) -> bytes:
    if width % 8 != 0 or height % 8 != 0:
        print(f"Warning: Image size {width}x{height} is not multiple of 8")

    img_data = np.array(pixels)
    img_data = img_data.reshape(height, width)

    # 将8位灰度压成4位 (0-255 -> 0-15)
    img_data_4bit = (img_data // 17).astype(np.uint8)  # 255/15 ≈ 17

    # 按8x8块处理
    output_bytes = bytearray()
    for blk_y in range(0, height, 8):
        for blk_x in range(0, width, 8):
            for y in range(8):
                for x in range(0, 8, 2):  # 每次处理2个像素，组合成一个byte
                    if blk_y + y < height and blk_x + x + 1 < width:
                        px1 = img_data_4bit[blk_y + y, blk_x + x]
                        px2 = img_data_4bit[blk_y + y, blk_x + x + 1]
                        combined_byte = (px1 << 4) | px2
                        output_bytes.append(combined_byte)
                    else:
                        raise Exception(f"超出边界: {blk_x + x + 1}, {blk_y + y}")
                        # 超出边界的像素用0填充
                        output_bytes.append(0)
    return output_bytes

def get_char_bitmap_from_hzk16h(char, hzk16h_path):
    try:
        gb_code = char.encode('gb2312')
    except UnicodeEncodeError:
        print(f"字符 '{char}' 无法编码为 GB2312")
        return None
    if len(gb_code) != 2:
        print(f"字符 '{char}' 不是 GB2312 编码的 2 字节字符")
        return None
    # 计算字符在字库中的位置
    zone_code = gb_code[0] - 0xA0
    bit_code = gb_code[1] - 0xA0
    offset = (94 * (zone_code - 1) + (bit_code - 1)) * 32
    # 读取点阵数据
    with open(hzk16h_path, 'rb') as f:
        f.seek(offset)
        data = f.read(32)
    # 将字节数据转换为16x16的二进制矩阵
    bitmap = np.zeros((16, 16), dtype=int)
    for i in range(16):
        line_data = data[i*2:i*2+2]
        for j in range(16):
            # 计算字节中的位位置
            byte_idx = j // 8
            bit_idx = 7 - (j % 8)
            if line_data[byte_idx] & (1 << bit_idx):
                bitmap[i, j] = 1
    return bitmap
def get_char_bitmap_from_simhei(char, font_size=16):
    try:
        from PIL import Image as PILImage, ImageDraw as PILImageDraw, ImageFont as PILImageFont
        try:
            font_path = "simhei.ttf"
            font = PILImageFont.truetype(font_path, font_size)
        except:
            raise Exception("字体文件 simhei.ttf 不存在")

        bbox = font.getbbox(char)
        if not bbox:
            bbox = (0, 0, font_size, font_size)

        image = PILImage.new('L', (font_size, font_size), 0)
        draw = PILImageDraw.Draw(image)

        # 绘制字符（使用抗锯齿）
        draw.text((0, 0), char, font=font, fill=255)

        # 转换为16x16的二进制矩阵（如果需要固定尺寸）
        # 这里只是获取原始数据，不进行缩放
        bitmap_data = np.array(image)
        bitmap = (bitmap_data > 128).astype(int)  # 阈值化，转换为 0/1

        return bitmap

    except Exception as e:
        print(f"生成字符 '{char}' 的位图时出错: {e}")
        return None
def gen_default_param(ch, cur_x, cur_y, width, height):
    return stFontParam(bigEndian=True, u=cur_x, v=cur_y, w=width, h=height)
def gen_char_image(char: str, width, height) -> Image:
    assert(len(char) == 1)

    FONT_SIZE = 16
    CANVAS_SIZE = 48
    # bitmap = get_char_bitmap_from_hzk16h(char, "C:\\Users\\yvev2\\Downloads\\HZK16C")
    bitmap = get_char_bitmap_from_hzk16h(char, "C:\\Users\\yvev2\\Downloads\\hzk16h")
    # bitmap = get_char_bitmap_from_simhei(char)
    import PIL.Image as PILImage
    import PIL.ImageDraw as PILImageDraw
    import PIL.ImageFont as PILImageFont
    final_img = PILImage.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), color=(0,0,0))
    final_draw = PILImageDraw.Draw(final_img)

    # 计算每个点的大小和间距
    seg = CANVAS_SIZE / 64

    # 绘制点阵
    if char != " ":
        if bitmap is None:
            print(f"无法获取字符 '{char}' 的点阵数据")
            raise Exception("无法获取字符的点阵数据")
        for i in range(FONT_SIZE):
            for j in range(FONT_SIZE):
                if bitmap[i, j]:
                    center_x = 2 + 4*(j-1)
                    center_y = 2 + 4*(i-1)
                    bbox = [
                        seg * (center_x+2),
                        seg * (center_y+2),
                        seg * (center_x + 4),
                        seg * (center_y + 4),
                    ]
                    final_draw.ellipse(bbox, fill=(255, 255, 255))

    # 保存图像
    # DEBUG: 保存一张就走人
    # if char == "曼":
    #     final_img.save(os.path.join("genTextures", "noiseFont", "test.png"))
    #     final_img.close()
    #     exit(1)
    img_buffer = io.BytesIO()
    final_img = final_img.resize((width, height), PILImage.Resampling.LANCZOS)
    final_img.save(img_buffer, format='PNG')

    img_blob = img_buffer.getvalue()
    final_img.close()

    img = Image(blob=img_blob)
    if char == "丘": # DEBUG: 特殊处理
        img.roll(y=3)
    img.gamma(1.27)
    img.modulate(brightness=150, saturation=100, hue=100)
    img.contrast_stretch(black_point=0.2, white_point=0.8)
    img.quantize(number_colors=5, colorspace_type='rgb', treedepth=0, dither=True)
    # img.resize(width=32, height=32, blur=0, filter='cubic')
    img.level(gamma=2.3, black=0.1, white=0.36)
    # img.gamma(2.3)
    # font_path = "TT_DotGothic12-M.ttf"
    # img.font = Font(
    #     path=font_path,
    #     color = Color('white'),
    #     size = height
    # )
    # img.gravity = 'center'
    # img.caption(text=char)
    # # OFFSET = -4
    # # img.roll(y=OFFSET)
    return img

def analyze_characters(json_data):
    all_text = ''.join(json_data.values())
    unique_chars = set()

    alphabet_digit_chars = []
    other_chars = []

    for char in all_text:
        if char in unique_chars:
            continue
        unique_chars.add(char)
        if char.isascii() and char.isalnum():
            alphabet_digit_chars.append(char)
        elif char != " ":
            other_chars.append(char)
    print(f"总唯一字符数量: {len(unique_chars)}")

    # 排序
    alphabet_digit_chars.sort()

    # 统计字符频率
    char_counter = Counter(all_text)

    if len(other_chars) > 180:
        raise Exception("汉字数量超过180个，请检查数据")

    print("\n=== 字母和数字字符 ===")
    print(f"数量: {len(alphabet_digit_chars)}")
    print(f"字符: {''.join(alphabet_digit_chars)}")

    print("\n=== 汉字+其它 ===")
    print(f"数量: {len(other_chars)}")
    print(f"汉字: {''.join(other_chars)}")
    # print("\n汉字使用频率:")
    # for char in other_chars:
    #     print(f"  '{char}': {char_counter[char]}次")

    return {
        'total_unique_chars': len(unique_chars),
        'alphabet_digit_chars': alphabet_digit_chars,
        'other_chars': other_chars,
        # 'char_frequency': dict(char_counter)
    }

def recalculate_meta(meta : MetaData_JA, sentences : list[stOneSentence], fParams : list[stFontParam], tex: oldGCTex) -> MetaData_JA:
    bigEndian = True
    dummy_fp = io.BytesIO()

    meta.write(dummy_fp)
    after_meta = dummy_fp.tell()
    assert(after_meta == meta.sentence_offset)

    # 只要句子个数不变，对char_offset应该不存在修改
    assert(len(sentences) == meta.sentence_num)
    for sent in sentences:
        sent.write(dummy_fp)
    after_sent = dummy_fp.tell()
    if True:
        touch = after_sent
        not_touched : bool = (meta.char_offset == touch)
        print(f"修改meta: char_offset {meta.char_offset} -> {'[SAME]' if not_touched else touch}")
        meta.char_offset = after_sent

    # 对fParams的修改
    if True:
        touch = len(fParams)
        not_touched : bool = (meta.char_num == touch)
        print(f"修改meta: char_num {meta.char_num} -> {'[SAME]' if not_touched else touch}")
        meta.char_num = len(fParams)

    assert(len(fParams) == meta.char_num)
    for fparam in fParams:
        fparam.write(dummy_fp)
    after_char = dummy_fp.tell()
    # padding
    if after_char != meta.tex_offset:
        padding_size = 32 - (after_char % 32)
        dummy_fp.write(b'\x00' * padding_size)
        after_char = dummy_fp.tell()
    if True:
        touch = after_char
        not_touched : bool = (meta.tex_offset == touch)
        print(f"修改meta: tex_offset {meta.tex_offset} -> {'[SAME]' if not_touched else touch}")
        meta.tex_offset = after_char

    assert(dummy_fp.tell() == meta.tex_offset)
    tex.write(dummy_fp)
    after_tex = dummy_fp.tell()
    if after_tex % 32 != 0:
        padding_size = 32 - (after_tex % 32)
        dummy_fp.write(b'\x00' * padding_size)
        after_tex = dummy_fp.tell()
    if True:
        touch = after_tex
        not_touched : bool = (meta.s_motion_offset == touch)
        print(f"修改meta: s_motion_offset {meta.s_motion_offset} -> {'[SAME]' if not_touched else touch}")
        meta.s_motion_offset = after_tex

    del dummy_fp
    return meta

def analyze(filename):
    if not os.path.exists(filename):
        print(f"错误: 文件 '{filename}' 不存在")
        sys.exit(1)
    with open(filename, 'rb') as fp:
        bigEndian = True
        meta = MetaData_JA(fp, bigEndian)
        fp.seek(meta.sentence_offset)
        print(meta)

        sentences : list[stOneSentence] = []
        for i in range(meta.sentence_num):
            sentences.append(stOneSentence(fp, bigEndian))
        jmk_num = sentences[0].valid_jmk_num()
        print(f"jmk_num: {jmk_num}")
        assert jmk_num == 1
        print(sentences[0].jimaku_list[0].char_data)
        # NOTE: 似乎只是dummy，根本不看这个的？

        fp.seek(meta.char_offset)
        fParams = []
        for _ in range(meta.char_num):
            fParams.append(stFontParam(fp, bigEndian = bigEndian))
        pprint(fParams, compact=True, indent=2)
        print(len(fParams))

        fp.seek(meta.tex_offset)
        tex = oldGCTex(fp, bigEndian)
        print(tex)

        return meta, sentences, fParams, tex

def extract():
    for filename in [readonly_noise_kana]:
        noext = os.path.basename(filename)[:-4]
        dump_path = os.path.join("genTextures", "noiseFont", noext + ".png")

        meta, sentences, fParams, tex = analyze(filename)
        I4_dump(tex, dump_path)

def pack():
    meta, sentences, fParams, tex = analyze(readonly_noise_kana)
    filename = extracted_noise_kana
    noext = os.path.basename(filename)[:-4]

    # index:
    #   当(u8)(mFont[i].str[j]) < (u8)(0x7F)时，被当做Alphabet
    #       index = mFont[i].str[j] - 0x21;
    #   else，被当作Katakana
    #       index = (u8)(mFont[i].str[j]) - (u8)(0xA6); // katakana 计算方法
    #       注意，ｦ=0xA6,ｱ=0xA7,...,浊音ﾞ单独一个=0xDE
    #       所以从0xff~0x67，再跳过不能碰的ﾞ(0xDE)和ﾟ(0xDF)我还有87个字符可以用？
    #   这肯定不够用
    #   对于Alphabet：
    #       原本:
    #           - 0x30~0x39是0~9
    #           - 0x3a~0x40是莫名其妙的字符
    #           - 0x41~0x5a是A~Z
    #           - 0x5b~0x60是又一批莫名其妙的字符
    #           - 0x61~0x7a是a~z
    #       现在：
    #           - 0x01~0x0a是0~9
    #           - 0x0b是空格
    #           - 0x12~0x2b是A~Z
    #           - 0x2c~0x45是a~z
    #   对于Katakana，0x46及以上都是了！
    #       TODO: 注意原本对浊音(0xDE)和ﾟ(0xDF)的判断，现在要取消，否则宽度会被压缩成1/3
    with open(os.path.join("genTextures", "noiseFont", "translation.json"), 'r', encoding='utf-8') as fp:
        translation = json.load(fp)
        info = analyze_characters(translation)
        hanzi = info['other_chars']

    BLOCK_HEIGHT = 48
    gCurX = 0
    # gCurY = BLOCK_HEIGHT * 3
    gCurY = 0
    gCurLineCharCnt = 0
    WIDTH_CAPACITY = 15
    canvas = Image(
        width   = 720,
        height  = BLOCK_HEIGHT * (len(hanzi)//8 + 4),
        background=Color('transparent'))
    orig_img_png = os.path.join("genTextures", "noiseFont", noext + ".png")
    mod_img_png = os.path.join("genTextures", "noiseFont", noext + "_mod.png")
    # with Image(filename=orig_img_png) as orig:
    #     canvas.composite(orig, left=0, top=0)

    fParams : list[stFontParam] = []
    # 对hanzi这个List做出改变，将' '插入进index为14的地方
    hanzi = hanzi[:14] + [' '] + hanzi[14:]
    for ch in tqdm(hanzi, desc=f"生成{noext}", unit="char"):
        if gCurLineCharCnt >= WIDTH_CAPACITY:
            gCurX = 0
            gCurY += BLOCK_HEIGHT
            gCurLineCharCnt = 0
        cParam = gen_default_param(ch, gCurX, gCurY, BLOCK_HEIGHT, BLOCK_HEIGHT)
        fParams.append(cParam)
        c_img = gen_char_image(ch, BLOCK_HEIGHT, BLOCK_HEIGHT)
        canvas.composite(c_img, left=gCurX, top=gCurY, operator='copy')
        c_img.close()
        gCurX += BLOCK_HEIGHT
        gCurLineCharCnt += 1
    width = 720
    height = gCurY + BLOCK_HEIGHT
    canvas.crop(0, 0, width=width, height=(gCurY + BLOCK_HEIGHT))
    canvas.format='png'
    canvas.save(filename=mod_img_png)
    canvas_pixels = canvas.export_pixels(channel_map='I', storage='char')

    mod_texture_bytes = I4_encode(canvas_pixels, width, height)
    tex.header_h = height
    tex.header_w = width
    tex.texture = mod_texture_bytes
    print(f"len of bytes = {len(tex.texture)}")

    meta = recalculate_meta(meta, sentences, fParams, tex)
    with open(filename, 'wb') as fp:
        meta.write(fp)
        after_meta = fp.tell()
        assert(after_meta == meta.sentence_offset)

        for sent in sentences:
            sent.write(fp)
        after_sent = fp.tell()
        assert(after_sent == meta.char_offset)

        for fparam in fParams:
            fparam.write(fp)
        after_char = fp.tell()
        if after_char != meta.tex_offset:
            # 补全 0，直到与32 byte alignment
            padding_size = 32 - (after_char % 32)
            fp.write(b'\x00' * padding_size)
        assert(fp.tell() == meta.tex_offset)

        tex.write(fp)
        after_tex = fp.tell()
        if after_tex != meta.s_motion_offset:
            padding_size = 32 - (after_tex % 32)
            fp.write(b'\x00' * padding_size)
        assert(fp.tell() == meta.s_motion_offset)
    shutil.copy2(filename, dest_jmb)

if __name__ == "__main__":
    command = input("提取图片输入y;将修改后的图片封装回去输入n (y/n): ").lower().strip()
    if command == "y":
        extract()
    elif command == "n":
        pack()
    else:
        print("invalid input")