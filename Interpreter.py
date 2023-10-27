from __future__ import annotations
import sys, os
from typing import cast

def lexer(chars: str) -> list[tuple[str, str]] | None:
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
                else:
                    tokens.append(("INT", char))
            else:
                tokens.append(("INT", char))
        elif char.isascii():
            if char == ";":
                tokens.append(("END-OF-LINE", char))
            elif char == "/":
                if len(tokens) > 0 and tokens[-1][0] == "DIV":
                    if len(tokens) > 1 and tokens[-2][0] == "STR":
                        tokens[-1] = ("COMMENT-END", "//")
                    else:
                        tokens[-1] = ("COMMENT-BEGIN", "//")
                else:
                    tokens.append(("DIV", char))
            elif char == "'" or char == '"':
                if len(tokens) > 0 and tokens[-1][0] == "STR":
                    tokens.append(("STR-END", char))
                else:
                    tokens.append(("STR-BEGIN", char))
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
        if parent != None:
            self.parent = parent
        self.children : list[Node] = []
    def add_child(self, obj : Node) -> Node:
        self.children.append(obj)
        return obj

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

    def curr(self):
        return self.collection[self.index]


def parse(tokens : list[tuple[str, str]]) -> Node:
    line = Node("LINE", "LINE", None)
    currentNode = line
    Itokens = bidirectional_iterator(tokens)
    while Itokens.curr()[0] != "END-OF-INPUT":
        token = Itokens.curr()
        if token[0] == "COMMENT-BEGIN":
            Itokens, currentNode = COMMENT(Itokens, currentNode)
        elif token[0] == "IDENT":
            if cast(tuple[str, str], Itokens.peek())[0] == "SET":
                Itokens, currentNode = IDENT(Itokens, currentNode)
            elif cast(tuple[str, str], Itokens.peek())[0] == "INT":
                Itokens, currentNode = EXPRESSION(Itokens, currentNode)
        else:
            exitWithError("Unknown token: "+token[0]+" with value: "+token[1])
    return line

def COMMENT(tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
    currentNode = currentNode.add_child(Node("COMMENT-BLOCK", "////", currentNode))
    currentNode.add_child(Node(*tokens.curr(), currentNode))
    while tokens.next() != None and tokens.curr()[0] != "COMMENT-END":
        currentNode.add_child(Node(*tokens.curr(), currentNode))
    if tokens.peek() is None:
        exitWithError("Forgot to close comment(//)?")
    currentNode.add_child(Node(*cast(tuple[str, str], tokens.next()), currentNode))
    currentNode = currentNode.parent
    return tokens, currentNode

def IDENT(tokens : bidirectional_iterator, currentNode : Node) -> tuple[bidirectional_iterator, Node]:
    return tokens, currentNode

def EXPRESSION(tokens : bidirectional_iterator, currentNode : Node):
    return tokens, currentNode

def emitter(NodeTree : Node):
    pass

def exitWithError(Error : str):
    # print(Error)
    sys.exit(Error)

if len(sys.argv) == 1 or not os.path.exists(sys.argv[1]):
    exitWithError("Need file input!")

with open(sys.argv[1]) as sourceFile:
    chars = sourceFile.read()
    lexResult = lexer(chars)
    if type(lexResult) is list:
        print(lexResult)
        parseResult = parse(lexResult)
        if type(parseResult) is Node:
            print([child.name for child in parseResult.children])
