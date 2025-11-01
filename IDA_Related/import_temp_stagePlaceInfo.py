import idautils
import idc
import json

def encode_custom_string(s):
    """
    将字符串按照自定义编码规则编码为字节序列
    """
    encoded_bytes = bytearray()

    for char in s:
        # ASCII 字符处理
        encoded_byte = None
        if '0' <= char <= '9':
            encoded_byte = 0x01 + (ord(char) - ord('0'))
        elif char == ' ':
            encoded_byte = 0x0B
        elif 'A' <= char <= 'Z':
            encoded_byte = 0x12 + (ord(char) - ord('A'))
        elif 'a' <= char <= 'z':
            encoded_byte = 0x2C + (ord(char) - ord('a'))
        else:
            code_point = char.encode('shift_jis')
            assert b'\x61' <= code_point <= b'\xDF', f"不支持的字符: {char} (Shift-JIS-{code_point.hex()})"
            encoded_byte = code_point[0] - 0x60
        if encoded_byte is None:
            raise ValueError(f"不支持的字符: {char} (U+{code_point:04X})")
        else:
            encoded_bytes.append(encoded_byte)

    return encoded_bytes

def write_custom_strings_to_ida(json_path):
    """
    从JSON文件读取字符串并写回IDA中的对应符号地址
    """
    # 读取JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        string_dict = json.load(f)

    # 遍历所有符号
    for addr, name in idautils.Names():
        # 只处理以"K7StagePlaceInfo_"开头并以"_JP"结尾的symbol
        if name.startswith("K7StagePlaceInfo_") and (name.endswith("_JP") or name.endswith("_EN")):
            if name in string_dict:
                new_string = string_dict[name]
                print(f"Processing: {name} -> {new_string}")

                try:
                    # 编码字符串
                    encoded_bytes = encode_custom_string(new_string)

                    # 获取原数据长度（直到null字节）
                    current_ea = addr
                    original_length = 0
                    while idc.get_wide_byte(current_ea) != 0:
                        original_length += 1
                        current_ea += 1

                    # 检查新编码的字符串是否会超出原空间
                    if len(encoded_bytes) > original_length:
                        print(f"警告: 字符串 '{new_string}' 长度超过原空间，将被截断")
                        encoded_bytes = encoded_bytes[:original_length]

                    # 写回数据
                    for i, byte_val in enumerate(encoded_bytes):
                        idc.patch_byte(addr + i, byte_val)

                    # 确保字符串以null终止
                    if len(encoded_bytes) < original_length:
                        idc.patch_byte(addr + len(encoded_bytes), 0)

                    print(f"成功写入: {name}")

                except Exception as e:
                    print(f"处理 {name} 时出错: {str(e)}")
            else:
                print(f"跳过: {name} (不在JSON文件中)")
        else:
            # 可选：显示跳过的符号（调试用）
            # print(f"跳过: {name} (不符合命名规则)")
            pass

    print("所有字符串已处理完毕")

if __name__ == "__main__":
    json_path = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Tools\\jmbDump\\genTextures\\noiseFont\\temp.json"
    write_custom_strings_to_ida(json_path)