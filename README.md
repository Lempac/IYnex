# IYnex
Custom programming languge.

## Gammer

```
program = statement
statement = "out" "(" comparison ")" ";"
    |   "if" "(" comparison ")" statement ";" 
        |   "else"
            |   "(" comparison ")" statement ";"
            |   statement ";"
    |   "while" "(" comparison ")" statement ";"
    |   ident = (comparison)* ";"
    |   ident ( "(" ")" | "(" ( comparison )* ")" )
        |   ";" 
        |   statement ";"
    |   "in" "(" comparison ")" ";"


comparison = expression (( "==" | "!=" | ">" | ">=" | "<" | "<=" | "&" | "|" ) expression)*
expression = ( term (( "-" | "+" ) term)* | string "+" string | string | "#" expression )
term = unary (( "/" | "*" ) unary)*
unary = ( "+" | "-" ) ( number | decimal | ident )
primary = number | decimal | string | ident
number = [0-9]*
text = [a-zA-Znumber]
string = ( ' | " ) text ( ' | " )
decimal = number "." number
ident = [a-zA-Z] text
comment = "//" text "//"
array = "(" (comparison ";" | comparison)* ")" ";"
dict = "(" (primary "=" comparison ";" | primary "=" comparison)* ")" ";"
```