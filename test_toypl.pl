# 递归方式实现斐波那契数列
func Fib(n)
    if n <= 0 then
        return 0
    elif n == 1 then
        return 1
    else
        return Fib(n-1) + Fib(n-2)
    end
end

# 通过列表实现斐波那契数列
func Fib_Res(n)
    var res_list = []
    for i = 1 to n then
        var res_list = append(res_list, Fib(i))
    end
    return res_list
end

Fib_Res(10)