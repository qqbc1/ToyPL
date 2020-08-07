## 文法

支持多行编程

statements  : NEWLINE* expr (NEWLINE+ expr)* NEWLINE*

expr        : KEYWORD:var IDENTIFIER EQ expr
            : comp-expr ((KEYWORD:and | KEYWORD:or) comp-expr)*

comp-expr   : NOT comp-expr
            : arith-expr ((EE | LT | GT | LTE | GTE) arith-expr)*

arith-expr  : term ((PLUS | MINUS) term)*

term        : factor (MUL | DIV) factor)*

factor      : (PLUS | MINUS) factor
            : power
        
power       : call (POW factor)*

call        : atom (LPAREN (expr (COMMA expr)*)? RPAREN)?

atom        : INT | FLOAT | STRING | IDENTIFIER
            : LPAREN expr RPAREN
            : list-expr
            : if-expr
            : for-expr
            : while-expr
            : func-expr
            
list-exp    : LSQUARE (expr (COMMA expr)*)? RESQUARE // [1,2,3]
                 
       
if expr then;
    print("懒编程");
    var a = 6;
elif expr then;
    var b = 6;
else;
    var c = 7;
              
if-expr     : KEYWORD:if expr KEYWORD:then
              (expr if-expr-b | if-expr-c?) | (NEWLINE statements KEYWORD:end | if-expr-b | if-expr-c)
              
if-expr-b   : KEYWORD:elif expr KEYWORD:then
              (expr if-expr-b | if-expr-c?) | (NEWLINE statements KEYWORD:end | if-expr-b | if-expr-c)
              
if-expr-c   : KEYWORD:else
              expr | (NEWLINE statments KEYWORD:end)
                          
              
for-expr    : KEYWORD:for IDENTIFIER EQ expr KEYWORD:to expr
              (KEYWORD:step expr)? KEYWROD: then 
              // 如果没有NEWLINE，则只是单纯的expr，如果有NEWLINE则说明有换行
              expr | (NEWLINE statements KEYWORD:end)
              
while-expr  : KEYWORD:while expr KEYWROD:then
              expr | (NEWLINE statements KEYWORD:end)
    
// 支持匿名函数          
func-expr   : KEYWORD func IDENTIFIER?
              LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
              (ARROW expr) | (NEWLINE statements KEYWORD:end)   
  
## 说明

*   0次或多次
?   0次或一次
+   1次或多次

expr 表达式
comp-expr 比较表达式 compare
arith-expr 运算表达式
term 项
factor 因子
power 幂
atom 原子