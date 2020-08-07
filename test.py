from main import run

def test():
    def func(text):
        result, error = run('<stdin>', text)
        if error:
            print(error.as_string())
        elif result:
            print(result)

    # 测试基本运算
    command = '-10 * 3 + (2 + 1.0) / 4 - 3' # -32.25
    func(command)
    command = '--5' # 5
    func(command)
    command = '2^8' # 256
    func(command)

    # 测试变量支持
    command = 'var a = var b = var c = 1'
    func(command)
    command = 'var x = 4 + a - (1 * b)'
    func(command)

    # 测试布尔类型
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

    # 测试循环
    command = 'if 3 < 1 then 40 elif 5 > 4.0 then 50 else 60'
    func(command)
    command = 'if 3 < 1 then var a = 2 elif 5 > 6 then var b = 3.0 else var c = -4'
    func(command)

    # 测试循环
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

    # 测试函数
    command = 'func add(a,b) -> a + b'
    func(command)
    command = 'add(1, 3)'
    func(command)

    # 测试 string 类型
    command = 'var s = "Text"'
    func(command)
    command = r'var s = "text \"x\""'
    func(command)
    command = r'var s = "text \\ x \\"'
    func(command)
    command = r'var s = "text \nx\ty\nc"'
    func(command)

    # 测试list
    command = '[1,2,3]'
    func(command)
    command = '[1,2,3] + 4' # [1,2,3,4] 添加元素
    func(command)
    command = '[1,2,3] + [4,5,6]' # [1,2,3,[4,5,6]] 添加元素
    func(command)
    command = '[1,2,3] / 0' # 1 获取列表中元素
    func(command)
    command = '[1,2,3] * [4,5,6]' # [1,2,3,4,5,6] 拼接列表
    func(command)
    command = '[1,2,3] - 0' # [2,3] 删除列表中对应位置元素
    func(command)

    # 测试内建函数
    command = 'print(10)' # 输入 10
    func(command)
    command = 'var a = append([1,2,3], 4)' # a => [1,2,3,4]
    func(command)
    command = 'var a = pop([1,2,3], 0)' # a => 1
    func(command)
    command = 'var a = extend([1,2,3], [4,5])' # a => [1,2,3,4,5]
    func(command)

    # 测试多行支持, ; 表示换行
    command = '1+2; 3+4' # 3, 7
    func(command)
    command = 'var r = if 5 == 5 then "懒编程" else "二两说"' # 懒编程
    func(command)
    command = r'''
    if 3 == 3 then;
        var a = 1;
        var b = a + 3;
    elif 3 > 1 then;
        var c = 6;
    else print("123");
    a; b
    ''' # 0, 1, 4
    func(command)
    command = r'''
            var r1 = var r2 = 0;
            for i = 1 to 10 step 2 then; 
                var r1 = r1 + i; 
                var r2 = r2 - i;
            end;
            r1 ; r2; i
            '''
    func(command)# 0, 0, 25, -25, 9
    command = '''
    var r1 = var r2 = 0;
    while i < 10 then;
        var r1 = r1 + i;
        var r2 = r2 - i;
        var i = i + 1;
    end;
    r1 ; r2
    '''
    func(command) # 0, 0, 9, -9
test()