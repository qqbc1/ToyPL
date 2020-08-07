from tokens import *
from function import *


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

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node, context):
        # visit 循环调用，由NumberNode终结符结束
        # set_context 设置当前ast node的上下文
        # set_pos 设置当前ast node的position
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node, context):
        """
        访问list
        :param node:
        :param context:
        :return:
        """
        res = RTResult()
        elements = []

        # 获取list中的内容并添加到elements中
        for en in node.element_nodes:
            elements.append(res.register(self.visit(en, context)))
            if res.should_return(): return res

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

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
        if res.should_return(): return res
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
        if res.should_return():
            return res
        # 右递归
        right = res.register(self.visit(node.right_node, context))
        if res.should_return():
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
        if res.should_return():
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
        for condition, expr, should_return_null in node.case:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res
                if should_return_null:
                    return res.success(Number.null)
                else:
                    return res.success(expr_value)

        # else ...
        if node.else_case:
            expr, should_return_null =  node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.should_return(): return res
            if should_return_null:
                return res.success(Number.null)
            else:
                return res.success(else_value)

        # if判断，不满足条件，则返回None
        return res.success(Number.null)

    def visit_ForNode(self, node, context):
        """
        for循环
        :param node: ForNode
        :param context:
        :return:
        """
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return(): return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return(): return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.should_return(): return res
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
            # body_node可以对应着多行代码
            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res
            # 跳过此次循环
            if res.loop_should_continue:
                continue
            # 跳出此次循环
            if res.loop_should_break:
                break
            elements.append(value)

        if node.should_return_null:
            return res.success(Number.null)
        else:
            # 不为null，则返回循环体中每次循环逻辑执行后返回的值
            return res.success(List(elements).set_pos(node.pos_start, node.pos_end).set_context(context))

    def visit_WhileNode(self, node, context):
        """
        while循环
        :param node: WhileNode
        :param context:
        :return:
        """
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res

            if not condition.is_true(): break # while条件为False时，跳出while循环

            value = res.register(self.visit(node.body_node, context))
            # 只希望 res.error 为 True的时候返回res
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res
            # 跳过此次循环
            if res.loop_should_continue:
                continue
            # 跳出此次循环
            if res.loop_should_break:
                break
            elements.append(value)

        if node.should_return_null:
            return res.success(Number.null)
        else:
            # 不为null，则返回循环体中每次循环逻辑执行后返回的值
            return res.success(List(elements).set_pos(node.pos_start, node.pos_end).set_context(context))


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
        func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)

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
        if res.should_return(): return res
        # 为value_to_call（函数调用对象）设置上下文，这很重要，因为调用函数时，需要将函数内的context.parent设置成当前context
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end).set_context(context)

        for arg_node in node.arg_nodes:
            # 函数参数可能是执行式，也可以只是个数字 => a(1+2, 5)
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return(): return res
        # 函数的执行需要传入解释器 interpreter
        return_value = res.register(value_to_call.execute(args, self))
        if res.should_return(): return res
        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        """
        return关键字
        :param node:
        :param context:
        :return:
        """
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return(): return res
        else:
            value = Number.null
        # 返回对应值
        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        """
        toypl代码出现cointinue会被parse解析，然后会调用visit_ContinueNode方法
        该方法会将 loop_should_continue 设置为 True
        :param node:
        :param context:
        :return:
        """
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        """
        与visit_ContinueNode同理
        :param node:
        :param context:
        :return:
        """
        return RTResult().success_break()