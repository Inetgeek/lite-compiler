#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: compiler
 @devtool: PyCharm
 @date: 2023/3/25
 @file: action_goto.py
"""
from ..utils.comm import *
from ..config import config as conf
from .attrib import AttributesExtend


class Production:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right

    def __str__(self):
        return self.left + " -> " + str(self.right)


class ProductionItem:
    def __init__(self, production, index=0, forward=None):
        if forward is None:
            forward = {'#'}
        # 产生式
        self.production = production
        # 向前看的单词的位置
        self.index = index
        # 向前搜索符
        self.forward = forward

    def __eq__(self, other):
        if self.index != other.index:
            return False
        if self.forward != other.forward:
            return False
        if self.production != other.production:
            return False
        return True

    def __str__(self):
        return str(self.production) + "," + str(self.forward) + ", index=" + str(self.index)


class Closure:
    def __init__(self):
        # 定义静态全局变量
        self.id = conf.global_closure_num
        self.item_list = []
        self.shift_closure = {}

    def add_item(self, item):
        self.item_list.append(item)

    def __eq__(self, other):
        if self.item_list == other.item_list:
            return True
        if len(self.item_list) != len(other.item_list):
            return False
        flag = True
        for item in self.item_list:
            if item not in other.item_list:
                flag = False
                break
        return flag

    def __str__(self):
        res = ""
        for pro in self.item_list:
            res += str(pro) + "\n"

        return res


class DFA:
    def __init__(self, file_path, start_of_grammar):
        self.attributes = AttributesExtend(file_path)
        self.production_list = self.get_production_list()
        self.production_map = self.get_production_map()
        self.start_of_grammar = start_of_grammar
        self.closure_list = []
        self.get_closure_list()

    def get_production_list(self):
        production_list = []
        for pro in self.attributes.production_list:
            production = Production(left=pro['left'], right=pro['right'])
            production_list.append(production)
        return production_list

    def get_production_map(self):
        production_map = {}
        for left in self.attributes.production_map.keys():
            production_list = []
            for right in self.attributes.production_map[left]:
                production_list.append(Production(left=left, right=right))
            production_map[left] = production_list
        return production_map

    # item_set是Closure类型的
    def get_closure(self, closure):
        for tmp in closure.item_list:
            if tmp.index == len(tmp.production.right) - 1:
                # 点 后面只有一个符号 是否是非终结符
                may_left = tmp.production.right[tmp.index]
                # 是 非终结符
                if may_left in self.attributes.nonTerminator_list:
                    for production in self.production_map[may_left]:
                        closure1 = ProductionItem(production=production, index=0, forward=tmp.forward)
                        if closure1 not in closure.item_list:
                            closure.item_list.append(closure1)
            elif tmp.index < len(tmp.production.right) - 1:
                # 点 后面有超过一个符号 是否为非终结符
                may_left = tmp.production.right[tmp.index]
                # 是 非终结符
                if may_left in self.attributes.nonTerminator_list:
                    forward1 = set([])
                    is_all_space = True
                    for token in tmp.production.right[tmp.index + 1:]:
                        if token not in self.attributes.space_nonTerminator:
                            is_all_space = False
                            forward1 |= self.attributes.first_set_map[token]
                            break
                        forward1 |= self.attributes.first_set_map[token]
                    if is_all_space:
                        forward1 |= tmp.forward
                    for production in self.production_map[may_left]:
                        closure1 = ProductionItem(production=production, index=0, forward=forward1)
                        if closure1 not in closure.item_list:
                            closure.item_list.append(closure1)

    # item_set是Closure类型的
    def search_forward(self, closure):
        s_map = {}
        keys = []
        # tmp是当前产生式项目
        for tmp in closure.item_list:
            # 如果tmp不是规约项目而是移进项目
            if tmp.index < len(tmp.production.right):
                # ss是要被移进的字符
                ss = tmp.production.right[tmp.index]
                # 如果移进ss已经被执行
                if ss in s_map.keys():
                    # 在ss的已移进项目集中添加当前被移进项目
                    closure1 = s_map[ss]
                    closure1.add_item(
                        ProductionItem(production=tmp.production, index=tmp.index + 1, forward=tmp.forward))
                else:
                    # 否则产生新项目集
                    closure1 = Closure()
                    # 新项目集中加入当前被移进项目
                    closure1.add_item(
                        ProductionItem(production=tmp.production, index=tmp.index + 1, forward=tmp.forward))
                    # 添加映射
                    s_map[ss] = closure1
                    keys.append(ss)
        # 解决冲突重复问题
        for key in keys:
            # 各自建完整项目集
            closure1 = s_map[key]
            self.get_closure(s_map[key])
            # 如果已经存在
            if closure1 in self.closure_list:
                ind = self.closure_list.index(closure1)
                closure.shift_closure[key] = ind
            else:
                conf.global_closure_num += 1
                closure1.id = conf.global_closure_num
                closure.shift_closure[key] = closure1.id
                self.closure_list.append(closure1)

    def get_closure_list(self):
        # 增广文法中产生式开始符对应的产生式只有一条，取出之
        start_production = self.production_map[self.start_of_grammar][0]
        start_item = Closure()
        self.closure_list.append(start_item)
        start_item.add_item(ProductionItem(start_production))
        cnt = 0
        while True:
            self.get_closure(self.closure_list[cnt])
            self.search_forward(self.closure_list[cnt])
            cnt += 1
            num = len(self.closure_list)
            if cnt == num:
                break


class ActionGoto:
    def __init__(self, file_path, start_of_grammar):
        self.dfa = DFA(file_path=file_path, start_of_grammar=start_of_grammar)
        self.action_list, self.goto_list = self.get_action_goto_list()

    def get_action_goto_list(self):
        action_list = []
        goto_list = []
        for item_set in self.dfa.closure_list:
            action_dict = {}
            goto_dict = {}
            # 移进项目
            for key in item_set.shift_closure.keys():
                if key in self.dfa.attributes.terminator_list:
                    action_dict[key] = item_set.shift_closure[key]
                else:
                    goto_dict[key] = item_set.shift_closure[key]
            # 规约项目
            for production_item in item_set.item_list:
                if production_item.index == len(production_item.production.right):
                    for token in production_item.forward:
                        action_dict[token] = production_item.production
            action_list.append(action_dict)
            goto_list.append(goto_dict)
        # 接受
        action_list[1]['#'] = "acc"
        return action_list, goto_list
