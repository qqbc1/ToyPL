class NumberNode(object):
    """
    数字节点
    """

    def __init__(self, tok):
        """
        :param tok: 节点的token
        """
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class VarAccessNode(object):
    """
    访问变量名
    """

    def __init__(self, var_name_tok):
        """
        :param var_name_tok: 变量名token
        """
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f'({self.var_name_tok})'



class VarAssignNode(object):
    """
    为变量分配值
    """

    def __init__(self, var_name_tok, value_node):
        """
        :param var_name_tok: 变量名token
        :param value_node: 变量名对应的表达式节点
        """
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f'({self.var_name_tok}, {self.value_node})'


class BinOpNode(object):
    """
    二元操作
    """

    def __init__(self, left_node, op_tok, right_node):
        """
        6.0 * 4  =>  (FLOAT:6.0, MUL, INT:4)
        :param left_node: 左节点 => FLOAT:6.0
        :param op_tok: 中间操作符 => MUL
        :param right_node: 右节点 => INT:4
        """
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode(object):
    """
    一元操作
    """

    def __init__(self, op_tok, node):
        """
        -100  =>  (MINUS, INT:100)
        :param op_tok: 操作符
        :param node: 节点
        """
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

class IfNode(object):
    """
    if ... then
    elif ... then
    else ...
    if相关操作
    """
    def __init__(self, case, else_case):
        self.case = case
        self.else_case = else_case

        # 因为if判断可以有多层，所以case是二元数组
        self.pos_start = self.case[0][0].pos_start
        self.pos_end = (self.else_case or self.case[len(self.case) - 1][0]).pos_end

    def __repr__(self):
        result = ''
        for condition, expr in self.case[:-1]:
            result += f"if {condition} then {expr}"
        if self.else_case:
            result += f" else {self.else_case}"
        return f'({result})'