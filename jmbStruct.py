from jmbDefine import gDat
from dataclasses import dataclass

import struct
import os

# 常量定义（与原始代码一致）
FILE_LENGTH = 32
JIMAKU_CHAR_MAX = 32
JIMAKU_RUBI_MAX = 10
JIMAKU_RUBI_DAT_MAX = 16
JIMAKU_LINE_MAX = 16

TEX_HEADER_SIZE = 72

def read_c_string(b):
    # 找到第一个 \x00 的位置，截断后面的内容
    null_pos = b.find(b'\x00')
    if null_pos == -1:  # 如果没有 \x00，整个字符串都是有效的（但 C 字符串通常会有 \x00）
        return b.decode('ascii', errors='ignore')
    else:
        return b[:null_pos].decode('ascii', errors='ignore')
def write_c_string(s, length):
    # 先编码成 bytes
    encoded = s.encode('ascii') if s else b''
    # 如果太长，截断（但 C 字符串需要至少 1 字节存放 \x00）
    if len(encoded) >= length:
        return encoded[:length-1] + b'\x00'  # 确保最后一个字节是 \x00
    else:
        # 填充 \x00 和 \xcd
        padding = bytes([0xCD] * (length - len(encoded) - 1))
        return encoded + b'\x00' + padding

class MetaData:
    def __init__(self, fp = None):
        self.sentence_num : int = 0                 # s16
        self.char_num : int = 0                     # s16
        self.sentence_offset : int = 0              # u32
        self.char_offset : int = 0                  # u32
        self.tex_offset : int = 0                   # u32
        self.s_motion_offset : int = 0              # u32
        self.s_motion_size_tbl : list[int] = []     # u32[]
        if fp is not None:
            self.read(fp)

    # 从文件流读取数据
    def read(self, fp):
        self.sentence_num = struct.unpack('<h', fp.read(2))[0]      # s16
        self.char_num = struct.unpack('<h', fp.read(2))[0]          # s16
        self.sentence_offset = struct.unpack('<I', fp.read(4))[0]   # u32
        self.char_offset = struct.unpack('<I', fp.read(4))[0]       # u32
        self.tex_offset = struct.unpack('<I', fp.read(4))[0]        # u32
        self.s_motion_offset = struct.unpack('<I', fp.read(4))[0]   # u32
        self.s_motion_size_tbl = list(struct.unpack(                # u32[]
            f'<{self.sentence_num}I',
            fp.read(4 * self.sentence_num)
        ))

    def write(self, fp):
        fp.write(struct.pack('<h', self.sentence_num))
        fp.write(struct.pack('<h', self.char_num))
        fp.write(struct.pack('<I', self.sentence_offset))
        fp.write(struct.pack('<I', self.char_offset))
        fp.write(struct.pack('<I', self.tex_offset))
        fp.write(struct.pack('<I', self.s_motion_offset))
        fp.write(struct.pack(f'<{self.sentence_num}I', *self.s_motion_size_tbl))

    # 序列化并保存到文件
    def dump(self, filename):
        with open(filename, 'wb') as f:
            self.write(f)

    # 从文件加载数据
    @classmethod
    def load(cls, filename):
        meta = cls()
        raise NotImplementedError("TODO")

    # 调试用：打印数据
    def __repr__(self):
        return (
            f"MetaData(sentence_num={self.sentence_num}, "
            f"char_num={self.char_num}, "
            f"sentence_offset={self.sentence_offset}, "
            f"char_offset={self.char_offset}, "
            f"tex_offset={self.tex_offset}, "
            f"s_motion_offset={self.s_motion_offset}, "
            f"s_motion_size_tbl={self.s_motion_size_tbl[:3]}...)"
        )

class stInfo:
    def __init__(self, fp = None):
        self.STRUCT_SIZE = 76
        self.wait = 0            # s32
        self.hps_file = ''       # 字符串（FILE_LENGTH字节）
        self.mth_file = ''       # 字符串（FILE_LENGTH字节）
        self.back_locate = 0     # s16
        self.countinue = 0       # s16
        self.key = 0             # s16
        self.padding = b''
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        before = fp.tell()
        self.wait = struct.unpack('<i', fp.read(4))[0]         # s32
        self.hps_file = read_c_string(fp.read(FILE_LENGTH))
        self.mth_file = read_c_string(fp.read(FILE_LENGTH))
        self.back_locate = struct.unpack('<h', fp.read(2))[0]  # s16
        self.countinue = struct.unpack('<h', fp.read(2))[0]    # s16
        self.key = struct.unpack('<h', fp.read(2))[0]          # s16
        self.padding = fp.read(2) # NOTE: 4-byte alignment padding for struct
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        fp.write(struct.pack('<i', self.wait))             # s32
        fp.write(write_c_string(self.hps_file, FILE_LENGTH))
        fp.write(write_c_string(self.mth_file, FILE_LENGTH))
        fp.write(struct.pack('<h', self.back_locate))      # s16
        fp.write(struct.pack('<h', self.countinue))        # s16
        fp.write(struct.pack('<h', self.key))              # s16
        fp.write(self.padding) # NOTE: alignment padding for struct
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)
        # print("\t\t !stInfo <-", after)

    def dump(self, filename):
        with open(filename, 'wb') as f:
            self.write(f)

    @classmethod
    def load(cls, fp):
        info = cls()
        raise NotImplementedError("TODO")

    def __repr__(self):
        return (f"stInfo(wait={self.wait}, hps_file='{self.hps_file}', "
                f"mth_file='{self.mth_file}', "
                f"back_locate={self.back_locate}, countinue={self.countinue}, key={self.key}, padding={self.padding})")

class stRubiDat:
    def __init__(self, fp=None):
        self.STRUCT_SIZE = 22
        self.from_num : int = -1                # s8
        self.to_num : int = -1                  # s8
        self.char_id : list[int] = []           # s16[JIMAKU_RUBI_MAX]
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        before = fp.tell()
        self.from_num = struct.unpack('<b', fp.read(1))[0]       # s8
        self.to_num = struct.unpack('<b', fp.read(1))[0]         # s8
        self.char_id = list(struct.unpack(
            f'<{JIMAKU_RUBI_MAX}h',
            fp.read(2 * JIMAKU_RUBI_MAX)
        ))
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        fp.write(struct.pack('<b', self.from_num))   # s8
        fp.write(struct.pack('<b', self.to_num))     # s8
        fp.write(struct.pack(
            f'<{JIMAKU_RUBI_MAX}h',
            *self.char_id
        ))
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def dump(self, fp):
        raise NotImplementedError("TODO")

    def clear(self):
        self.from_num = -1
        self.to_num = -1
        self.char_id = [-1] * JIMAKU_RUBI_MAX

    @classmethod
    def load(cls, fp):
        return cls(fp)

    def __repr__(self):
        if self.from_num != -1 and self.to_num != -1:
            valid_rubis = [num for num in self.char_id if num != -1]
            return f"fstRubiDat({self.from_num}->{self.to_num}, {valid_rubis})"
        else:
            return f""


class stJimaku:
    def __init__(self, fp = None):
        self.STRUCT_SIZE = 424
        self.wait = 0             # s32
        self.disp_time = 0        # s32
        self.char_data : list[int]  = []            # s16[JIMAKU_CHAR_MAX] (2 * 32 = 64)
        self.rubi_data : list[stRubiDat] = []       # stRubiDat[JIMAKU_RUBI_DAT_MAX] (22 * 16 = 352)
        if fp is not None:
            self.read(fp)

    def valid(self) -> bool:
        return self.char_data[0] != -1

    def read(self, fp):
        before = fp.tell()
        self.wait = struct.unpack('<i', fp.read(4))[0]          # s32
        self.disp_time = struct.unpack('<i', fp.read(4))[0]     # s32
        # 读取字符数据
        self.char_data = list(struct.unpack(
            f'<{JIMAKU_CHAR_MAX}h',
            fp.read(2 * JIMAKU_CHAR_MAX)
        ))
        # 读取注音数据
        self.rubi_data = []
        for _ in range(JIMAKU_RUBI_DAT_MAX):
            self.rubi_data.append(stRubiDat(fp))
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        fp.write(struct.pack('<i', self.wait))             # s32
        fp.write(struct.pack('<i', self.disp_time))        # s32

        # 序列化字符数据
        fp.write(struct.pack(
            f'<{JIMAKU_CHAR_MAX}h',
            *self.char_data
        ))

        # 序列化注音数据
        for rubi in self.rubi_data:
            rubi.write(fp)

        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)
        # print("\t\t !stJimaku <-", after)

    def dump(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as fp:
            # 写入wait
            fp.write(f"wait = {self.wait}\n")
            # 写入disp_time
            fp.write(f"disp_time = {self.disp_time}\n")
            # 写入char_data
            char_str = " ".join(str(c) for c in gDat.display_char_data(self.char_data))
            fp.write(f"{char_str}\n")

    @classmethod
    def load(cls, filename):
        jimaku = cls()
        with open(filename, 'r') as fp:
            lines = fp.readlines()
            assert(len(lines) == 3)

            # 解析wait
            wait_line = lines[0].strip()
            if not wait_line.startswith("wait = "):
                raise ValueError("Invalid wait line format")
            jimaku.wait = int(wait_line[7:])

            # 解析disp_time
            disp_line = lines[1].strip()
            if not disp_line.startswith("disp_time = "):
                raise ValueError("Invalid disp_time line format")
            jimaku.disp_time = int(disp_line[12:])

            # 解析char_data
            char_line = lines[2].strip()
            assert(len(char_line) < JIMAKU_CHAR_MAX)
            jimaku.char_data = [int(c) for c in char_line.split()]
            jimaku.char_data.append(-2)
            while len(jimaku.char_data) < JIMAKU_CHAR_MAX:
                jimaku.char_data.append(-1)

            # 填充空rubi
            rubis = []
            for _ in range(JIMAKU_RUBI_DAT_MAX):
                rubi = stRubiDat()
                rubi.clear()
                rubis.append(rubi)
            jimaku.rubi_data = rubis

    def __repr__(self):
        char_str = ''.join([chr(c) if c > 0 else f'[{c}]' for c in self.char_data[:8]])
        return (f"stJimaku(wait={self.wait}, disp_time={self.disp_time}, "
                f"char_data='{char_str}...', rubi_data={len(self.rubi_data)} items)")

class stOneSentence:
    def __init__(self, fp = None):
        self.STRUCT_SIZE = 6860
        self.info : stInfo = stInfo()               # stInfo对象 (76)
        self.jimaku_list : list[stJimaku] = []      # stJimaku对象列表（JIMAKU_LINE_MAX个） (16 * 424)
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        before = fp.tell()
        # 读取stInfo
        self.info.read(fp)

        # 读取stJimaku列表
        self.jimaku_list = []
        for _ in range(JIMAKU_LINE_MAX):
            jimaku = stJimaku(fp)
            self.jimaku_list.append(jimaku)
        assert(len(self.jimaku_list) == JIMAKU_LINE_MAX)
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        self.info.write(fp)
        for jimaku in self.jimaku_list:
            jimaku.write(fp)
        after = fp.tell()
        # print("\t !stOneSentence <-", after)

        assert(after - before == self.STRUCT_SIZE)

    def dump(self, filename):
        raise NotImplementedError("TODO")

    @classmethod
    def load(cls, fp):
        sentence = cls()
        raise NotImplementedError("TODO")

    def __repr__(self):
        return (f"stOneSentence(\n  info={self.info},\n  "
                f"jimaku_list=[{len(self.jimaku_list)} items])")

class stFontParam:
    def __init__(self, fp=None, *, u=0, v=0, w=0, h=0):
        self.u: int = u             # u16
        self.v: int = v             # u16
        self.w: int = w             # u16
        self.h: int = h             # u16
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        self.u, self.v, self.w, self.h = struct.unpack('<4H', fp.read(8))

    def write(self, fp):
        fp.write(struct.pack('<4H', self.u, self.v, self.w, self.h))

    def dump(self, fp):
        raise NotImplementedError("TODO")

    @classmethod
    def load(cls, fp):
        return cls(fp)

    def __repr__(self):
        return (f"stFontParam(u={self.u}, v={self.v}, w={self.w}, h={self.h})")

    def __eq__(self, other):
        if not isinstance(other, stFontParam):
            return False
        return (
            self.u == other.u and
            self.v == other.v and
            self.w == other.w and
            self.h == other.h
        )

class stTex:
    def __init__(self, fp=None):
        self.header : bytes
        self.dds : bytes
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        self.header = fp.read(TEX_HEADER_SIZE)
        self.dds = fp.read()
        assert(self.dds[:4] == b'DDS ')

    def write(self, fp):
        fp.write(self.header)
        fp.write(self.dds)

    def dump(self, filename):
        with open(filename, 'wb') as wfp:
            wfp.write(self.dds)

    @classmethod
    def load(cls, fp):
        return cls(fp)

    def __repr__(self):
        return (f"stTex : len(header) = {len(self.header)}, len(dds) = {len(self.dds)}")