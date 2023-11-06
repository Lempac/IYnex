# IYnex
Custom programming languge.

## Gammer

```
program = statement
statement = ( 
    "out" "(" comparison ")" ";"
    |   "if" "(" comparison ")" statement ";"
    |   "else" ( "(" comparison ")" statement ";" | statement ";" )
    |   "while" "(" comparison ")" ( statement ";" | ";" )
    |   variable
    |   function
    |   "in" "(" comparison ")" ";"
    |   comment
)

variable = ident ( "=" ( comparison ("()") ";" | "(" ( variable | primary "=" variable )* ")" ";" ) | ";" )
function = ident ( "(" ")" | "(" comparison ")" ) ( ";" | (statement)* ";" )

comparison = expression (( "==" | "!=" | ">" | ">=" | "<" | "<=" | "&" | "|" ) expression)* | "(" expression ")"
expression = ( term (( "-" | "+" ) term)* | string "+" string | string | "#" primary )
term = unary (( "/" | "*" ) unary)*
unary = ( "+" | "-" ) primary
primary = int | decimal | string | ident | bool
bool = "T" | "F"
int = [0-9]*
text = [a-zA-Zint]
string = ( "'" text "'" | """ text """ | "'" "'" | """ """ )
decimal = int "." int
ident = [a-zA-Z] text
comment = "//" text "//"
```