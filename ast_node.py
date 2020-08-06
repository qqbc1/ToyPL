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

class StringNode(object):
    """
    字符串节点
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


class ForNode(object):
    """
    for循环
    """
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
        """
        :param var_name_tok: 循环变量
        :param start_value_node: 起始值
        :param end_value_node: 终止值
        :param step_value_node: 每次循环跳跃
        :param body_node: 循环体逻辑

        for var i = 0 to 10 step 2 then
            body

        i => var_name_tok
        0 => start_value_node
        10 => end_value_node
        2 => step_value_node
        body => body_node
        """
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node


class WhileNode(object):
    """
    while循环
    """
    def __init__(self, condition_node, body_node):
        """
        while codition_node then
            body_node
        :param condition_node: while关键字后的条件语句
        :param body_node: while循环体中逻辑
        """
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class FuncNode(object):
    def __init__(self, var_name_tok, arg_name_toks, body_node):
        """
        :param var_name_tok: 函数名
        :param arg_name_toks: 函数参数
        :param body_node: 函数体
        """
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node

        if self.var_name_tok: # 函数有函数名时
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0: # 函数无函数名，但有参数时
            self.pos_start = self.arg_name_toks[0].pos_start
        else: # 函数无函数名且无参数时
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end


class CallNode(object):
    """调用函数节点"""
    def __init__(self, node_to_call, arg_nodes):
        """
        :param node_to_call: 函数调用对象 ->
        :param arg_nodes: 调用函数时传入的参数
        """
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0: # 调用函数，传参时
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else: # 调用函数不传参时
            self.pos_end = self.node_to_call.pos_end