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

def print_info(st: texStrImage):
    print(st.header)
    for i in range(st.header.strPackNum):
        print(st.strpack[i])
    for i in range(st.header.strNum):
        print(st.str[i])
    for i in range(st.header.chrNum):
        print(f"[{i}] {st.chb[i]}")
    print(f"{st.tex.header.w=}, {st.tex.header.h=}, {st.tex.header.dds_size=}")
    print(f"{len(st.tex.dds)=}")
    print(st.tex.header)
    print("="*20)

Map_00_Cel = {
    "name": "00_Cel",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapCelJ\\map_CelJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapCelJ\\map_CelJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapCelJ\\NameSelJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapCelJ\\NameSelJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapCelJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapCelJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapCelJ.pak",
}
Map_10_Fuk = {
    "name": "10_Fuk",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapFukJ\\map_FukJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapFukJ\\map_FukJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapFukJ\\Name_FukJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapFukJ\\Name_FukJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapFukJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapFukJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapFukJ.pak",
}
Map_11_Kak = {
    "name": "11_Kak",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapKakJ\\map_KakJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapKakJ\\map_KakJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapKakJ\\Name_KakuJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapKakJ\\Name_KakuJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapKakJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapKakJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapKakJ.pak",
}
Map_20_Txs = {
    "name": "20_Txs",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapTxsJ\\map_TxsJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapTxsJ\\map_TxsJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapTxsJ\\Name_TxsJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapTxsJ\\Name_TxsJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapTxsJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapTxsJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapTxsJ.pak",
}
Map_30_Isz = {
    "name": "30_Isz",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapIszJ\\map_IszJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapIszJ\\map_IszJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapIszJ\\Name_IszJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapIszJ\\Name_IszJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapIszJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapIszJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapIszJ.pak",
}
Map_31_Kur = {
    "name": "31_Kur",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapKurJ\\map_CurJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapKurJ\\map_CurJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapKurJ\\Name_KurJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapKurJ\\Name_KurJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapKurJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapKurJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapKurJ.pak",
}
Map_40_Dmi = {
    "name": "40_Dmi",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapDmiJ\\map_DmiJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapDmiJ\\map_DmiJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapDmiJ\\Name_dmiJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapDmiJ\\Name_dmiJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapDmiJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapDmiJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapDmiJ.pak",
}
Map_50_HTl = {
    "name": "50_HTl",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapHTlJ\\map_HTJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapHTlJ\\map_HTJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapHTlJ\\Name_HtlJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapHTlJ\\Name_HtlJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapHTlJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapHTlJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapHTlJ.pak",
}
Map_51_Scl = {
    "name": "51_Scl",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapSclJ\\map_SclJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapSclJ\\map_SclJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapSclJ\\Name_SclJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapSclJ\\Name_SclJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapSclJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapSclJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapSclJ.pak",
}
Map_60_Sen = {
    "name": "60_Sen",
    "readonly_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapSenJ\\map_SenJ.sti",
    "extracted_sti": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapSenJ\\map_SenJ.sti",
    "readonly_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\ReadOnly\\Texture\\mapSenJ\\Name_senJ.BIN",
    "extracted_mapname": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapSenJ\\Name_senJ.BIN",
    "extracted_dir": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapSenJ",
    "extracted_rsl": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Extracted\\Texture\\mapSenJ.rsl",
    "dest_pak": "D:\\SteamLibrary\\steamapps\\common\\killer7\\Texture\\mapSenJ.pak",
}
maps = [Map_00_Cel, Map_10_Fuk, Map_11_Kak, Map_20_Txs, Map_30_Isz, Map_31_Kur, Map_40_Dmi, Map_50_HTl, Map_51_Scl, Map_60_Sen]

prefix = os.path.join(current_dir, "map")

for idx, map in enumerate(maps):
# for idx, map in enumerate([maps[0]]):
# for idx, map in enumerate(maps[3:5]):
    name = map["name"]
    run_script_path = os.path.join(prefix, "run.py")
    linking_run_script_path = os.path.join(prefix, name, "run.py")
    if os.path.exists(run_script_path):
        with open(run_script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        exec_env = {
            'map_data': map,
            '__file__': linking_run_script_path
        }
        exec_env.update({
            'print_info': print_info
        })
        # try:
        exec(code, exec_env)
        if 'run' in exec_env:
            result = exec_env['run'](map)
            print(f"✓ {name} 处理完成")
        # except Exception as e:
        #     print(f"处理 {name} 时发生错误: {e}")
    # # DEBUG: 先把单个搞好了
    # break