from main import run

def test():
    def func(text):
        result, error = run('<stdin>', text)
        if error:
            print(error.as_string())
        else:
            print(result)
    command = '-10 * 3 + (2 + 1.0) / 4 - 3' # -32.25
    func(command)
    command = '--5' # 5
    func(command)
    command = '2^8' # 256
    command = 'var a = var b = var c = 1'
    func(command)
    command = 'var x = 4 + a - (1 * b)'
    func(command)


test()