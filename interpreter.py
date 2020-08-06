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

class Value(object):
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RTError(
            self.pos_start, other.pos_end,
            # Illegal operation => 非法操作
            "Illegal operation",
            self.context
        )


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_by(self, other):
        """加法操作"""
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        """减法操作"""
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        """乘法操作"""
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

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
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        """幂运算"""
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        """copy本身"""
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)


class Function(Value):
    def __init__(self, name, body_node, arg_names):
        """
        函数对象
        :param name: 函数名
        :param body_node: 函数体
        :param arg_names: 函数参数
        """
        super().__init__()
        # anonymous 匿名
        self.name = name or "<anonymous>"
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        """
        执行函数
        :param args: 执行函数时，传入的参数
        :return:
        """
        res = RTResult()
        # 为函数单独创建新的解释器
        interpreter = Interpreter()
        # 为函数创建新的上下文，每个函数都有独立的上下文
        # 其parent.context为调该用函数的对象的context，即self.context
        new_context = Context(self.name, self.context, self.pos_start)
        # 为函数创建新的符号表，每个函数都有独立的符号表
        # 其parent.symbol_table为调用该函数的对象的symbol_table
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

        # 调用函数时传入的参数多于函数定义中的参数
        if len(args) > len(self.arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(self.arg_names)} too many args passed into '{self.name}'",
                self.context
            ))

        # 调用函数时传入的参数多于函数定义中的参数
        if len(args) < len(self.arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(self.arg_names)} too few args passed into '{self.name}'",
                self.context
            ))

        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            # 更新当前节点的上下文，方便报错时定位
            arg_value.set_context(new_context)
            # 将调用函数时，传入的参数值存入函数符号表中
            new_context.symbol_table.set(arg_name, arg_value)

        # 通过解释器执行函数体中的逻辑
        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error: return res
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"

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
        """
        二元操作
        :param node:
        :param context:
        :return:
        """
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
        """
        一元操作
        :param node:
        :param context:
        :return:
        """
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

    def visit_IfNode(self, node, context):
        """
        if条件语句
        :param node: IfNode 对象，其中case是二元组，表示有有多层if判断
         if ... then ...
         elif ... then ...
         elif ... then ...
         else ...  => [(condition, expr), ...]
        :param context:
        :return:
        """
        res = RTResult()

        # if ... then ... elif ... then ...
        for condition, expr in node.case:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                return res.success(expr_value)

        # else ...
        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error: return res
            return res.success(else_value)

        # if判断，不满足条件，则返回None
        return res.success(None)

    def visit_ForNode(self, node, context):
        """
        for循环
        :param node: ForNode
        :param context:
        :return:
        """
        res = RTResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error: return res
        else:
            step_value = Number(1) # 默认每次循环，只跳过一个元素

        # 允许 step 为负数
        i = start_value.value

        # In [8]: condition = lambda: i<4
        # In [9]: i = 1
        # In [10]: while condition():
        #     ...:     print(i)
        #     ...:     i += 1
        # 1
        # 2
        # 3
        # 4
        if step_value.value >= 0:
            # step_value 为正数时，循环start_value -> end_value 从小到大
            condition = lambda: i < end_value.value
        else:
            # step_value 为负数时，循环start_value -> end_value 从大到小
            condition = lambda : i > end_value.value

        while condition():
            # node.var_name_tok.value =>  KEYWORD:for IDENTIFIER EQ expr 中的 IDENTIFIER 变量名
            # 这里将for循环中的变量名的值存入符号表中，让该变量值，在循环后，依旧可以获得累加或累减后的结果
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value # 循环
            # 执行循环体对应的expr
            res.register(self.visit(node.body_node, context))
            if res.error: return res

        return res.success(None)

    def visit_WhileNode(self, node, context):
        """
        while循环
        :param node: WhileNode
        :param context:
        :return:
        """
        res = RTResult()

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res

            if not condition.is_true(): break # while条件为False时，跳出while循环

            res.register(self.visit(node.body_node, context))
            if res.error: return res

        return res.success(None)

    def visit_FuncNode(self, node, context):
        """
        定义函数，获得函数可调用对象
        :param node: FuncNode
        :param context: 上下文
        :return:
        """
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None # 函数名
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        # 通过Function构建函数对象
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_tok:
            # 将函数对象存入到函数parent.context中，让 visit_CallNode 方法使用
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        """
        调用函数，获得函数执行结果
        :param node: CallNode
        :param context:
        :return:
        """
        res = RTResult()
        args = []
        # self.visit(node.node_to_call, context) -> visit_VarAccessNode()
        # visit_VarAccessNode()方法通过节点名（即函数名）从符号表中获得函数对象本身
        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            # 函数参数可能是执行式，也可以只是个数字 => a(1+2, 5)
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res

        return_value = res.register(value_to_call.execute(args))
        if res.error: return res
        return res.success(return_value)


