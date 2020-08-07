####################
# PARSER RESULT 解析结果
####################

class ParserResult(object):
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0 # 便于选择不同的报错，具体看failure方法
        self.last_registered_advance_count = 0
        self.to_reverse_count = 0 # 反向操作个数

    def register_advancement(self):
        self.advance_count += 1
        self.last_registered_advance_count = 1

    def register(self, parser_result):
        self.last_registered_advance_count = parser_result.advance_count
        self.advance_count += parser_result.advance_count
        if parser_result.error:
            self.error = parser_result.error
        return parser_result.node

    def try_register(self, parser_result):
        if parser_result.error:
            self.to_reverse_count = parser_result.advance_count
            return None
        return self.register(parser_result)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        # 使用advance_count来选择显示的报错信息
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self


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