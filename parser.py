from tokens import *
from ast_node import *
from error import InvalidSyntaxError


####################
# PARSER RESULT 解析结果
####################

class ParserResult(object):
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0 # 便于选择不同的报错，具体看failure方法

    def register_advancement(self):
        self.advance_count += 1

    def register(self, parser_result):
        self.advance_count += parser_result.advance_count
        if parser_result.error:
            self.error = parser_result.error
        return parser_result.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        # 使用advance_count来选择显示的报错信息
        if not self.error or self.advance_count == 0:
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
        """
        从tokens列表中获得下一个token
        :return:
        """
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        # 语法解析Tokens

        # 从其实非终结符开始 => AST Root Node
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"
            ))
        return res

    def if_expr(self):
        """
        if-expr     : KEYWORD:if expr KEYWORD:then expr
                      (KEYWORD:elif expr KEYWORD:then expr)* // 多层if
                      (KEYWORD:else expr)?

        if ... then
        elif ... then
        else ...
        :return:
        """
        res = ParserResult()
        case = []
        else_case = None

        # if-expr     : KEYWORD:if expr KEYWORD:then expr
        if not self.current_tok.matches(TT_KEYWORD, 'if'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "expected 'if'"
            ))

        res.register_advancement()
        self.advance() # 获取下个token

        condition = res.register(self.expr()) # 获得条件
        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "expected 'then'"
            ))

        res.register_advancement()
        self.advance()  # 获取下个token

        expr = res.register(self.expr())
        if res.error: return res
        case.append((condition, expr))

        # (KEYWORD:elif expr KEYWORD:then expr)*
        while self.current_tok.matches(TT_KEYWORD, 'elif'):
            res.register_advancement()
            self.advance()
            condition = res.register(self.expr())
            if res.error: return res

            if not self.current_tok.matches(TT_KEYWORD, 'then'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "expected 'then'"
                ))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            case.append((condition, expr))

        # (KEYWORD:else expr)?
        if self.current_tok.matches(TT_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()
            else_case = res.register(self.expr())
            if res.error: return res

        return res.success(IfNode(case, else_case))

    def for_expr(self):
        """
        for-expr    : KEYWORD:for IDENTIFIER EQ expr KEYWORD:to expr
              (KEYWORD:step expr)? KEYWROD: then expr

        var res = 1
        for var i = 1 to 10 then
            var res = res * i
        :return:
        """
        res = ParserResult()

        if not self.current_tok.matches(TT_KEYWORD, 'for'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'for'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'identifier'"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'identifier'"
            ))

        res.register_advancement()
        self.advance()
        start_value = res.register(self.expr()) # for循环起始值
        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, 'to'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'to'"
            ))

        res.register_advancement()
        self.advance()
        end_value = res.register(self.expr()) # for循环结束值

        if res.error: return res

        if self.current_tok.matches(TT_KEYWORD, 'step'): # 单次循环跳跃多少元素
            res.register_advancement()
            self.advance()
            step_value = res.register(self.expr())
            if res.error: return res

        else:
            step_value = None

        if not self.current_tok.matches(TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'then'"
            ))

        res.register_advancement()
        self.advance()
        body = res.register(self.expr())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self):
        """
        while-expr  : KEYWORD:while expr KEYWROD:then expr

        var i = 0
        while i < 10 then
            var i = i + 1
        :return:
        """
        res = ParserResult()

        if not self.current_tok.matches(TT_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'while'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'then'"
            ))

        res.register_advancement()
        self.advance()
        body = res.register(self.expr())
        if res.error: return res

        return res.success(WhileNode(condition, body))

    def func_expr(self):
        """
        解析函数定义
        func-expr   : KEYWORD func IDENTIFIER?
              LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
              ARROW expr
        :return:
        """
        res = ParserResult()

        if not self.current_tok.matches(TT_KEYWORD, 'func'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'func'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER: # 函数名
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            # 函数名后必然跟着 ( => func a(
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '('"
                ))
        else:
            var_name_tok = None # 匿名函数
            # 匿名函数后，直接跟 (
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier or '('"
                ))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        # 参数名，函数至少有一个参数 => func a(x
        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()
            # 参数中有逗号分隔，则有多个参数 => func a(x,y
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected identifier"
                    ))

                # 将参数添加到arg_name_toks列表中
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            # 参数匹配完后，就需要匹配右括号 => func a(x,y)
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected , or ')'"
                ))

        else: # 函数定义时，可以没有参数 => func a()
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier or ')'"
                ))

        res.register_advancement()
        self.advance()
        # func a (x,y) ->
        if self.current_tok.type != TT_ARROW:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected -> "
            ))

        res.register_advancement()
        self.advance()
        # 解析函数体中的逻辑，获得该函数的返回值
        node_to_return = res.register(self.expr())
        if res.error: return res
        return res.success(FuncNode(var_name_tok, arg_name_toks, node_to_return))

    def call(self):
        """
        解析函数调用
        call        : atom (LPAREN (expr (COMMA expr)*)? RPAREN)
        a(1+2, 3+4)
        """

        res = ParserResult()

        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            # 调用函数时，没有传参数
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                # 调用函数时，参数可以写成expr，expr也包含INT|FLOAT|IDENTIFIER等 => a(1+2
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(' or 'NOT'"
                    ))

                # 多个参数，由逗号分开
                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    # 将调用参数添加到arg_nodes列表中
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                # a(1+2, 3)
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()

            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        """
        atom        : INT|FLOAT|IDENTIFIER
                    : LPAREN expr RPAREN
                    : if-expr
                    : for-expr
                    : while-expr
                    : func-expr
        :return:
        """
        res = ParserResult()
        tok = self.current_tok

        # atom  : INT|FLOAT
        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        # atom  : STRINg
        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        # atom  : IDENTIFIER
        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            # 访问变量时，只会输入单独的变量名
            return res.success(VarAccessNode(tok))

        # atom : LPAREN expr RPAREN => (1 + 2) * 3
        elif tok.type == TT_LPAREN:
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res

            if self.current_tok.type == TT_RPAREN:
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        # atom : if-expr
        elif tok.matches(TT_KEYWORD, 'if'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        # atom : for-expr
        elif tok.matches(TT_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        # atom : while-expr
        elif tok.matches(TT_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        # atom : func-expr
        elif tok.matches(TT_KEYWORD, 'func'):
            func_expr = res.register(self.func_expr())
            if res.error: return res
            return res.success(func_expr)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            # 报错中，期望的值中不包含var，虽然其文法中包含expr（LPAREN expr RPAREN），而expr中又包含var KEYWORD
            # 但这里并不存赋值的情况，所以报错中不包含var
            # 编程语言中的错误提示非常重要，所以要尽可能保持正确
            "Expected int, float, identifier, '+', '-', '(', 'IF', 'FOR', 'WHILE', 'FUN'"
        ))

    def power(self):
        """
        power       : call (POW factor)*
        :return:
        """
        return self.bin_op(self.call, (TT_POW,), self.factor)

    def factor(self):
        """
        factor  : (PLUS|MINUS) factor
                : power
        :return:
        """
        res = ParserResult()
        tok = self.current_tok

        # factor  : (PLUS|MINUS) factor
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            # UnaryOpNode 一元操作 => (PLUS|MINUS) factor
            return res.success(UnaryOpNode(tok, factor))
        # factor    : power
        return self.power()

    def term(self):
        """
        term    : factor (MUL|DIV) factor)*
        :return:
        """
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def comp_expr(self):
        res = ParserResult()

        # comp-expr   : NOT comp-expr
        if self.current_tok.matches(TT_KEYWORD, 'not'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))
        else:
            # comp-expr    : arith-expr ((EE|LT|GT|LTE|GTE) arith-expr)*
            node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected int, float, identifier, '+', '-', '(' or 'not'"
                ))
            return res.success(node)

    def arith_expr(self):
        # arith-expr  : term ((PLUS|MINUS) term)*
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def expr(self):
        """
        表达式
        expr    : KEYWORD:var IDENTIFIER EQ expr
                : term ((PLUS|MINUS) term)*
        :return:
        """
        res = ParserResult()

        # 如果token为var，则是声明语句
        # expr    : KEYWORD:var IDENTIFIER EQ expr
        if self.current_tok.matches(TT_KEYWORD, 'var'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                # 不是变量名，语法异常，报错
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_EQ:
                # 表示等号，语法异常，报错
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))

            res.register_advancement()
            self.advance()
            # 变量赋值时，右值为表达式expr，此时可以调用self.expr() 递归处理
            # 此外，等于操作符不会出现在生成树中
            # basic > var a = 1
            # [KEYWORDS:var, IDENTIFIER:a, EQ, INT:1, EOF]
            # (IDENTIFIER:a, INT:1) => EQ 不存在
            # 1
            expr = res.register(self.expr())
            if res.error: return res
            # 赋值操作 var a = 1 + 4 => KEYWORD: var, Identifier: a, expr: 1 + 4
            return res.success(VarAssignNode(var_name, expr))
        else:
            node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_end, self.current_tok.pos_end,
                    # 期望的值中，包含var
                    "Expected 'var', int, float, identifier, '+', '-', '(' or 'not'"
                ))
            return res.success(node)


    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a
        res = ParserResult()
        left = res.register((func_a()))  # 递归调用
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)
