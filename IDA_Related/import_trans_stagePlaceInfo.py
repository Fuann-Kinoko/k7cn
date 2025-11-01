import idautils
import idc
import json

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
    # print(f"总唯一字符数量: {len(unique_chars)}")

    # 排序
    alphabet_digit_chars.sort()

    print("\n=== 字母和数字字符 ===")
    print(f"数量: {len(alphabet_digit_chars)}")
    print(f"字符: {''.join(alphabet_digit_chars)}")

    print("\n=== 汉字+其它 ===")
    print(f"数量: {len(other_chars)}")
    print(f"汉字: {''.join(other_chars)}")
    print("\n汉字使用频率:")

    return {
        'total_unique_chars': len(unique_chars),
        'alphabet_digit_chars': alphabet_digit_chars,
        'other_chars': other_chars,
    }

def encode_custom_string(s, hanzi):
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
            assert char in hanzi, f"不支持的字符: {char}"
            index = hanzi.index(char)
            if index >= 14:
                index += 1 # 因为14由特殊原因被空白占据，因此之后的需要序号+1
            encoded_byte = index + 0x46
            # code_point = char.encode('shift_jis')
            # assert b'\x61' <= code_point <= b'\xDF', f"不支持的字符: {char} (Shift-JIS-{code_point.hex()})"
            # encoded_byte = code_point[0] - 0x60
        if encoded_byte is None:
            raise ValueError(f"不支持的字符: {char}")
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

    info = analyze_characters(string_dict)
    hanzi:list[str] = info['other_chars']
    hanzi_dict = {char: index for index, char in enumerate(hanzi)}
    # 遍历所有符号
    for addr, name in idautils.Names():
        # 只处理以"K7StagePlaceInfo_"开头并以"_JP"结尾的symbol
        if name.startswith("K7StagePlaceInfo_") and (name.endswith("_JP") or name.endswith("_EN")):
            if name in string_dict:
                new_string = string_dict[name]
                print(f"Processing: {name} -> {new_string}")

                try:
                    # 编码字符串
                    encoded_bytes = encode_custom_string(new_string, hanzi)

                    # 获取原数据长度（直到null字节）
                    current_ea = addr
                    original_length = 0
                    while idc.get_wide_byte(current_ea) != 0:
                        original_length += 1
                        current_ea += 1

                    # 检查新编码的字符串是否会超出原空间
                    if len(encoded_bytes) > original_length:
                        print(f"Warning: 字符串 '{new_string}' 长度超过原空间，将被截断")
                        encoded_bytes = encoded_bytes[:original_length]

                    # 写回数据
                    for i, byte_val in enumerate(encoded_bytes):
                        idc.patch_byte(addr + i, byte_val)

                    # 确保字符串以null终止
                    if len(encoded_bytes) < original_length:
                        idc.patch_byte(addr + len(encoded_bytes), 0)

                    name_codes = [int(byte_val) for byte_val in encoded_bytes]
                    print(f"成功写入: {name} ({name_codes})")

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
    json_path = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Tools\\jmbDump\\genTextures\\noiseFont\\translation.json"
    write_custom_strings_to_ida(json_path)


