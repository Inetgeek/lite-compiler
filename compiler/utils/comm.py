#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: lite-compiler
 @devtool: PyCharm
 @date: 2023/3/25
 @file: comm.py
"""
import os
import re
import json
import jsonlines


def jsonl_write(jsonl: dict, path: str):
    """
    (追加)逐行写入jsonl文件API

    :param jsonl: 需要写入的jsons，为dict
    :param path: 需要写入的jsonl文件的路径
    :return: None
    """
    with jsonlines.open(path, mode='a') as w:
        w.write(jsonl)


def jsonl_read(path: str):
    """
    逐行读取jsonl文件中json的API

    :param path: 需要读取的jsonl文件路径
    :return: json
    """
    assert os.path.exists(path), f"The {path} is not exist!"
    with jsonlines.open(path, mode='r') as r:
        for row in r:
            yield row


def get_json(file_dir: str) -> dict:
    """
    读取json文件

    :param file_dir: 需要读取的json文件所在路径
    :return: json转dict
    """
    assert os.path.exists(file_dir), f"The {file_dir} is not exist!"
    with open(file_dir, mode='r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def set_json(file_dir: str, data: dict) -> bool:
    """
    写入json文件

    :param file_dir: 需要写入的json文件所在路径
    :param data: 需要写入的数据
    :return: True or False
    """
    index = file_dir.rfind(re.findall('/', file_dir)[-1])
    os.makedirs(os.path.join(file_dir[:index]), exist_ok=True)  # 如果不存在该目录则创建一个
    with open(file_dir, mode='w', encoding='utf-8') as f:
        json.dump(data, f)
    return True


def load_all(file_dir: str) -> str:
    """
    读取文件的全部内容并返回

    :param file_dir: 需要读取的文件所在路径
    :return: 文件的全部内容
    """
    assert os.path.exists(file_dir), f"The {file_dir} is not exist!"
    with open(file_dir, mode='r', encoding='utf-8') as f:
        data = f.read()
    return data


def load_line(file_dir: str) -> str:
    """
    逐行读取文件，并返回一个生成器

    :param file_dir: 需要读取的文件所在路径
    :return: 生成器，包含文件中的每一行内容
    """
    assert os.path.exists(file_dir), f"The {file_dir} is not exist!"
    with open(file_dir, mode='r', encoding='utf-8') as f:
        for index, line in enumerate(f):
            yield index, line.rstrip()


def load_lines(file_dir: str) -> list:
    """
    读取文件的全部内容，将每一行作为列表元素返回

    :param file_dir: 需要读取的文件所在路径
    :return: 包含文件每一行内容的列表
    """
    assert os.path.exists(file_dir), f"The {file_dir} is not exist!"
    with open(file_dir, mode='r', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f]
    return lines
