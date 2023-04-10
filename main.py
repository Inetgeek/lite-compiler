import os
import argparse
from compiler.config import config
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic_analyzer import Semantic

if __name__ == '__main__':
    output = config.dist_dir
    os.makedirs(os.path.join('.', output), exist_ok=True)

    parser = argparse.ArgumentParser(description='[lite-compiler]\nAuthor: Colyn\nEmail: digran@foxmail.com')
    parser.add_argument("-l", "--lex", type=str, help="需要进行词法分析的源代码路径，如[-l code.cpp]")
    parser.add_argument("-p", "--parse", type=str, help="需要进行语法分析的token表路径，默认不填写")
    parser.add_argument("-s", "--semantic", type=str, help="需要进行语义分析的token表路径，默认不填写")
    parser.add_argument("-o", "--observer", type=int, help="是否需要显示每个分析器的输出结果 [1 显示][0 不显示]")

    args = parser.parse_args()

    if args.lex:
        show = False
        if args.observer:
            show = bool(args.observer)
        lex = Lexer(src_code_path=args.lex)
        lex.analysis(show)

    if args.parse:
        show = False
        if args.observer:
            show = bool(args.observer)
        parser = Parser(token_table_path=args.parse)
        parser.analysis(show)

    if args.semantic:
        show = False
        if args.observer:
            show = bool(args.observer)
        sem = Semantic(token_table_path=args.semantic)
        sem.analysis(show)
