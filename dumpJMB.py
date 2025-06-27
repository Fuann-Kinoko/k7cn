import DDSTool
from jmbStruct import MetaData, stOneSentence, stFontParam, stTex
from jmbDefine import gDat
from copy import copy, deepcopy
import os

def read_jmb_file(filename : str) -> gDat:
    file_length : int
    jmb = gDat()
    with open(filename, 'rb') as fp:
        original_data : bytes = fp.read()
        file_length = len(original_data)

    with open(filename, 'rb') as fp:
        # 1. 读取基础头信息
        meta = MetaData(fp)

        # 2. 读取句子数据
        fp.seek(meta.sentence_offset)
        sentences : list[stOneSentence] = []
        for _ in range(meta.sentence_num):
            sentences.append(stOneSentence(fp))

        # 4. 读取字体参数 (stFontParam)
        fp.seek(meta.char_offset)
        f_params : list[stFontParam] = []
        for _ in range(meta.char_num):
            f_params.append(stFontParam(fp))

        # 5. 读取纹理数据（含对齐填充）
        fp.seek(meta.tex_offset)
        tex = stTex(fp)
        end_by_tex : bool = (file_length == meta.s_motion_offset)
        assert(end_by_tex) # TODO: 还没做

        # 6. 读取口型数据 TODO: 还没做
        if not end_by_tex:
            fp.seek(meta.s_motion_offset)
            motions = []
            for size in meta.s_motion_size_tbl:
                if size > 0:
                    motions.append(fp.read(size))
                else:
                    motions.append(b'')

        jmb.meta = meta
        jmb.sentences = sentences
        jmb.fParams = f_params
        jmb.tex = tex
        jmb.end_by_tex = end_by_tex
        return jmb

def temp_modify(jmb : gDat):
    # target = jmb.sentences[0].jimaku_list[0].char_data
    # print("==Before Modify")
    # print(target)
    # target_bytes = struct.pack(f'<{JIMAKU_CHAR_MAX}h', *target)
    # print(target_bytes)

    # print("==After Modify")
    # modified = copy(target)
    # for idx in [1, 2, 3, 4, 5]:
    #     modified[idx] = 2
    # print(modified)
    # modified_bytes = struct.pack(f'<{JIMAKU_CHAR_MAX}h', *modified)
    # print(modified_bytes)

    # jmb.sentences[0].jimaku_list[0].char_data = modified
    for i in range(jmb.meta.sentence_num):
        sent = jmb.sentences[i]
        print("+sent", i)
        print("\t info", sent.info)
        for jmk_idx, jmk in enumerate(sent.jimaku_list):
            if not jmk.valid():
                break
            print("\t char_data:", len(jmk.char_data), jmk.char_data)
            print("\t rubi_data:", len(jmk.rubi_data), jmk.rubi_data)
            jmk.dump(f"jmks/sent{i}/{jmk_idx:02d}")

    # jmb.sentences[0].jimaku_list[0].rubi_data[0].clear()
    # jmb.sentences[0].jimaku_list[0].dump("dummy.jmk")
    # print(jmb.sentences[0].jimaku_list[0].char_data)
    # jmb.sentences[0].jimaku_list[0].load("dummy.jmk")
    # print(jmb.sentences[0].jimaku_list[0].char_data)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("用法: python script.py <filename.jmb>")
        sys.exit(1)
    filename = sys.argv[1]
    if not filename.lower().endswith('.jmb'):
        print("错误: 文件必须以.jmb结尾")
        sys.exit(1)
    if not os.path.exists(filename):
        print(f"错误: 文件 '{filename}' 不存在")
        sys.exit(1)
    jmb = read_jmb_file(filename)
    print(f"解析完成")
    print(f"+setence_offset = {jmb.meta.sentence_offset}")
    print(f"+char_offset = {jmb.meta.char_offset}")
    print(f"+tex_offset = {jmb.meta.tex_offset}")
    print(f"+setence_num = {jmb.meta.sentence_num}")
    print(f"+char_num = {jmb.meta.char_num}")
    print(f"++no_motion = {jmb.end_by_tex}")

    print("\n==== Debug (fParams) ====")
    f_params = jmb.fParams
    print(f"len(f_params) = {len(f_params)}")
    # print(f_params)

    # current_u = 0
    # for i in range(jmb.meta.char_num):
    #     if i % 16 == 0:
    #         current_u = 0
    #     print(f"f_params[{i}].uvwh = {f_params[i]}") # 这个DDS中 30 是 杀, 0~15这16个构成一行
    #     # assert(current_u == f_params[i].u)
    #     step : int = 0
    #     match f_params[i].w:
    #         case 35 | 28 | 21 | 47: # kanji / katakana / numbers
    #             step = f_params[i].w + 1
    #         case _:
    #             step = f_params[i].w
    #     if (i % 16) != 15:
    #         current_u += step
    #     else:
    #         current_u += f_params[i].w
    # del current_u

    # NOTE:
    # 平假名 w=26; 片假名 w=28 ; 汉字 w=35 ; 日语的ー？这些特殊符号 w=35; 数字例如1234 w=21; 殺 w=47; 引号“” w=19;
    # DDS 本身是 1996 x 1140, /4 = 499 x 285 = 499 x (57(高度) * 5)
    # 这意味着如果f_params中h是57，那么实际在DDS中存储的，h就是57*4=228，而w也同样乘以4，只不过w会根据字的不同变化

    # print("\n==== Debug ====")
    # sent0 = jmb.sentences[0]
    # jmk0 = sent0.jimaku_list[0]
    # print("jmk0", gDat.display_char_data(jmk0.char_data)) # そこが巣だ 0, 1, 2, 3, 4; -2表示RET，-1表示空

    # jmk1 = sent0.jimaku_list[1]
    # print("jmk1", gDat.display_char_data(jmk1.char_data)) # このアパートが？ 1, 5, 6, 7, 8, 9, 2, 10; -2表示RET，-1表示空

    print("\n==== Validation ====")
    print(f"Generation Validation : {jmb.no_diff_with(filename)}")

    temp_modify(jmb)
    # jmb.write_to_file("testmod.jmb")

    # print("\n==== DDS Extraction ====")
    # DDSTool.extract("dds_font", jmb.tex.dds, jmb.fParams, should_store = True)
    # DDSTool.extract("dds_font", jmb.tex.dds, jmb.fParams, should_store = False)
    # print("\n==== DDS Reconstruction ====")
    # DDSTool.reconstruction("dds_font", "reconstruct.dds", f_params)
    # print("\n==== Reimport jmb ====")
    # jmb.reimport_tex("reconstruct.dds")
    # jmb.write_to_file("testmod.jmb")

    # print("\n==== Dump Tex ====")
    # jmb.tex.dump("tex.dds")

    # temp_modify(jmb)
    # wait_bytes = struct.pack("<i", jmk0['wait'])
    # wait_bytes = struct.pack("<f", jmk0['wait'])
    # wait_hexp = ' '.join([f'0x{byte:02x}' for byte in wait_bytes])
    # print(wait_hexp)