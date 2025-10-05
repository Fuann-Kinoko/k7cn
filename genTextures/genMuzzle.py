import json
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
from jmbStruct import MetaData_JA, stOneSentence, stFontParam, stTex, texStrImage, texMeta, SIChr
from jmbData import gDat_JA

from wand.image import Image
from wand.color import Color
from wand.font import Font

order_00 = {
    "name": "00",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st00J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st00J",
    "muzzles": [
        "st0000.BIN", "st0001.BIN", "st0002.BIN", "st0003.BIN",
        "st0004.BIN", "st0005.BIN", "st0006.BIN", "st0007.BIN",
        "st0008.BIN", "st0009.BIN", "st0010.BIN", "st0011.BIN",
        "st0012.BIN", "st0013.BIN",
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st00J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st00J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st00J.rsl",
}
order_01 = {
    "name": "01",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st01J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st01J",
    "muzzles": [
        "st0100.BIN", "st0101.BIN", "st0102.BIN", "st0103.BIN",
        "st0104.BIN", "st0105.BIN", "st0106.BIN", "st0107.BIN",
        "st0108.BIN", "st0109.BIN", "st0110.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st01J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st01J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st01J.rsl",
}
order_02 = {
    "name": "02",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st02J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st02J",
    "muzzles": [
        "st0200.BIN", "st0201.BIN", "st0202.BIN", "st0203.BIN",
        "st0204.BIN", "st0205.BIN", "st0206.BIN", "st0207.BIN",
        "st0208.BIN", "st0209.BIN", "st0210.BIN", "st0211.BIN",
        "st0212.BIN", "st0213.BIN", "st0214.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st02J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st02J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st02J.rsl",
}
order_03 = {
    "name": "03",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st03J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st03J",
    "muzzles": [
        "st0300.BIN", "st0301.BIN", "st0302.BIN", "st0303.BIN",
        "st0304.BIN", "st0305.BIN", "st0306.BIN", "st0307.BIN",
        "st0308.BIN", "st0309.BIN", "st0310.BIN", "st0311.BIN",
        "st0312.BIN", "st0313.BIN", "st0314.BIN", "st0315.BIN",
        "st0316.BIN", "st0317.BIN", "st0318.BIN", "st0319.BIN",
        "st0320.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st03J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st03J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st03J.rsl",
}
order_04 = {
    "name": "04",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st04J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st04J",
    "muzzles": [
        "st0400.BIN", "st0401.BIN", "st0402.BIN", "st0403.BIN",
        "st0404.BIN", "st0405.BIN", "st0406.BIN", "st0407.BIN",
        "st0408.BIN", "st0409.BIN", "st0410.BIN", "st0411.BIN",
        "st0412.BIN", "st0413.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st04J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st04J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st04J.rsl",
}
order_05 = {
    "name": "05",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st05J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st05J",
    "muzzles": [
        "st0500.BIN", "st0501.BIN", "st0502.BIN", "st0503.BIN",
        "st0504.BIN", "st0505.BIN", "st0506.BIN", "st0507.BIN",
        "st0508.BIN", "st0509.BIN", "st0510.BIN", "st0511.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st05J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st05J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st05J.rsl",
}
order_06 = {
    "name": "06",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st06J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st06J",
    "muzzles": [
        "st0600.BIN", "st0601.BIN", "st0602.BIN", "st0603.BIN",
        "st0604.BIN", "st0605.BIN", "st0606.BIN", "st0607.BIN",
        "st0608.BIN", "st0609.BIN", "st0610.BIN", "st0611.BIN",
        "st0612.BIN", "st0613.BIN", "st0614.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st06J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st06J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st06J.rsl",
}
order_07 = {
    "name": "07",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st07J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st07J",
    "muzzles": [
        "st0700.BIN", "st0701.BIN", "st0702.BIN", "st0703.BIN",
        "st0704.BIN", "st0705.BIN", "st0706.BIN", "st0707.BIN",
        "st0708.BIN", "st0709.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st07J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st07J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st07J.rsl",
}
order_08 = {
    "name": "08",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st08J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st08J",
    "muzzles": [
        "st0800.BIN", "st0801.BIN", "st0802.BIN", "st0803.BIN",
        "st0804.BIN", "st0805.BIN", "st0806.BIN", "st0807.BIN",
        "st0808.BIN", "st0809.BIN", "st0810.BIN", "st0811.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st08J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st08J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st08J.rsl",
}
order_09 = {
    "name": "09",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st09J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st09J",
    "muzzles": [
        "st0900.BIN", "st0901.BIN", "st0902.BIN", "st0903.BIN",
        "st0904.BIN", "st0905.BIN", "st0906.BIN", "st0907.BIN",
        "st0908.BIN", "st0909.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st09J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st09J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st09J.rsl",
}
order_10 = {
    "name": "10",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st10J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st10J",
    "muzzles": [
        "st1000.BIN", "st1001.BIN", "st1002.BIN", "st1003.BIN",
        "st1004.BIN", "st1005.BIN", "st1006.BIN", "st1007.BIN",
        "st1008.BIN", "st1009.BIN", "st1010.BIN", "st1011.BIN",
        "st1012.BIN", "st1013.BIN", "st1014.BIN", "st1015.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st10J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st10J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st10J.rsl",
}
order_11 = {
    "name": "11",
    "readonly_prefix":  "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\subtitle\\st11J",
    "extracted_prefix": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st11J",
    "muzzles": [
        "st1100.BIN", "st1101.BIN", "st1102.BIN", "st1103.BIN",
        "st1104.BIN", "st1105.BIN", "st1106.BIN", "st1107.BIN",
        "st1108.BIN", "st1109.BIN"
    ],
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st11J",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\subtitle\\st11J.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\subtitle\\st11J.rsl",
}
orders = [
    order_00, order_01, order_02, order_03,
    order_04, order_05, order_06, order_07,
    order_08, order_09, order_10, order_11
]

prefix = os.path.join(current_dir, "muzzle")

for idx, order in enumerate(orders):
# for idx, order in enumerate([order_00]):
    name = order["name"]
    run_script_path = os.path.join(prefix, "run.py")
    linking_run_script_path = os.path.join(prefix, name, "run.py")
    if os.path.exists(run_script_path):
        with open(run_script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        exec_env = {
            'order_info': order,
            '__file__': linking_run_script_path
        }
        # exec_env.update({
        #     'print_info': print_info
        # })
        # try:
        exec(code, exec_env)
        if 'run' in exec_env:
            result = exec_env['run'](order)
            print(f"✓ {name} 处理完成")
        # except Exception as e:
        #     print(f"处理 {name} 时发生错误: {e}")
    # # DEBUG: 先把单个搞好了
    # break