from tokens import *
from error import RTError


####################
# RUNTIME RESULT 运行时结果
####################

class RTResult(object):
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


####################
# VALUES
####################

class Number(object):
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_by(self, other):
        # 加法操作
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subbed_by(self, other):
        # 减法操作
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multed_by(self, other):
        # 乘法操作
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def dived_by(self, other):
        # 除法操作
        if isinstance(other, Number):
            if other.value == 0:
                # 除法分母不可为0
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None

    def __repr__(self):
        return str(self.value)

####################
# CONTEXT 上下文
####################

class Context(object):
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        """

        :param display_name:
        :param parent:
        :param parent_entry_pos:
        """
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos


####################
# INTERPRETER 解释器
####################

class Interpreter(object):
    def visit(self, node, context):
        """
        递归下降算法
        :param node: 起始节点
        :param context: 对应的上下文，方便定位错误
        :return:
        """
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self):
        raise Exception(f'No visit_{type(node).__name__}')

    def visit_NumberNode(self, node, context):
        # visit 循环调用，由NumberNode终结符结束
        # set_context 设置当前ast node的上下文
        # set_pos 设置当前ast node的position
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        # 左递归
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        # 右递归
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        if node.op_tok.type == TT_PLUS: # 加法操作符
            result, error = left.added_by(right)
        elif node.op_tok.type == TT_MINUS: # 减法操作符
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL: # 乘法操作符
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV: # 除法操作符
            result, error = left.dived_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        # 当前number
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res

        error = None

        if node.op_tok.type == TT_MINUS: # 负数
            number, error = number.multed_by(Number(-1))

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))