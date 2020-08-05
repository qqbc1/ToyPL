from tokens import *
from error import RTError
from symbol_table import SymbolTable


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
        """加法操作"""
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subbed_by(self, other):
        """减法操作"""
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multed_by(self, other):
        """乘法操作"""
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def dived_by(self, other):
        """除法操作"""
        if isinstance(other, Number):
            if other.value == 0:
                # 除法分母不可为0
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None

    def powed_by(self, other):
        """幂运算"""
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        """copy本身"""
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

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
        self.symbol_table = None # 符号表



class Interpreter(object):
    """
    解释器
    Interpreter类方法名的规则: "visit_" + ast_node.py中的类名
    """
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

    def visit_VarAccessNode(self, node ,context):
        """
        访问变量的值
        :param node: 节点
        :param context: 上下文
        :return:
        """
        res = RTResult()
        var_name = node.var_name_tok.value # 从token中获得变量名
        value = context.symbol_table.get(var_name) # 从符号表中取值

        if not value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"{var_name} is not defined",
                context
            ))
        # copy本身，避免影响后续操作（引用型语言要考虑的问题）
        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        """
        变量赋值
        :param node:
        :param context:
        :return:
        """
        res = RTResult()
        var_name = node.var_name_tok.value # 变量名
        # 因为node.value_node对应的节点可能是expr、Number等，所以需要递归处理
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res
        # 将变量名与变量值存入符号表中
        context.symbol_table.set(var_name, value)
        return res.success(value)

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
        elif node.op_tok.type == TT_POW: # 幂运算
            result, error = left.powed_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'and'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, 'or'):
            result, error = left.ored_by(right)
        else:
            # 不支持某种操作
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"{node.op_tok.type} is not suppert",
                context
            ))

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
        elif node.op_tok.matches(TT_KEYWORD, 'not'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))