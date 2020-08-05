####################
# CONSTANT 常量
####################

DIGITS = '0123456789'


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
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end


    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'