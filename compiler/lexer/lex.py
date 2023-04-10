#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: Colyn
@project: lite-compiler
@devtool: PyCharm
@date: 2023/3/25
@file: lex.py
"""
import os
import re
from ..utils.comm import *
from ..utils.log import Log
from ..config import config as conf


class Lexer(object):
    """
    词法分析器类
    """

    def __init__(self, src_code_path: str):
        """
        初始化词法分析器

        :param src_code_path: 源码路径
        """
        self.code = load_all(file_dir=src_code_path)  # 读取源代码
        self.tokens = get_json(file_dir='./compiler/config/lex_tokens.json')  # 从JSON文件中读取词法标记
        self.tokens_values = tuple(self.tokens.values())  # 将正则文法转换为元组
        self.grammar = get_json(file_dir='./compiler/config/lex_grammar.json')  # 从JSON文件中读取词法规则
        self.output = conf.dist_dir  # 输出目录
        self.log = Log(name=f'./{self.output}/{conf.log}')
        os.makedirs(os.path.join('.', self.output), exist_ok=True)
        os.remove(f'./{self.output}/{conf.token_table}') if os.path.exists(
            f'./{self.output}/{conf.token_table}') else None

    def is_keyword(self, token) -> bool:
        """
        判断token是否为关键字

        :param token: token
        :return: bool
        """
        nfa = self.grammar["KEY_WORD"]  # 获取关键字的NFA
        return token in nfa  # 判断token是否为关键字

    def is_operator(self, token) -> bool:
        """
        判断token是否为运算符

        :param token: token
        :return: bool
        """
        nfa = self.grammar["OP"]  # 获取运算符的NFA
        return token in nfa  # 判断token是否为运算符

    def is_delimiter(self, token) -> bool:
        """
        判断token是否为分隔符

        :param token: token
        :return: bool
        """
        nfa = self.grammar["SYMBOL"]  # 获取分隔符的NFA
        return token in nfa  # 判断token是否为分隔符

    def is_identifier(self, token) -> bool:
        """
        判断token是否为标识符

        :param token: token
        :return: bool
        """
        nfa = self.grammar["ID"]  # 获取标识符的NFA
        return re.match(nfa, token) is not None  # 判断token是否为标识符

    def is_constant(self, token) -> bool:
        """
        判断token是否为常量

        :param token: token
        :return: bool
        """
        nfa = self.grammar["CONSTANT"]
        return re.match(nfa, token) is not None  # 判断token是否为常量
        # 判断token是否为常量

    def nfa_to_nfa(self):
        """
        NFA确定化为DFA

        :return: DFA
        """
        nfa = '|'.join(self.tokens_values)
        dfa = re.compile(nfa)
        return dfa

    def tokenize(self, text: str):
        """
        分词器

        :param text: 需要分词的源码文本
        :return: tokenizer
        """
        src_code = text.split('\n')
        cls_code_lines, tokenizer = [], []
        # 过滤单行注释及多行注释
        for index, line in enumerate(src_code):
            cls_code_line = line.strip()
            if cls_code_line and not re.match(r'^//', cls_code_line) and not re.match(r'^/\*',
                                                                                      cls_code_line) and not re.match(
                    r'^\*/', cls_code_line):
                cls_code_lines.append((index + 1, cls_code_line))
        # 分词
        for index, line in cls_code_lines:
            tokens = self.nfa_to_nfa().findall(line)
            # yield line, tokens
            tokenizer.append((index, tokens))
        return tokenizer

    def analysis(self, show: bool = False):
        """
        词法分析API
        :param show: 是否打印token表
        :return: None
        """
        tokens = []  # 初始化一个空列表，用于存储识别到的 tokens
        # 遍历源代码的每一行，同时获取行号
        err_cnt = 0  # 记录词法错误的次数
        for line_num, line in self.tokenize(self.code):
            for token in line:
                token_type = None  # 初始化 token 类型为 None
                token_value = token  # 将 token 值设置为匹配到的 token
                # 检查 token 是否为关键字
                if self.is_keyword(token):
                    token_type = 'KEYWORD'
                # 检查 token 是否为操作符
                elif self.is_operator(token):
                    token_type = 'OP'
                # 检查 token 是否为分隔符
                elif self.is_delimiter(token):
                    token_type = 'SYMBOL'
                # 检查 token 常量否合法
                elif re.match(r'[-+]?[0-9]*\.?[0-9]+[eE][-+]?[0-9]*\.[0-9]+', token):
                    self.log.error(f'Token at line {line_num}: {token}, Sci notation\'s exponent can\'t be a decimal')
                    token_type = 'ERR'
                    err_cnt += 1
                # 检查 token 标识符是否合法
                elif re.match(r'^\d(?!\d*$)\w+$', token):
                    self.log.error(f'Token at line {line_num}: {token}, the head of identifier can\'t be a num.')
                    token_type = 'ERR'
                    err_cnt += 1
                # 检查 token 是否为标识符
                elif self.is_identifier(token):
                    token_type = 'ID'
                # 检查 token 是否为常量
                elif self.is_constant(token):
                    token_type = 'CONSTANT'

                else:
                    # 如果 token 不属于上述任何一类，抛出 ValueError 异常
                    self.log.error(f'Invalid token at line {line_num}: {token}')
                    token_type = 'ERR'
                    err_cnt += 1

                if err_cnt > 1:
                    break
                # 将识别到的 token（包括行号、类型和值）添加到 tokens 列表中
                tokens.append((line_num, token_type, token_value))
                # 写入到输出文件
                jsonl_write(jsonl={'val': token_value, 'type': token_type, 'line': line_num},
                            path=f'./{self.output}/lex_tokens.jsonl')
                err_cnt += 1 if err_cnt == 1 else 0

        if show:
            for token in tokens:
                self.log.debug(token)
        if err_cnt == 0:
            self.log.info("Lexer executed succeed!")
        else:
            self.log.warning("Lexer executed failed!")
