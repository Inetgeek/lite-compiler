#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: lite-compiler
 @devtool: PyCharm
 @date: 2023/3/25
 @file: parse.py
"""

from .action_goto import *
from ..utils.comm import *
from ..utils.log import Log
from ..config import config as conf


class Parser(object):
    """
    语法分析器类

    """

    def __init__(self, token_table_path: str = None):
        """
        初始化语法分析器
        :param token_table_path: token表的路径
        """
        self.output = conf.dist_dir  # 输出目录
        self.token_table = token_table_path
        if self.token_table is None:
            self.token_table = f"./{conf.dist_dir}/{conf.token_table}"
            assert os.path.exists(self.token_table), f"The {self.token_table} is not exist!"
        self.log = Log(name=f'./{self.output}/{conf.log}')
        self.state_table = f'./{self.output}/{conf.state_table}'
        self.action_goto = f"./{self.output}/{conf.action_goto}"
        os.makedirs(os.path.join('.', self.output), exist_ok=True)
        os.remove(self.state_table) if os.path.exists(self.state_table) else None

        conf.global_closure_num = 0

        # 获取LR1项目集解析表
        self.LR1 = ActionGoto(file_path="./compiler/config/parse_grammar.json",
                              start_of_grammar=conf.start_of_grammar)

        # 初始化输入串
        self.input_token_list = []
        self.input_val_line_list = []
        self.error_line = 0
        self.error_token = None
        self.error_state = None
        self.is_parser_error = False

        # 构建输入串
        for token in jsonl_read(self.token_table):
            self.input_val_line_list.append(dict(token))
            if token['type'] == 'ID' or token['type'] == 'CONSTANT' or token['type'] == 'ERR':
                self.input_token_list.append(token['type'])
            else:
                self.input_token_list.append(token['val'])
        self.input_token_list.append('#')

    # 判断是否出错
    def is_error(self, state, input_token):
        """
        判断LR(1)分析是否出错

        :param state: 当前栈的状态
        :param input_token: 输入串
        :return: bool
        """
        return input_token not in self.LR1.action_list[state].keys()

    def LR1_parser(self, show=False):
        """
        LR(1)解析器

        :return: 是否成功被接受
        """
        # 状态栈
        state_stack = [0]
        # 符号栈
        token_stack = ['#']
        while True:
            state = state_stack[-1]
            input_token = self.input_token_list[0]
            # 输出当前状态
            if show:
                self.log.info(f"状态栈: {state_stack}\n符号栈: {token_stack}\n输入串: {self.input_token_list}\n\n")
            # 输出当前状态并保存到本地
            jsonl_write({"状态栈": state_stack, "符号栈": token_stack, "输入串": self.input_token_list}, path=self.state_table)

            if self.is_error(state, input_token):
                # 出错状态
                self.error_state = state
                return False

            action = self.LR1.action_list[state][input_token]

            if isinstance(action, int):
                # 移进
                state_stack.append(action)
                token_stack.append(input_token)
                self.input_token_list.pop(0)

                # 记录出错词和行
                self.error_token = self.input_val_line_list[0]['val']
                self.error_line = self.input_val_line_list[0]['line']

                self.input_val_line_list.pop(0)

            elif isinstance(action, Production):
                # 规约
                len_pop = len(action.right)
                for i in range(len_pop):
                    state_stack.pop(-1)
                    token_stack.pop(-1)

                token_stack.append(action.left)
                state_stack.append(self.LR1.goto_list[state_stack[-1]][action.left])

            elif action == 'acc':
                # 接受
                return True

    def analysis(self, show=False):
        """
        语法分析API

        :param show: 是否打印state表
        :return: None
        """
        # 进行语法分析
        self.is_parser_error = not self.LR1_parser(show)
        # 如果分析出错
        if self.is_parser_error:
            error_keys = []
            for key in self.LR1.action_list[self.error_state].keys():
                if key != '#':
                    error_keys.append(key)
            self.log.error(f"Some wrong on line {self.error_line}: {self.error_token}, maybe right in {error_keys}.")
            self.log.warning("Parser executed failed!")
        else:
            action_list, goto_list = self.LR1.get_action_goto_list()
            with open(self.action_goto, "a+", encoding="utf-8") as f:
                for action, goto in zip(action_list, goto_list):
                    print({"ACTION": str(action), "GOTO": str(goto)}, file=f)

            self.log.info("Parser executed succeed!")
