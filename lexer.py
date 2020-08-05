from position import Position
from tokens import *
from error import IllegalCharError


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