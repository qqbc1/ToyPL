from string_with_arrows import *

####################
# CONSTANT 常量
####################

DIGITS = '0123456789'

####################
# Error
####################

class Error(object):
    def __init__(self, pos_start, pos_end, error_name, details):
        """
        :param pos_start: 错误其实位置
        :param pos_end: 错误终止位置
        :param error_name: 错误类型名称
        :param details: 错误细节
        """
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        # 更加细致的错误信息
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        # Illegal Character => 非法字符
        super().__init__(pos_start, pos_end, "Illegal Character", details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        # Invalid Syntax => 无效的语法
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

####################
# POSITION 跟踪行号、列号、当前索引，便于定位报错
####################

class Position(object):
    def __init__(self, idx, ln, col, fn, ftxt):
        """

        :param idx: 索引
        :param ln: 行号
        :param col: 列号
        :param fn: 文件名（定义报错用）
        :param ftxt: 内容
        """
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        """
        读取下一个字符时
        :param current_char: 当前字符
        :return:
        """
        self.idx += 1 # 索引 + 1
        self.col += 1 # 列号 + 1

        if current_char == '\n': # 换行符
            self.ln += 1 # 行号 + 1
            self.col += 0 # 列号 归零

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

####################
# TOKENS
####################

# Token type => TT
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS" # 减法
TT_MUL = "MUL"
TT_DIV = "DIV" # 除法
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_EOF = "EOF" # 终止符

class Token(object):
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        # Token = <token-name, attribute-value>
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance(self.value)

        if pos_end:
            self.pos_end = pos_end


    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


####################
# LEXER 词法分析
####################

class Lexer(object):
    def __init__(self, fn, text):
        self.fn = fn # text来源 => 某个文件，方便报错定位
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text) # 位置
        self.current_char = None # 当前字符
        self.advance() # self.pos从-1开始，然后立刻调用self.advance

    # advance 预先的；先行的，获取下一个字符
    def advance(self):
        self.pos.advance(self.current_char)
        if self.pos.idx < len(self.text):
            self.current_char = self.text[self.pos.idx]
        else:
            self.current_char = None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in (' ', '\t'):
                # 为空格或制表符，直接跳过
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                # 没有匹配任何Token，return some error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_coumt = 0 # 点的个数 => . 小数点
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_coumt == 1:
                    break # 只可有一个小数点
                dot_coumt += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        if dot_coumt == 0: # 整数
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

####################
# NODES
####################

class NumberNode(object):
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'

class BinOpNode(object):
    # 二元操作
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode(object):
    # 一元操作
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


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

####################
# RUN
####################

def run(fn, text):
    # 生成Tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    print(tokens)
    # 生成AST，通过__repr__形式打印出树结构而已
    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error