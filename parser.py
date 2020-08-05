from tokens import *
from ast_node import *
from error import InvalidSyntaxError


####################
# PARSER RESULT 解析结果
####################

class ParserResult(object):
    # 目前阶段没什么用
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParserResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


####################
# PARSER 解析器
####################

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-', '*' or '/'"
            ))
        return res

    def factor(self):
        """
        因素
        factor  : INT|FLOAT
        :return:
        """
        res = ParserResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            # factor : (PLUS|MINUS) factor => -5
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT):
            # factor  : INT|FLOAT
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == TT_LPAREN:
            # factor : LPAREN expr RPAREN => (1 + 2) * 3
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res

            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))
        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int or float"
        ))

    def term(self):
        """
        术语
        term    : factor (MUL|DIV) factor)*
        :return:
        """
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        """
        表达式
        expr    : term ((PLUS|MINUS) term)*
        :return:
        """
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func , ops):
        # 递归调用，构建出AST
        res = ParserResult()
        left = res.register(func()) # 递归调用
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func()) # 递归调用
            left = BinOpNode(left, op_tok, right)
        return res.success(left)