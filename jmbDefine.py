import io
from jmbStruct import *

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

        # NOTE: sentence_offset 大小不应该改变
        self.meta.write(dummy_fp)
        after_meta = dummy_fp.tell()
        assert( after_meta == self.meta.sentence_offset)

        # NOTE: DISABLED: 对char_offset的修改
        for sent in self.sentences:
            sent.write(dummy_fp)
        after_sent = dummy_fp.tell()
        if False:
            self.meta.char_offset = after_sent
        assert( after_sent == self.meta.char_offset)

        # NOTE: DISABLED: 对fParams的修改
        assert(len(self.fParams) == self.meta.char_num)
        for fparam in self.fParams:
            fparam.write(dummy_fp)
        after_char = dummy_fp.tell()
        # padding
        if after_char != self.meta.tex_offset:
            padding_size = 32 - (after_char % 32)
            dummy_fp.write(b'\x00' * padding_size)
            after_char = dummy_fp.tell()
        if False:
            self.meta.tex_offset = dummy_fp.tell()
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
            print(f"修改meta: s_motion_offset {self.meta.s_motion_offset} -> {after_tex}")
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