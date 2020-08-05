# 文法文件

## 说明

expr => 表达式
term => 项
factor => 因子

BNF范式中，一个表达式（expr）由一个项（term）构成，而项有因子（factor）构成

* 表示0个或无穷个

## 文法

为何不是 `expr : term ((MUL|DIV) term)*`？要考虑算计计算本身的规则。

expr    : term ((PLUS|MINUS) term)*

term    : factor (MUL|DIV) factor)*

factor  : INT|FLOAT
        : (PLUS|MINUS) factor
        : LPAREN expr RPAREN