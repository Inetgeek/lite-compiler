#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: compiler
 @devtool: PyCharm
 @date: 2023/3/25
 @file: config.py
"""

# 文法开始符号
start_of_grammar = "START"
# 全局闭包数量
global_closure_num = 0
# 全局变量计数器
global_var_cnt = 0
# 全局标签计数器
global_label_cnt = 0
# 无条件跳转标签栈
global_goto_label_stack = []
# 条件跳转标签栈
global_if_goto_label_stack = []
global_while_label_stack = []
global_for_label_stack = []
global_for_operator_stack = []
# 输出目录
dist_dir = "dist"
# token表文件名
token_table = "lex_tokens.jsonl"
# state表文件名
state_table = "parse_states.jsonl"
# action及goto表文件名
action_goto = "parser_action_goto.jsonl"
# tac表文件名
tac_table = "sem_tacs.jsonl"
# 日志文件
log = "out.log"
# 语义类型list
type_list = [
    "DECLARE_INTER_START",  # 变量声明语句
    "BLOCK_STMT_EXPRESSION_START",  # 单纯的赋值语句
    "PRINT_STMT_START",  # print语句
    "RETURN_STMT_START",  # return 语句
    "IF_STMT_START",  # if-else语句
    "WHILE_STMT_START",  # while循环语句
    "DO_WHILE_STMT_START",  # do-while循环语句
    "FOR_STMT_START"  # for循环语句
]
# 运算优先级映射：“非算关与或赋”
op_map = {'=': 0, '||': 1, '&&': 2, '==': 2.5, '!=': 2.5, '<=': 2.5, '>=': 2.5, '>': 2.5, '<': 2.5, '+': 3, '-': 3,
          '*': 4, '/': 4, '%': 4}
double_op = ["+=", "-=", "++", "--"]
# 条件分支语句列表
branch_list = ['if', 'else', 'while', 'for']
