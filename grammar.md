## 文法

expr        : KEYWORD:var IDENTIFIER EQ expr
            : comp-expr ((KEYWORD:and|KEYWORD:or) comp-expr)*

comp-expr   : NOT comp-expr
            : arith-expr ((EE|LT|GT|LTE|GTE) arith-expr)*

arith-expr  : term ((PLUS|MINUS) term)*

term        : factor (MUL|DIV) factor)*

factor      : (PLUS|MINUS) factor
            : power
        
power       : call (POW factor)*

call        : atom (LPAREN (expr (COMMA expr)*)? RPAREN)?

atom        : INT|FLOAT|STRING|IDENTIFIER
            : LPAREN expr RPAREN
            : if-expr
            : for-expr
            : while-expr
            : func-expr
            
if-expr     : KEYWORD:if expr KEYWORD:then expr
              (KEYWORD:elif expr KEYWORD:then expr)* // 多层if
              (KEYWORD:else expr)?
              
for-expr    : KEYWORD:for IDENTIFIER EQ expr KEYWORD:to expr
              (KEYWORD:step expr)? KEYWROD: then expr
              
while-expr  : KEYWORD:while expr KEYWROD:then expr
              
func-expr   : KEYWORD func IDENTIFIER?
              LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
              ARROW expr    // 支持匿名函数
  
## 说明

* 0次或多次
? 0次或一次

expr 表达式
comp-expr 比较表达式 compare
arith-expr 运算表达式
term 项
factor 因子
power 幂
atom 原子