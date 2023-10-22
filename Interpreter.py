from __future__ import annotations
import sys, os

def lex(line: str) -> list[tuple[str, str]] | str | None:
    tokens: list[tuple[str, str]] = []
    line = line.strip()
    if line == "":
        return
    for index, letter in enumerate(line):
        if letter.isalpha():
            if len(tokens) > 0:
                if tokens[-1][0] == "STR-BEGIN" or tokens[-1][0] == "COMMENT-BEGIN":
                    tokens.append(("STR", letter))
                elif tokens[-1][0] == "STR":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + letter))
                elif tokens[-1][0] == "IDENT":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + letter))
                else:
                    tokens.append(("IDENT", letter))
            else:
                tokens.append(("IDENT", letter))
        elif letter.isdigit():
            if len(tokens) > 0:
                if tokens[-1][0] == "INT":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + letter))
                elif tokens[-1][0] == "IDENT":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + letter))
                else:
                    tokens.append(("INT", letter))
            else:
                tokens.append(("INT", letter))
        elif letter.isascii():
            if letter == "/":
                if len(tokens) > 0 and tokens[-1][0] == "DIV":
                    if len(tokens) > 1 and tokens[-2][0] == "STR":
                        tokens[-1] = ("COMMENT-END", "//")
                    else:
                        tokens[-1] = ("COMMENT-BEGIN", "//")
                else:
                    tokens.append(("DIV", letter))
            elif letter == "'" or letter == '"':
                if len(tokens) > 0 and tokens[-1][0] == "STR":
                    tokens.append(("STR-END", letter))
                else:
                    tokens.append(("STR-BEGIN", letter))
            elif letter == ".":
                tokens.append(("DOT", letter))
            elif letter == "=":
                if len(tokens) > 0 and tokens[-1][0] == "SET":
                    tokens[-1] = ("EQU", str(tokens[-1][1] + letter))
                elif len(tokens) > 0 and (
                    tokens[-1][0] == "NOT"
                    or tokens[-1][0] == "LESS"
                    or tokens[-1][0] == "GREATER"
                ):
                    tokens[-1] = (
                        tokens[-1][0] + "-EQU",
                        str(tokens[-1][1] + letter),
                    )
                else:
                    tokens.append(("SET", letter))
            elif letter == "<":
                tokens.append(("LESS", letter))
            elif letter == ">":
                tokens.append(("GREATER", letter))
            elif letter == "!":
                tokens.append(("NOT", letter))
            elif letter == "*":
                tokens.append(("MUL", letter))
            elif letter == "-":
                tokens.append(("SUB", letter))
            elif letter == "+":
                tokens.append(("ADD", letter))
            elif letter == "(":
                tokens.append(("OPEN-P", letter))
            elif letter == ")":
                tokens.append(("CLOSE-P", letter))
            elif letter.isspace():
                if len(tokens) > 0 and tokens[-1][0] == "STR":
                    tokens[-1] = (tokens[-1][0], str(tokens[-1][1] + letter))
                else:
                    continue
            else:
                return "Unknown " + str(letter) + " symbal at: " + str(index)
        else:
            return "Unknown " + str(letter) + " char at: " + str(index)
    return tokens

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

def parse(tokens : list[tuple[str, str]]) -> Node | str:
    line = Node("LINE", "LINE", None)
    currentNode = line
    isComment = False
    for token in tokens:
        if token[0] == "COMMENT-BEGIN":
            currentNode = currentNode.add_child(Node("COMMENT-BEGIN", "//", currentNode))
            isComment = True
        elif token[0] == "COMMENT-END":
            currentNode.add_child(Node("COMMENT-END", "//", currentNode))
            while currentNode.name != "COMMENT-BEGIN":
                if not currentNode.parent:
                    return "Couldnt find COMMENT-BEGIN(//)!"
                else:
                    currentNode = currentNode.parent
            currentNode = currentNode.parent
            isComment = False
        elif isComment:
            currentNode = currentNode.add_child(Node(*token, currentNode))
        elif token[0] == "SET":
            if currentNode.name != "IDENT":
                return "What ever your setting in line, the left side is not a IDENT!"
            currentNode = currentNode.add_child(Node(*token, currentNode))
        elif token[0] == "OPEN-P":
            pass
        elif token[0] == "INT":
            pass
        else:
            line.add_child(Node(*token, currentNode))
    return line

def exitWithError(Error : str):
    print(Error)
    sys.exit(Error)


if len(sys.argv) == 1 or not os.path.exists(sys.argv[1]):
    exitWithError("Need file input!")

with open(sys.argv[1]) as sourceFile:
    lines = sourceFile.read().split(";")
    for index, line in enumerate(lines):
        lexResult = lex(line)
        if lexResult == None:
            continue
        elif type(lexResult) == str:
            exitWithError("On line: " + str(index+1) + " " + str(lexResult))
        elif type(lexResult) == list[tuple[str, str]]:
            print(lexResult)
            parseResult = parse(lexResult)
            if type(parseResult) == str:
                exitWithError("On line: " + str(index+1) + " " + str(parseResult))
            else:
                print(parseResult)
