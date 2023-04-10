#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: compiler
 @devtool: PyCharm
 @date: 2023/3/25
 @file: semantic.py
"""
from .tac import *
from ..utils.log import Log
from ..utils.comm import *


class Semantic:
    """
    语义分析类
    """

    def __init__(self, token_table_path: str = None):
        """
        初始化语义分析器
        :param token_table_path: token表的路径
        """
        self.tac_list = None
        self.line_list = []
        self.each_line = []
        self.output = conf.dist_dir  # 输出目录
        self.tac_table = f"./{conf.dist_dir}/{conf.tac_table}"
        self.token_table = token_table_path
        if self.token_table is None:
            self.token_table = f"./{conf.dist_dir}/{conf.token_table}"
            assert os.path.exists(self.token_table), f"The {self.token_table} is not exist!"
        self.log = Log(name=f'./{self.output}/{conf.log}')
        os.makedirs(os.path.join('.', self.output), exist_ok=True)
        os.remove(self.tac_table) if os.path.exists(self.tac_table) else None

        is_for_stmt = False
        for token in jsonl_read(self.token_table):
            self.each_line.append(token)
            if token['val'] == 'for':
                is_for_stmt = True
            if is_for_stmt:
                if token['val'] == '{' or token['val'] == '}':
                    self.line_list.append(self.each_line)
                    self.each_line = []
                    is_for_stmt = False
            else:
                if token['val'] == ';' or token['val'] == '{' or token['val'] == '}':
                    self.line_list.append(self.each_line)
                    self.each_line = []

    def TAC_parser(self):
        branch_list = conf.branch_list
        branch_state_stack = [self.line_list[0][0]['val']]
        tac_list = []

        for line in self.line_list:
            gen_tac = GenTAC(parser_config_file_path="./compiler/config/sem_grammar.json", token_list=line)
            gen_tac_list = gen_tac.gen_TAC()
            for tac in gen_tac_list:
                tac_list.append(tac)
            if line[0]['val'] in branch_list:
                if line[0]['val'] == 'if':
                    branch_state_stack.append('if')
                    conf.global_if_goto_label_stack.append(conf.global_label_cnt - 1)
                elif line[0]['val'] == 'else':
                    if line[1]['val'] == 'if':
                        branch_state_stack.append('elif')
                        conf.global_if_goto_label_stack.append(conf.global_label_cnt - 1)
                    else:
                        branch_state_stack.append('else')
                elif line[0]['val'] == 'for':
                    branch_state_stack.append('for')

                elif line[0]['val'] == 'while':
                    branch_state_stack.append('while')

            elif line[0]['val'] == '}':
                if branch_state_stack[-1] == 'if':
                    branch_state_stack.pop(-1)
                    tac_list[conf.global_if_goto_label_stack[-1]].tac_tuple[3] = conf.global_label_cnt + 1
                    conf.global_if_goto_label_stack.pop(-1)
                    conf.global_goto_label_stack.append([conf.global_label_cnt])
                    tac_list.append(TAC(("goto", "-", "-", conf.global_label_cnt + 1)))  # 若没有else语句则默认跳转下一条语句

                elif branch_state_stack[-1] == 'elif':
                    branch_state_stack.pop(-1)
                    tac_list[conf.global_if_goto_label_stack[-1]].tac_tuple[3] = conf.global_label_cnt + 1
                    conf.global_if_goto_label_stack.pop(-1)
                    conf.global_goto_label_stack[-1].append(conf.global_label_cnt)
                    tac_list.append(TAC(("goto", "-", "-", conf.global_label_cnt + 1)))  # 若没有else语句则默认跳转下一条语句

                elif branch_state_stack[-1] == 'else':
                    branch_state_stack.pop(-1)
                    for label in conf.global_goto_label_stack[-1]:
                        tac_list[label].tac_tuple[3] = conf.global_label_cnt
                    conf.global_goto_label_stack.pop(-1)

                elif branch_state_stack[-1] == 'while':
                    branch_state_stack.pop(-1)
                    tac_list[conf.global_while_label_stack[-1] + 1].tac_tuple[3] = conf.global_label_cnt + 1
                    tac_list.append(TAC(("goto", "-", "-", conf.global_while_label_stack[-1])))
                    conf.global_while_label_stack.pop(-1)

                elif branch_state_stack[-1] == 'for':
                    branch_state_stack.pop(-1)
                    tac_list += gen_BLOCK_STMT_EXPRESSION_TAC(conf.global_for_operator_stack[-1])
                    conf.global_for_operator_stack.pop(-1)
                    tac_list[conf.global_for_label_stack[-1] + 1].tac_tuple[3] = conf.global_label_cnt + 1
                    tac_list.append(TAC(("goto", "-", "-", conf.global_for_label_stack[-1])))
                    conf.global_for_label_stack.pop(-1)

                else:
                    tac_list.append(TAC(("end", "-", "-", "-")))

        return tac_list

    def analysis(self, show=False):
        self.log.info("Please wait a moment...")
        self.tac_list = self.TAC_parser()
        with open(self.tac_table, "a+", encoding="utf-8") as f:
            for tac in self.tac_list:
                print(tac, file=f)
                if show:
                    self.log.debug(tac)
        self.log.info("Semantic Analyzer executed succeed!")
