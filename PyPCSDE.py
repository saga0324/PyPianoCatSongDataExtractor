# -*- coding: utf-8 -*-
# Py Piano Cat Song Data Extractor (PyPCSDE)
# (C) whc2001 and Yuu
# Version 2024.V1

import os
import struct
from typing import List, Tuple

Encoding = 'gbk'
key = None

def getKey(file_data: bytes) -> bytes:
    key_a = file_data[1024:1024+32]
    key_b = file_data[1056:1056+32]
    ret = bytearray(32)
    for i in range(32):
        ret[i] = (key_b[i] - key_a[i]) % 256
    return ret


def getDir(file_data: bytes) -> List[Tuple[str, int, int]]:
    ret = []
    dir_num = struct.unpack('I', file_data[252:256])[0]
    for i in range(dir_num):
        offset = 1280 + i * 128
        item = bytearray(file_data[offset:offset+128])
        for j in range(len(item)):
            item[j] = (item[j] - key[j % 32]) % 256
        dir_name = item[:120].decode(Encoding).rstrip('\x00')
        dir_data_length = struct.unpack('I', item[120:124])[0] << 7
        dir_data_offset = struct.unpack('I', item[124:128])[0]
        ret.append((dir_name, dir_data_length, dir_data_offset))
    return ret


def getFile(file_data: bytes, dir_data_offset: int, dir_data_length: int) -> List[Tuple[str, int, int]]:
    ret = []
    for i in range(dir_data_length // 128):
        offset = dir_data_offset + i * 128
        item = bytearray(file_data[offset:offset+128])
        for j in range(len(item)):
            item[j] = (item[j] - key[j % 32]) % 256
        file_name = item[:64].decode(Encoding).rstrip('\x00')
        song_data_offset = struct.unpack('I', item[64:68])[0]
        song_data_length = struct.unpack('I', item[68:72])[0]
        ret.append((file_name, song_data_offset, song_data_length))
    return ret


def getSong(file_data: bytes, song_data_offset: int, song_data_length: int) -> bytes:
    return file_data[song_data_offset:song_data_offset+song_data_length]

def main(input_path: str, output_path: str):
    global key
    if not os.path.exists(input_path):
        print(f"File Not Found in {input_path}")
        exit(1)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with open(input_path, 'rb') as f:
        data = f.read()
    key = getKey(data)
    dirs = getDir(data)
    for dir_name, dir_data_length, dir_data_offset in dirs:
        dir_path = os.path.join(output_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        songs = getFile(data, dir_data_offset, dir_data_length)
        for file_name, song_data_offset, song_data_length in songs:
            print(f"{dir_name} -> {file_name}")
            song_data = getSong(data, song_data_offset, song_data_length)
            with open(os.path.join(dir_path, f"{file_name}.mid"), 'wb') as f:
                f.write(song_data)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: PyPCSDE.py <INPUT_FILE> <OUTPUT_FOLDER>")
        exit(1)
    main(sys.argv[1], sys.argv[2])
