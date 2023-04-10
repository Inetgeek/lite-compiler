#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: compiler
 @devtool: PyCharm
 @date: 2023/3/25
 @file: tac.py
"""


from ..parser.parse import *
from ..config import config as conf


def gen_OP_TAC(token_list):
    """
    生成运算语句的TAC

    :return:
    """
    result, to_process_list, LRD_stack, op_stack, token_cnt = [], [], [], [], 0
    for token in token_list:
        if token['type'] == 'ID' or token['type'] == 'CONSTANT':
            LRD_stack.append(token)
        elif token['val'] in conf.op_map.keys():
            op = token
            while True:
                if len(op_stack) == 0 or op_stack[-1]['val'] == '(' or conf.op_map[op['val']] > conf.op_map[op_stack[-1]['val']]:
                    break
                LRD_stack.append(op_stack[-1])
                op_stack.pop(-1)
            op_stack.append(op)
        elif token['val'] == '(':
            op_stack.append(token)
        elif token['val'] == ')':
            while True:
                if op_stack[-1]['val'] != '(':
                    LRD_stack.append(op_stack[-1])
                    op_stack.pop(-1)
                else:
                    op_stack.pop(-1)
                    break
        elif token['val'] == '++' or token['val'] == '--':
            op = token['val'][0]
            if token_cnt == 0:
                result.append(TAC((op, token_list[token_cnt + 1]['val'], 1, "T" + str(conf.global_var_cnt))))
                result.append(TAC(('=', "T" + str(conf.global_var_cnt), '-', token_list[token_cnt + 1]['val'])))
                conf.global_var_cnt += 1
            else:
                if token_list[token_cnt + 1]['type'] == 'ID':
                    result.append(TAC((op, token_list[token_cnt + 1]['val'], 1, "T" + str(conf.global_var_cnt))))
                    result.append(TAC(('=', "T" + str(conf.global_var_cnt), '-', token_list[token_cnt + 1]['val'])))
                    conf.global_var_cnt += 1
                elif token_list[token_cnt - 1]['type'] == 'ID':
                    to_process_list.append((op, token_list[token_cnt - 1]['val'], 1))
                    to_process_list.append(('=', '-', token_list[token_cnt - 1]['val']))
        token_cnt += 1

    while True:
        if len(op_stack) == 0:
            break
        LRD_stack.append(op_stack[-1])
        op_stack.pop(-1)

    var_stack = []
    for token in LRD_stack:
        if token['type'] == 'ID' or token['type'] == 'CONSTANT':
            var_stack.append(token['val'])
        elif token['type'] == 'OP':
            var2 = var_stack[-1]
            var_stack.pop(-1)
            var1 = var_stack[-1]
            var_stack.pop(-1)
            process_var = "T" + str(conf.global_var_cnt)
            if token['val'] == '=':
                tac = TAC((token['val'], var2, '-', var1))
            else:
                tac = TAC((token['val'], var1, var2, process_var))
                conf.global_var_cnt += 1
            result.append(tac)
            var_stack.append(process_var)

    for to_process_tac in to_process_list:
        process_var = "T" + str(conf.global_var_cnt)
        if to_process_tac[0] == '=':
            tac = TAC(to_process_tac[:1] + (process_var,) + to_process_tac[1:])
            result.append(tac)
            conf.global_var_cnt += 1
        else:
            to_process_tac += (process_var,)
            result.append(TAC(to_process_tac))
    # 返回TAC语句序列和运算结果
    return result, var_stack[0]


# 生成赋值语句的TAC
def gen_BLOCK_STMT_EXPRESSION_TAC(token_list, is_declare_inter=False):
    # 如果是在变量声明时则沿用前面的后缀表达式
    # 用以区别双目运算符的赋值语句和存在双目运算符的表达式
    if is_declare_inter:
        return gen_OP_TAC(token_list)[0]

    global marked_op
    result = []
    exist_double_op = False

    for token in token_list:
        if token['val'] in conf.double_op:
            marked_op = token['val']
            exist_double_op = True
            break

    # 存在双目运算符且不是变量声明时的赋值
    if exist_double_op:
        process_var = "T" + str(conf.global_var_cnt)
        global var0
        for token in token_list:
            if token['type'] == 'ID':
                var0 = token['val']
                break
        if marked_op == '+=' or marked_op == '-=':
            result.append(TAC((marked_op[0], var0, token_list[2]['val'], process_var)))
            result.append(TAC(('=', process_var, '-', var0)))
            conf.global_var_cnt += 1
        elif marked_op == '++' or marked_op == '--':
            result.append(TAC((marked_op[0], var0, 1, process_var)))
            result.append(TAC(('=', process_var, '-', var0)))
            conf.global_var_cnt += 1

    else:
        result = gen_OP_TAC(token_list)[0]
    return result


# 生成变量声明的TAC语句
def gen_DECLARE_INTER_TAC(token_list):
    result, expression, expression_list, after_comma_list = [], [], [], []
    declare_type = token_list[0]['val']
    is_after_comma = True
    for token in token_list[1:-1]:
        if is_after_comma:
            after_comma_list.append(token)
            is_after_comma = False
        if token['val'] != ',':
            expression.append(token)
        else:
            expression_list.append(expression)
            expression = []
            is_after_comma = True
    if len(expression) != 0:
        expression_list.append(expression)
    for expression in expression_list:
        if len(expression) > 1:
            if expression[0] in after_comma_list:
                result.append(TAC((declare_type, expression[0]['val'], '-', '-')))
            for tac in gen_BLOCK_STMT_EXPRESSION_TAC(expression, is_declare_inter=True):
                result.append(tac)
        else:
            result.append(TAC((declare_type, expression[0]['val'], '-', '-')))

    return result


def gen_PRINT_STMT_TAC(token_list):
    result = []
    if len(token_list[2:]) == 1:
        result.append(TAC(('print', token_list[2]['val'], '-', '-')))
    else:
        tac_list, res = gen_OP_TAC(token_list[2:-2])
        for tac in tac_list:
            result.append(tac)
        result.append(TAC(('print', res, '-', '-')))
    return result


def gen_RETURN_STMT_TAC(token_list):
    result = []
    # 返回一个表达式的值
    if len(token_list[1:]) > 1:
        tac_list, res = gen_OP_TAC(token_list[1:])
        for tac in tac_list:
            result.append(tac)
        result.append(TAC(('return', res, '-', '-')))
    # 返回仅仅一个值
    elif len(token_list[1:]) == 1:
        result.append(TAC(('return', token_list[1]['val'], '-', '-')))
    # 返回空值
    else:
        result.append(TAC(('return', '-', '-', '-')))
    return result


def gen_IF_STMT_TAC(token_list):
    result = []
    start_pos = 2
    if token_list[0]['val'] == 'else':
        start_pos = 3
    tac_list, res = gen_OP_TAC(token_list[start_pos:-2])
    for tac in tac_list:
        result.append(tac)
    result.append(TAC(('!=', res, 'True', 0)))
    return result


def gen_WHILE_STMT_TAC(token_list):
    result = []
    conf.global_while_label_stack.append(conf.global_label_cnt)
    tac_list, res = gen_OP_TAC(token_list[2:-2])
    for tac in tac_list:
        result.append(tac)
    result.append(TAC(('!=', res, 'True', 0)))
    return result


def gen_FOR_STMT_TAC(token_list):
    result = []
    semicolon_index = []  # 分号下标
    for i in range(len(token_list)):
        if token_list[i]['val'] == ';':
            semicolon_index.append(i)
    declare_token_list = token_list[2:semicolon_index[0] + 1]
    judge_token_list = token_list[semicolon_index[0] + 1:semicolon_index[1]]
    operator_token_list = token_list[semicolon_index[1] + 1:-2]
    if len(declare_token_list) > 4:
        # 变量声明 int i = 0;这段变量声明的代码长度至少为4
        tac_list1 = gen_DECLARE_INTER_TAC(declare_token_list)
    else:
        tac_list1 = gen_BLOCK_STMT_EXPRESSION_TAC(declare_token_list)
    conf.global_for_label_stack.append(conf.global_label_cnt)
    tac_list2, res2 = gen_OP_TAC(judge_token_list)
    conf.global_for_operator_stack.append(operator_token_list)
    for tac in tac_list1 + tac_list2:
        result.append(tac)
    result.append(TAC(('!=', res2, 'True', 0)))
    return result


class TAC(object):
    """
    四元式类
    """

    def __init__(self, tac_tuple):
        self.label = conf.global_label_cnt
        conf.global_label_cnt += 1
        self.tac_tuple = [item.replace("'", '"') if isinstance(item, str) else item for item in tac_tuple]

    def __str__(self):
        return '{' + "\"label\":{},\"TAC\":{}".format(self.label, self.tac_tuple) + '}'


class MatchParser(object):
    """
    匹配解析器

    """

    def __init__(self, parser_config_file_path, token_list, start_of_grammar):
        self.error_state = None
        conf.global_closure_num = 0
        self.ag = ActionGoto(file_path=parser_config_file_path, start_of_grammar=start_of_grammar)
        # 输入串
        self.input_token_list = []
        self.input_val_line_list = []
        self.error_line = 0
        self.error_token = None

        for token in token_list:
            self.input_val_line_list.append({'val': token['val'], 'line': token['line']})
            if token['type'] == 'ID' or token['type'] == 'CONSTANT' or token['type'] == 'ERR':
                self.input_token_list.append(token['type'])
            else:
                self.input_token_list.append(token['val'])
        self.input_token_list.append('#')
        self.is_matched = self.parser()

    # 判断是否出错
    def is_error(self, state, input_token):
        return input_token not in self.ag.action_list[state].keys()

    def parser(self):
        # 状态栈
        state_stack = [0]
        # 符号栈
        token_stack = ['#']
        while True:
            state = state_stack[-1]
            input_token = self.input_token_list[0]

            # 出错
            if self.is_error(state, input_token):
                self.error_state = state
                return False

            action = self.ag.action_list[state][input_token]

            # S{action}，移进
            if type(action) == int:
                state_stack.append(action)
                token_stack.append(input_token)
                self.input_token_list.pop(0)

            # r{x}，规约
            elif type(action) == Production:
                len_pop = len(action.right)
                for i in range(len_pop):
                    state_stack.pop(-1)
                    token_stack.pop(-1)
                token_stack.append(action.left)
                state_stack.append(self.ag.goto_list[state_stack[-1]][action.left])

            # 接受
            elif action == 'acc':
                return True


class GenTAC(object):
    def __init__(self, parser_config_file_path, token_list):
        self.parser_config_file_path = parser_config_file_path
        self.token_list = token_list
        self.type = self.match_type()

    def match_type(self):

        if self.token_list[0]['val'] == 'if' \
                or self.token_list[0]['val'] == 'else' and self.token_list[1]['val'] == 'if':
            return "IF_STMT_START"

        if self.token_list[0]['val'] == 'while':
            return "WHILE_STMT_START"

        if self.token_list[0]['val'] == 'for':
            return "FOR_STMT_START"

        for start_token in conf.type_list:
            match_parser = MatchParser(parser_config_file_path=self.parser_config_file_path,
                                       token_list=self.token_list,
                                       start_of_grammar=start_token)
            if match_parser.is_matched:
                return start_token

    def gen_TAC(self):
        if self.type == 'BLOCK_STMT_EXPRESSION_START':
            return gen_BLOCK_STMT_EXPRESSION_TAC(self.token_list)
        if self.type == 'DECLARE_INTER_START':
            return gen_DECLARE_INTER_TAC(self.token_list)
        if self.type == 'PRINT_STMT_START':
            return gen_PRINT_STMT_TAC(self.token_list)
        if self.type == 'RETURN_STMT_START':
            return gen_RETURN_STMT_TAC(self.token_list)
        if self.type == 'IF_STMT_START':
            return gen_IF_STMT_TAC(self.token_list)
        if self.type == 'WHILE_STMT_START':
            return gen_WHILE_STMT_TAC(self.token_list)
        if self.type == 'FOR_STMT_START':
            return gen_FOR_STMT_TAC(self.token_list)
        return []
