from copy import copy
import io
from jmbStruct import *
import jmbConst

class gDat:
    def __init__(self):
        self.meta : MetaData
        self.sentences : list[stOneSentence]
        self.fParams : list[stFontParam]
        self.tex : stTex

        self.end_by_tex : bool

    def ready_to_write(self) -> bool:
        ready : bool = True
        ready &= self.meta != None
        ready &= self.sentences != None
        ready &= self.fParams != None
        ready &= self.tex != None
        ready &= self.end_by_tex # TODO: motion
        return ready

    def write_to_file(self, writepath:str, validation = True):
        with open(writepath, 'wb') as fp:
            self.write(fp, validation)
        print(f"已写入 {writepath}")

    def recalculate_meta(self):
        assert(self.ready_to_write())
        dummy_fp = io.BytesIO()

        # NOTE: sentence_offset 应该不会改变
        self.meta.write(dummy_fp)
        after_meta = dummy_fp.tell()
        assert(after_meta == self.meta.sentence_offset)

        # NOTE: 只要句子个数不变，对char_offset应该不存在修改
        assert(len(self.sentences) == self.meta.sentence_num)
        for sent in self.sentences:
            sent.write(dummy_fp)
        after_sent = dummy_fp.tell()
        if False:
            self.meta.char_offset = after_sent
        assert( after_sent == self.meta.char_offset)

        # NOTE: ENABLED: 对fParams的修改
        if True:
            touch = len(self.fParams)
            not_touched : bool = (self.meta.char_num == touch)
            print(f"修改meta: char_num {self.meta.char_num} -> {'[SAME]' if not_touched else touch}")
            self.meta.char_num = len(self.fParams)

        assert(len(self.fParams) == self.meta.char_num)
        for fparam in self.fParams:
            fparam.write(dummy_fp)
        after_char = dummy_fp.tell()
        # padding
        if after_char != self.meta.tex_offset:
            padding_size = 32 - (after_char % 32)
            dummy_fp.write(b'\x00' * padding_size)
            after_char = dummy_fp.tell()
        if True:
            touch = after_char
            not_touched : bool = (self.meta.tex_offset == touch)
            print(f"修改meta: tex_offset {self.meta.tex_offset} -> {'[SAME]' if not_touched else touch}")
            self.meta.tex_offset = after_char

        assert(dummy_fp.tell() == self.meta.tex_offset)
        self.tex.write(dummy_fp)

        # NOTE: ENABLED: 对s_motion_offset的修改
        assert(self.end_by_tex) # TODO: motion
        after_tex = dummy_fp.tell()
        if after_tex % 32 != 0:
            padding_size = 32 - (after_tex % 32)
            dummy_fp.write(b'\x00' * padding_size)
            after_tex = dummy_fp.tell()
        if True:
            touch = after_tex
            not_touched : bool = (self.meta.s_motion_offset == touch)
            print(f"修改meta: s_motion_offset {self.meta.s_motion_offset} -> {'[SAME]' if not_touched else touch}")
            self.meta.s_motion_offset = after_tex

        del dummy_fp

    def write(self, fp, validation = True):
        assert(self.ready_to_write())
        if validation:
            self.recalculate_meta()

        self.meta.write(fp)
        after_meta = fp.tell()
        # print("!meta <-", after_meta)
        # print("!meta", self.meta.sentence_offset)
        assert( after_meta == self.meta.sentence_offset)

        for sent in self.sentences:
            sent.write(fp)

        after_sent = fp.tell()
        # print("!sent <-", after_sent)
        # print("!sent", self.meta.char_offset)
        assert( after_sent == self.meta.char_offset)

        for fparam in self.fParams:
            fparam.write(fp)

        after_char = fp.tell()
        if after_char != self.meta.tex_offset:
            # 补全 0，直到与32 byte alignment
            padding_size = 32 - (after_char % 32)
            fp.write(b'\x00' * padding_size)
        assert(fp.tell() == self.meta.tex_offset)

        self.tex.write(fp)
        after_tex = fp.tell()
        if after_tex != self.meta.s_motion_offset:
            padding_size = 32 - (after_tex % 32)
            fp.write(b'\x00' * padding_size)
        assert(fp.tell() == self.meta.s_motion_offset)

    @staticmethod
    def display_char_data(lst: list[int]) -> list[int]:
        try:
            first_neg2_index = lst.index(-2)
        except ValueError:
            raise ValueError("no RET in char data")

        # 检查第一个-2右边的所有元素是否都是-1
        right_part = lst[first_neg2_index+1:]
        if not all(x == -1 for x in right_part):
            print("Error List:")
            print(lst)
            raise ValueError("There should be no Valid Char after RET")

        return lst[:first_neg2_index]

    def no_diff_with(self, filename: str) -> bool:
        gen_buf = io.BytesIO()
        self.write(gen_buf, validation=False)
        with open(filename, 'rb') as f_ori:
            ori_data = f_ori.read()
            gen_data = gen_buf.getvalue()
        return ori_data == gen_data

    def reimport_tex(self, filename: str):
        assert(self.end_by_tex) # TODO: motion还没有做
        old_len = len(self.tex.dds)
        with open(filename, 'rb') as fp:
            dds_bytes = fp.read()
            self.tex.dds = dds_bytes
            assert(self.tex.dds[:4] == b'DDS ')
        new_len = len(self.tex.dds)
        print(f"tex reimported from {filename} ({old_len} -> {new_len})")

    def update_sentence_ctl(self, translation: list[list[str]], char2ctl_lookup: dict[str, int], validation_mode = False):
        assert(self.meta.sentence_num == len(translation))
        for i, local_sent in enumerate(translation):
            assert(self.sentences[i].valid_jmk_num() == len(local_sent))
            for j, local_jmk in enumerate(local_sent):
                local_ctls = [char2ctl_lookup[ch] for ch in local_jmk]
                assert(len(local_ctls) < jmbConst.JIMAKU_CHAR_MAX)
                local_ctls.append(-2)
                while len(local_ctls) < jmbConst.JIMAKU_CHAR_MAX:
                    local_ctls.append(-1)
                assert(len(local_ctls) == len(self.sentences[i].jimaku_list[j].char_data))

                if validation_mode:
                    assert(self.sentences[i].jimaku_list[j].valid_len() == len(local_jmk))
                    for k, ctl in enumerate(self.sentences[i].jimaku_list[j].char_data):
                        assert(ctl == local_ctls[k])
                    print("jmk correct", local_jmk)
                else:
                    # old = copy(self.sentences[i].jimaku_list[j].char_data)
                    self.sentences[i].jimaku_list[j].overwrite_ctl(local_ctls)
                    # new = copy(self.sentences[i].jimaku_list[j].char_data)
                    # for k, old_ctl in enumerate(old):
                    #     assert(old_ctl == new[k])
                # print("ori_ctl", self.display_char_data(self.sentences[i].jimaku_list[j].char_data))
                # print("translation_ctl:", local_ctls)
