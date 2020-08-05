from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, Context

def run(fn, text):
    # 生成Tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    print(tokens)

    # 生成AST，通过__repr__形式打印出树结构而已
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
    print(ast.node)

    # 通过解释器执行程序
    interpreter = Interpreter()
    context = Context("<program>")
    result = interpreter.visit(ast.node, context)

    return result.value, result.error