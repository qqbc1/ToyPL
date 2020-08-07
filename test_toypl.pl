# Toy Programming language 使用测试

# 递归
func Fib(n)
    if n <= 0 then
        return 0
    elif n == 1 then
        return 1
    else
        return Fib(n-1) + Fib(n-2)
    end
end

# 将斐波那契数列存入列表中
func Fib_Res(n)
    var res_list = []
    for i = 1 to n+1 then
        var res_list = append(res_list, Fib(i))
    end
    return res_list
end

Fib_Res(10)