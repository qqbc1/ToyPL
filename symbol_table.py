class SymbolTable(object):
    """
    符号表实现
    """
    def __init__(self, parent=None):
        # 符号表
        self.symbols = {}
        # 用于判断作用域
        self.parent = parent

    def get(self, name):
        """
        获取变量的值
        :param name: 变量名
        :return:
        """
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            # 存在parent父对象，则说明此时可能在函数或类中寻找某变量
            # 如果变量不存在，则尝试搜索全局变量，即它的parent对应的symbols
            # 疑惑：函数嵌套，此时可能会有多级parent，不应该使用while吗？
            return self.parent.get(name)
        return value

    def set(self, name, value):
        """
        变量赋值
        :param name:
        :param value:
        :return:
        """
        self.symbols[name] = value

    def remove(self, name):
        """
        变量删除
        :param name:
        :return:
        """
        del self.symbols[name]
