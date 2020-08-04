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
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        # Illegal Character => 非法字符
        super().__init__(pos_start, pos_end, "Illegal Character", details)

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
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"

class Token(object):
    def __init__(self, type_, value=None):
        # Token = <token-name, attribute-value>
        self.type = type_
        self.value = value

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
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                # 没有匹配任何Token，return some error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_coumt = 0 # 点的个数 => . 小数点

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
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))


####################
# RUN
####################

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    return tokens, error
