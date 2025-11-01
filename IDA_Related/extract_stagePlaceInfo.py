import idautils
import idc
import json
import os

def extract_shift_jis_string(ea):
    """
    从给定地址提取 Shift-JIS 编码的字符串，直到遇到 null 字节
    """
    bytes_data = bytearray()
    current_ea = ea

    while True:
        # 读取一个字节
        byte_val = idc.get_wide_byte(current_ea)
        if byte_val == 0:  # 遇到 null 字节，字符串结束
            break

        bytes_data.append(byte_val)
        current_ea += 1

    try:
        # 尝试使用 Shift-JIS 解码
        return bytes_data.decode('shift-jis')
    except UnicodeDecodeError:
        # 如果解码失败，返回原始字节的十六进制表示
        return bytes_data.hex()

def main():
    # 存储结果的字典
    result_dict = {}

    # 遍历所有符号
    for addr, name in idautils.Names():
        if name.startswith("K7StagePlaceInfo"):
            # 提取字符串
            string_value = extract_shift_jis_string(addr)
            result_dict[name] = string_value
            print(f"Found: {name} -> {string_value}")

    # 生成 JSON 文件
    output_path = "D:\\SteamLibrary\\steamapps\\common\\killer7\\Tools\\jmbDump\\genTextures\\noiseFont\\ori.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)

    print(f"\nResults saved to: {output_path}")
    print(f"Total strings extracted: {len(result_dict)}")

if __name__ == "__main__":
    main()