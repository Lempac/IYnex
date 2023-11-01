from __future__ import annotations
import sys, os
from typing import NoReturn, cast
from termcolor import colored

"""
TODO:
Fix order of symbals(OR, AND, +, -, / ,*, ())
add not(!)
write emitter

"""

def lexer(chars: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    if chars == "":
        return [("END-OF-INPUT", "EOI")]
    for index, char in enumerate(chars):
        if char.isalpha():
            if len(tokens) > 0:
                if tokens[-1][0] in ("STR-BEGIN", "COMMENT-BEGIN"):
                    tokens.append(("STR", char))
                elif tokens[-1][0] == "STR":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + char))
                elif tokens[-1][0] == "IDENT":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + char))
                else:
                    tokens.append(("IDENT", char))
            else:
                tokens.append(("IDENT", char))
        elif char.isdigit():
            if len(tokens) > 0:
                if tokens[-1][0] == "INT":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + char))
                elif tokens[-1][0] == "IDENT":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + char))
                elif tokens[-1][0] == "STR":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + char))
                elif tokens[-1][0] in ("STR-BEGIN", "COMMENT-BEGIN"):
                    tokens.append(("STR", char))
                else:
                    tokens.append(("INT", char))
            else:
                tokens.append(("INT", char))
        elif char.isascii():
            if (char in ("'", '"')):
                if len(tokens) > 1 and tokens[-1][0] == "STR":
                    if tokens[-2][1] != char:
                        tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + char))
                    else:
                        tokens.append(("STR-END", char))
                elif len(tokens) > 1 and tokens[-1][0] == "STR-BEGIN":
                    tokens.append(("STR-END", char))
                else:
                    tokens.append(("STR-BEGIN", char))
            elif len(tokens) > 1 and tokens[-1][0] == "STR" and tokens[-2][0] != "COMMENT-BEGIN":
                tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + char))
            elif char == ";":
                tokens.append(("END-OF-LINE", char))
            elif char == "/":
                if len(tokens) > 0 and tokens[-1][0] == "DIV":
                    if len(tokens) > 1 and tokens[-2][0] == "STR":
                        tokens[-1] = ("COMMENT-END", "//")
                    else:
                        tokens[-1] = ("COMMENT-BEGIN", "//")
                else:
                    tokens.append(("DIV", char))
            elif char == ".":
                tokens.append(("DOT", char))
            elif char == "&":
                tokens.append(("AND", char))
            elif char == "|":
                tokens.append(("OR", char))
            elif char == "#":
                tokens.append(("LEN", char))
            elif char == "=":
                if len(tokens) > 0 and tokens[-1][0] == "SET":
                    tokens[-1] = ("EQU", str(tokens[-1][1] + char))
                elif len(tokens) > 0 and tokens[-1][0] in ("NOT", "LESS", "GREATER"):
                    tokens[-1] = (
                        tokens[-1][0] + "-EQU",
                        str(tokens[-1][1] + char),
                    )
                else:
                    tokens.append(("SET", char))
            elif char == "<":
                tokens.append(("LESS", char))
            elif char == ">":
                tokens.append(("GREATER", char))
            elif char == "!":
                tokens.append(("NOT", char))
            elif char == "*":
                tokens.append(("MUL", char))
            elif char == "-":
                tokens.append(("SUB", char))
            elif char == "+":
                tokens.append(("ADD", char))
            elif char == "(":
                tokens.append(("OPEN-P", char))
            elif char == ")":
                tokens.append(("CLOSE-P", char))
            elif char.isspace():
                if len(tokens) > 0 and tokens[-1][0] == "STR":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + char))
                elif len(tokens) > 0 and tokens[-1][0] in ("STR-BEGIN", "COMMENT-BEGIN"):
                    tokens.append(("STR", char))
                else:
                    tokens.append(("WHITESPACE", char))
            else:
                exitWithError("Unknown " + str(char) + " symbal at: " + str(index))
        else:
            exitWithError("Unknown " + str(char) + " char at: " + str(index))
    tokens.append(("END-OF-INPUT", "EOI"))
    return [ token for token in tokens if token[0] != "WHITESPACE" ]

class Node():
    def __init__(self, name : str, value : str, parent : Node | None):
        self.name = name
        self.value = value
        if parent is not None:
            self.parent = parent
        self.children : list[Node] = []
        self.index = -1
    def add_child(self, obj : Node) -> Node:
        self.children.append(obj)
        self.index += 1
        return obj

    def add_child_token(self, obj : tuple[str, str]) -> Node:
        return self.add_child(Node(*obj, self))

    def get_child(self, offset : int = 0):
        index = self.index+offset
        if index < 0 or index >= len(self.children):
            return None
        else:
            return self.children[index]
    
    def change_parent(self, node : Node):
        self.parent.children.remove(self)
        self.parent.index -= 1
        self.parent = node
        self.parent.add_child(self)

class bidirectional_iterator(object):
    def __init__(self, collection : list[tuple[str, str]]):
        self.collection = collection
        self.index = 0

    def peek(self):
        return self.collection[self.index+1] if self.index+1 < len(self.collection) else None

    def next(self):
        if self.index+1 < len(self.collection):
            self.index += 1
            return self.collection[self.index]
        else:
            return None

    def prev(self):
        self.index -= 1
        return None if self.index < 0 else self.collection[self.index]
    
    def prev_peek(self):
        return self.collection[self.index-1] if self.index-1 > 0 else None

    def curr(self):
        return self.collection[self.index]

class Parse():

    def parse(self, tokens : list[tuple[str, str]]) -> Node:
        line = Node("LINE", "LINE", None)
        Itokens = bidirectional_iterator(tokens)
        while not self.peek(Itokens.curr(), "END-OF-INPUT"):
            currentNode = line
            Itokens, currentNode = self.STATMENT(Itokens, currentNode)
        return line

    def match(self, token : tuple[str, str] | None, name : str | tuple[str, ...], value : str | None | tuple[str, ...] = None) -> bool:
        if token is None:
            exitWithError("Expected "+str(' or '.join(name) if name is tuple else name)+(" with value "+str(' or '.join(value) if value is tuple else value)+"!" if value is not None else "!"))

        if self.peek(token, name, value):
            return True
        else:
            if value is not None:
                exitWithError("Expected "+str(' or '.join(name) if name is tuple else name)+" with value "+str(' or '.join(value) if value is tuple else value)+" instead of "+token[0]+" with value "+token[1]+"!")
            else:
                exitWithError("Expected "+str(' or '.join(name) if name is tuple else name)+" instead of "+token[0]+"!")

    def peek(self, token : tuple[str, str] | None, name : str | tuple[str, ...], value : str | None | tuple[str, ...] = None) -> bool:
        if token is None:
            return False
        elif token[0] in name and value is None:
            return True
        elif token[0] in name and value is not None and token[1] in value:
            return True
        else:
            return False

    def END_OF_LINE(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "END-OF-LINE", ";")
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        return tokens, currentNode

    def SET(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "SET", "=")
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        return tokens, currentNode

    def COMMENT(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "COMMENT-BEGIN", "//")
        currentNode.name = "COMMENT-BLOCK"
        currentNode.value = "////"
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        if tokens.curr()[0] == "STR":
            currentNode.add_child_token(tokens.curr())
            tokens.next()
        self.match(tokens.curr(), "COMMENT-END", '//')
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        return tokens, currentNode

    def STR(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "STR-BEGIN", ('"', "'"))
        currentNode = currentNode.add_child_token(("STR", tokens.curr()[1]))
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        if tokens.curr()[0] == "STR":
            currentNode.add_child_token(tokens.curr())
            tokens.next()
        self.match(tokens.curr(), "STR-END", ('"', "'"))
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        return tokens, currentNode

    def INT(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        if tokens.curr()[0] != "INT" or not tokens.curr()[1].isdigit():
            exitWithError("Expected INT instead of "+tokens.curr()[0]+" with value "+tokens.curr()[1]+"!")
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        if self.peek(tokens.curr(), "DOT"):
            if currentNode.name == "DECIMAL":
                exitWithError(f"Cant have a second dot after {cast(Node, currentNode.get_child()).value}!")
            tokens, currentNode = self.DOT(tokens, currentNode)
        return tokens, currentNode

    def IDENT(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "IDENT")
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        return tokens, currentNode

    def DOT(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "DOT", ".")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("DECIMAL", ""))
            prev_child.change_parent(currentNode)
            currentNode.add_child_token(tokens.curr())
            tokens.next()
            tokens, currentNode = self.INT(tokens, currentNode)
            
        else:
            exitWithError("prev_child is missing?")
        return tokens, currentNode

    def ADD(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "ADD", "+")
        if currentNode.name == "UNARY":
            currentNode.add_child_token(tokens.curr())
        else:
            prev_child = currentNode.get_child()
            if prev_child is not None and prev_child.name == "TERM":
                currentNode = currentNode.add_child_token(("ADD", "+"))
                prev_child.change_parent(currentNode)
            else:
                exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def MUL(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "MUL", "*")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("MUL", "*"))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def SUB(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "SUB", "-")
        if currentNode.name == "UNARY":
            currentNode.add_child_token(tokens.curr())
        else:
            prev_child = currentNode.get_child()
            if prev_child is not None and prev_child.name == "TERM":
                currentNode = currentNode.add_child_token(("SUB", "-"))
                prev_child.change_parent(currentNode)
        tokens.next()
        return tokens, currentNode

    def DIV(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "DIV", "/")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("DIV", "/"))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def OPEN_P(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "OPEN-P", "(")
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        return tokens, currentNode

    def CLOSE_P(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "CLOSE-P", ")")
        currentNode.add_child_token(tokens.curr())
        tokens.next()
        return tokens, currentNode

    def NOT(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        exitWithError("NOT implemented, but do have not equ(!=) !")
        return tokens, currentNode

    def AND(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "AND", "&")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("AND", "&"))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def OR(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "OR", "|")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("OR", "|"))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def LESS(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "LESS", "<")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("LESS", "<"))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def GREATER(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "GREATER", ">")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("GREATER", ">"))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def EQU(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "EQU", "==")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("EQU", "=="))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def NOT_EQU(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "NOT-EQU", "!=")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("NOT-EQU", "!="))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def LESS_EQU(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "LESS-EQU", "<=")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("LESS-EQU", "<="))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def GREATER_EQU(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "GREATER-EQU", ">=")
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode = currentNode.add_child_token(("GREATER-EQU", ">="))
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens.next()
        return tokens, currentNode

    def LEN(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), "LEN", "#")
        currentNode = currentNode.add_child_token(("LEN-EXPRESSION", tokens.curr()[1]))
        currentNode.add_child_token(tokens.curr())
        tokens, currentNode = self.PRIMARY(tokens, currentNode)
        return tokens, currentNode

    def PRIMARY(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        if self.peek(tokens.curr(), "INT"):
            tokens, currentNode = self.INT(tokens, currentNode)
        elif self.peek(tokens.curr(), "STR-BEGIN"):
            tokens, currentNode = self.STR(tokens, currentNode)
        elif self.peek(tokens.curr(), "IDENT"):
            tokens, currentNode = self.IDENT(tokens, currentNode)
        else:
            exitWithError("Expected INT or STR-BEING or IDENT instead of "+tokens.curr()[0]+"!")
        return tokens, currentNode

    def UNARY(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        currentNode = currentNode.add_child_token(("UNARY", ""))
        if self.peek(tokens.curr(), "ADD"):
            tokens, currentNode = self.ADD(tokens, currentNode)
        elif self.peek(tokens.curr(), "SUB"):
            tokens, currentNode = self.SUB(tokens, currentNode)
        tokens, currentNode = self.PRIMARY(tokens, currentNode)
        
        return tokens, currentNode

    def TERM(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        currentNode = currentNode.add_child_token(("TERM", ""))
        tokens, currentNode = self.UNARY(tokens, currentNode)
        while self.peek(tokens.curr(), ("DIV", "MUL")):
            if self.peek(tokens.curr(), "DIV"):
                tokens, currentNode = self.DIV(tokens, currentNode)
            elif self.peek(tokens.curr(), "MUL"):
                tokens, currentNode = self.MUL(tokens, currentNode)
            tokens, currentNode = self.UNARY(tokens, currentNode)
        
        return tokens, currentNode

    def EXPRESSION(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        currentNode = currentNode.add_child_token(("EXPRESSION", ""))
        if self.peek(tokens.curr(), "LEN"):
            tokens, currentNode = self.LEN(tokens, currentNode)
        elif self.peek(tokens.curr(), "STR-BEGIN"):
            tokens, currentNode = self.STR(tokens, currentNode)
            if self.peek(tokens.curr(), "ADD"):
                tokens, currentNode = self.ADD(tokens, currentNode)
                tokens, currentNode = self.STR(tokens, currentNode)
        else:
            tokens, currentNode = self.TERM(tokens, currentNode)
            while self.peek(tokens.curr(), ("ADD", "SUB")):
                if self.peek(tokens.curr(), "ADD"):
                    tokens, currentNode = self.ADD(tokens, currentNode)
                elif self.peek(tokens.curr(), "SUB"):
                    tokens, currentNode = self.SUB(tokens, currentNode)
                tokens, currentNode = self.TERM(tokens, currentNode)
        return tokens, currentNode

    def COMPARISON(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        currentNode = currentNode.add_child_token(("COMPARISON", ""))
        tokens, currentNode = self.EXPRESSION(tokens, currentNode)
        while self.peek(tokens.curr(), ("AND", "OR", "EQU", "LESS-EQU", "NOT-EQU", "GREATER-EQU", "GREATER", "LESS")):
            if self.peek(tokens.curr(), "AND"):
                tokens, currentNode = self.AND(tokens, currentNode)
            elif self.peek(tokens.curr(), "OR"):
                tokens, currentNode = self.OR(tokens, currentNode)
            elif self.peek(tokens.curr(), "EQU"):
                tokens, currentNode = self.EQU(tokens, currentNode)
            elif self.peek(tokens.curr(), "LESS-EQU"):
                tokens, currentNode = self.LESS_EQU(tokens, currentNode)
            elif self.peek(tokens.curr(), "NOT-EQU"):
                tokens, currentNode = self.NOT_EQU(tokens, currentNode)
            elif self.peek(tokens.curr(), "GREATER-EQU"):
                tokens, currentNode = self.GREATER_EQU(tokens, currentNode)
            elif self.peek(tokens.curr(), "GREATER"):
                tokens, currentNode = self.GREATER(tokens, currentNode)
            elif self.peek(tokens.curr(), "LESS"):
                tokens, currentNode = self.LESS(tokens, currentNode)
            tokens, currentNode = self.EXPRESSION(tokens, currentNode)      
        return tokens, currentNode

    def OUT(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        out_statment = currentNode
        currentNode.name = "OUT-STATMENT"
        currentNode.value = tokens.curr()[1]
        tokens, currentNode = self.IDENT(tokens, currentNode)
        tokens, currentNode = self.OPEN_P(tokens, currentNode)
        tokens, currentNode = self.COMPARISON(tokens, currentNode)
        currentNode = out_statment
        tokens, currentNode = self.CLOSE_P(tokens, currentNode)
        tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        return tokens, currentNode

    def IN(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        in_statment = currentNode
        currentNode.name = "IN-STATMENT"
        currentNode.value = tokens.curr()[1]
        tokens, currentNode = self.IDENT(tokens, currentNode)
        tokens, currentNode = self.OPEN_P(tokens, currentNode)
        tokens, currentNode = self.COMPARISON(tokens, currentNode)
        currentNode = in_statment
        tokens, currentNode = self.CLOSE_P(tokens, currentNode)
        tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        return tokens, currentNode

    def WHILE(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        while_statment = currentNode
        currentNode.name = "WHILE-STATMENT"
        currentNode.value = tokens.curr()[1]
        tokens, currentNode = self.IDENT(tokens, currentNode)
        tokens, currentNode = self.OPEN_P(tokens, currentNode)
        tokens, currentNode = self.COMPARISON(tokens, currentNode)
        currentNode = while_statment
        tokens, currentNode = self.CLOSE_P(tokens, currentNode)
        if self.peek(tokens.curr(), "END-OF-INPUT"):
            tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        else:
            while not self.peek(tokens.curr(), "END-OF-LINE"):
                tokens, currentNode = self.STATMENT(tokens, currentNode)
                currentNode = while_statment
            tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        return tokens, currentNode

    def IF(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        if_statment = currentNode
        currentNode.name = "IF-STATMENT"
        currentNode.value = tokens.curr()[1]
        tokens, currentNode = self.IDENT(tokens, currentNode)
        tokens, currentNode = self.OPEN_P(tokens, currentNode)
        tokens, currentNode = self.COMPARISON(tokens, currentNode)
        currentNode = if_statment
        tokens, currentNode = self.CLOSE_P(tokens, currentNode)
        while not self.peek(tokens.curr(), "END-OF-LINE"):
            tokens, currentNode = self.STATMENT(tokens, currentNode)
            currentNode = if_statment
        tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        return tokens, currentNode

    def ELSE(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        else_statment = currentNode
        currentNode.name = "ELSE-STATMENT"
        currentNode.value = tokens.curr()[1]
        tokens, currentNode = self.IDENT(tokens, currentNode)
        if self.peek(tokens.curr(), "OPEN-P"):
            tokens, currentNode = self.OPEN_P(tokens, currentNode)
            tokens, currentNode = self.COMPARISON(tokens, currentNode)
            currentNode = else_statment
            tokens, currentNode = self.CLOSE_P(tokens, currentNode)
            while not self.peek(tokens.curr(), "END-OF-LINE"):
                tokens, currentNode = self.STATMENT(tokens, currentNode)
                currentNode = else_statment
            tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        else:
            while not self.peek(tokens.curr(), "END-OF-LINE"):
                tokens, currentNode = self.STATMENT(tokens, currentNode)
                currentNode = else_statment
            tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        return tokens, currentNode

    def FUNCTION(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        function_statment = currentNode
        prev_child = currentNode.get_child()
        if prev_child is not None:
            currentNode.name = "FUNCTION-"
            prev_child.change_parent(currentNode)
        else:
            exitWithError("prev_child is missing?")
        tokens, currentNode = self.OPEN_P(tokens, currentNode)
        if self.peek(tokens.curr(), "CLOSE-P"):
            tokens, currentNode = self.CLOSE_P(tokens, currentNode)
        else:
            tokens, currentNode = self.OPEN_P(tokens, currentNode)
            tokens, currentNode = self.COMPARISON(tokens, currentNode)
            currentNode = function_statment
            tokens, currentNode = self.CLOSE_P(tokens, currentNode)

        if self.peek(tokens.curr(), "END-OF-LINE"):
            currentNode.name += "UNSET"
            tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        else:
            currentNode.name += "SET"
            while not self.peek(tokens.curr(), "END-OF-LINE"):
                tokens, currentNode = self.STATMENT(tokens, currentNode)
                currentNode = function_statment
            tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        return tokens, currentNode

    def VARIABLE(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), ("END-OF-LINE", "SET"), (";", "="))
        variable_statment = currentNode
        if self.peek(tokens.curr(), "SET"):
            prev_child = currentNode.get_child()
            if prev_child is not None:
                currentNode.name = "VARIABLE-SET"
                prev_child.change_parent(currentNode)
                tokens, currentNode = self.SET(tokens, currentNode)
                if self.peek(tokens.curr(), "OPEN-P"):
                    tokens, currentNode = self.OPEN_P(tokens, currentNode)
                    while not self.peek(tokens.curr(), "CLOSE-P"):
                        if self.peek(tokens.peek(), "SET"):
                            tokens, currentNode = self.PRIMARY(tokens, currentNode)
                            tokens, currentNode = self.VARIABLE(tokens, currentNode)
                        else:
                            tokens, currentNode = self.COMPARISON(tokens, currentNode)
                            tokens, currentNode = self.VARIABLE(tokens, currentNode)
                    currentNode = variable_statment
                    tokens, currentNode = self.CLOSE_P(tokens, currentNode)
                    tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
                else:
                    tokens, currentNode = self.COMPARISON(tokens, currentNode)
                    currentNode = variable_statment
                    tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
            else:
                exitWithError("prev_child is missing?")
        else:
            prev_child = currentNode.get_child()
            if prev_child is not None:
                currentNode.name = "VARIABLE-UNSET"
                prev_child.change_parent(currentNode)
                tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
            else:
                exitWithError("prev_child is missing?")
        return tokens, currentNode

    def STATMENT(self, tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
        self.match(tokens.curr(), ("COMMENT-BEGIN", "IDENT", "SET", "OPEN-P", "END-OF-LINE"), ("//", "(", ";", tokens.curr()[1]))
        currentNode = currentNode.add_child_token(("STATMENT", ""))
        if self.peek(tokens.curr(), "COMMENT-BEGIN"):
            tokens, currentNode = self.COMMENT(tokens, currentNode)
        elif self.peek(tokens.curr(), "SET"):
            tokens, currentNode = self.VARIABLE(tokens, currentNode)
        elif self.peek(tokens.curr(), "IDENT"):
            if tokens.curr()[1] == "out":
                tokens, currentNode = self.OUT(tokens, currentNode)
            elif tokens.curr()[1] == "in":
                tokens, currentNode = self.IN(tokens, currentNode)
            elif tokens.curr()[1] == "if":
                tokens, currentNode = self.IF(tokens, currentNode)
            elif tokens.curr()[1] == "else":
                tokens, currentNode = self.ELSE(tokens, currentNode)
            elif tokens.curr()[1] == "while":
                tokens, currentNode = self.WHILE(tokens, currentNode)
            else:
                tokens, currentNode = self.IDENT(tokens, currentNode)
                self.match(tokens.curr(), ("END-OF-LINE", "OPEN-P", "SET"), ("=", "(", ";"))
                if self.peek(tokens.curr(), "OPEN-P"):
                    tokens, currentNode = self.FUNCTION(tokens, currentNode)
                else:
                    tokens, currentNode = self.VARIABLE(tokens, currentNode)
        elif self.peek(tokens.curr(), "END-OF-LINE"):
            tokens, currentNode = self.END_OF_LINE(tokens, currentNode)
        return tokens, currentNode

def emitter(NodeTree : Node):
    pass

def exitWithError(Error : str) -> NoReturn:
    # print(Error)
    sys.exit(colored(Error, 'red'))

def print_node(node : Node):
    print((node.name, node.value))
    print("Has:")
    for element in node.children:
        print((element.name, element.value), end=" ")
    print("\n")
    for element in node.children:
        if len(element.children) != 0:
            print_node(element)

if len(sys.argv) == 1:
    exitWithError("Need file input(-f helloWorld.ynex) or string of code(-c \'out(\"hello world\");\')!")
if sys.argv[1] not in ("-c", "-f"):
    exitWithError("""Options:
    -c : run with string of code
    -f : run with file of code
    """)
if sys.argv[1] == "-f":
    if len(sys.argv) < 3:
        exitWithError("No file input!")
    for file_path in sys.argv[2:]:
        if not os.path.exists(file_path):
            print(colored(f"Could open {file_path}!", 'red'))
            continue
        with open(file_path) as sourceFile:
            chars = sourceFile.read()
            lexResult = lexer(chars)
            print(lexResult)
            parseResult = Parse().parse(lexResult)
            print_node(parseResult)
            print(colored("DONE", 'green'))
            emitter(parseResult)
elif sys.argv[1] == "-c":
    if len(sys.argv) < 3:
        exitWithError("No input string!")
    for string_code in sys.argv[2:]:
        lexResult = lexer(string_code)
        print(lexResult)
        parseResult = Parse().parse(lexResult)
        print_node(parseResult)
        print(colored("DONE", 'green'))
        emitter(parseResult)
