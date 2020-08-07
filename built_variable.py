from type_operate import Number
from symbol_table import SymbolTable
from function import BuiltInFunction



# 全局符号表，用于定义默认的全局变量
global_symbol_table = SymbolTable()
# 定义默认变量null，其值为0
global_symbol_table.set('NULL', Number.null)
global_symbol_table.set('False', Number.false)
global_symbol_table.set('True', Number.true)
# 注册内建函数
global_symbol_table.set("PI", Number.PI)
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("is_number", BuiltInFunction.is_number)
global_symbol_table.set("is_str", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_func", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)