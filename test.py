from main import run

def test():
    def func(text):
        result, error = run('<stdin>', text)
        if error:
            print(error.as_string())
        elif result:
            print(result)
    command = '-10 * 3 + (2 + 1.0) / 4 - 3' # -32.25
    func(command)
    command = '--5' # 5
    func(command)
    command = '2^8' # 256
    func(command)
    command = 'var a = var b = var c = 1'
    func(command)
    command = 'var x = 4 + a - (1 * b)'
    func(command)
    command = '3 >= 3' # 1
    func(command)
    command = '6.0 > 7' # 1
    func(command)
    command = '3 < 1' # 0
    func(command)
    command = '3 <= 2' # 0
    func(command)
    command = '1 == 1 and 3 > 2'
    func(command)
    command = '(1 == 1) and (3 > 2)'
    func(command)
    command = 'var a = (1 == 1) and (3 > 2)'
    func(command)
    command = 'if 3 < 1 then 40 elif 5 > 4.0 then 50 else 60'
    func(command)
    command = 'if 3 < 1 then var a = 2 elif 5 > 6 then var b = 3.0 else var c = -4'
    func(command)
    command = 'var i = 0'
    func(command)
    command = 'while i < 10 then var i = i + 1'
    func(command)
    command = 'i'
    func(command)
    command = 'var res = 1'
    func(command)
    command = 'for i = 1 to 10 step 2 then var res = res + i'
    func(command)
    command = 'res'
    func(command)
    command = 'func add(a,b) -> a + b'
    func(command)
    command = 'add(1, 3)'
    func(command)

test()