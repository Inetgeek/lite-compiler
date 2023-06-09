#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""
 @author: Colyn
 @project: compiler
 @devtool: PyCharm
 @date: 2023/3/25
 @file: attrib.py
"""

from ..utils.comm import *


# 读取配置文件
def read_config(file_path):
    with open(file_path) as json_file:
        config = json.load(json_file)
    return config


class Attributes(object):
    def __init__(self, file_path):
        self.production_list = get_json(file_dir=file_path)['production']
        self.nonTerminator_list, self.terminator_list = self.get_terminators_and_nonTerminators()
        self.production_map = self.get_production_map()
        self.space_nonTerminator = self.get_space_nonTerminator()

    def get_terminators_and_nonTerminators(self):
        nonTerminator_list = []
        terminator_list = []
        for production in self.production_list:
            if production['left'] not in nonTerminator_list:
                nonTerminator_list.append(production['left'])
        for production in self.production_list:
            right_list = production['right']
            for r in right_list:
                if r not in nonTerminator_list and r not in terminator_list:
                    terminator_list.append(r)
        return nonTerminator_list, terminator_list

    def get_production_map(self):
        production_map = {}
        for nonTerminator in self.nonTerminator_list:
            production_map[nonTerminator] = []
        for production in self.production_list:
            production_map[production['left']].append(production['right'])
        return production_map

    def get_space_nonTerminator(self):
        space_nonTerminator_set = set([])
        for production in self.production_list:
            if production['right'] == []:
                space_nonTerminator_set.add(production['left'])
        pre_num = len(space_nonTerminator_set)
        for left in self.production_map.keys():
            flag = False
            for right in self.production_map[left]:
                flag1 = True
                for word in right:
                    if word not in list(space_nonTerminator_set):
                        flag1 = False
                        break
                if flag1:
                    flag = True
                    break
            if flag:
                space_nonTerminator_set.add(left)
        last_num = len(space_nonTerminator_set)
        while pre_num < last_num:
            pre_num = last_num
            for left in self.production_map.keys():
                flag = False
                for right in self.production_map[left]:
                    flag1 = True
                    for word in right:
                        if word not in list(space_nonTerminator_set):
                            flag1 = False
                            break
                    if flag1:
                        flag = True
                        break
                if flag:
                    space_nonTerminator_set.add(left)
            last_num = len(space_nonTerminator_set)
        return space_nonTerminator_set


class First:
    def __init__(self, file_path, s):
        self.s = s
        self.a = Attributes(file_path)
        self.visited_nonTerminator_list = []
        self.first_set = set(self.get_first(self.s))

    def get_first(self, s):
        # 避免死递归
        if s in self.visited_nonTerminator_list:
            return []
        if s in self.a.nonTerminator_list:
            self.visited_nonTerminator_list.append(s)
        if s in self.a.terminator_list:
            return [s]
        first_list = []
        for pro_right in self.a.production_map[s]:
            for word in pro_right:
                if word not in self.a.space_nonTerminator:
                    first_list += self.get_first(word)
                    break
                first_list += self.get_first(word)
        return first_list


class AttributesExtend(Attributes):
    def __init__(self, file_path):
        super(AttributesExtend, self).__init__(file_path)
        self.first_set_map = {}
        for s in self.terminator_list:
            self.first_set_map[s] = {s}
        f_list = [First(file_path, s) for s in self.nonTerminator_list]
        for f in f_list:
            self.first_set_map[f.s] = f.first_set
