#from Regex import Regex, parse_regex
from .DFA import DFA
from .NFA import NFA
import re
from typing import List, Tuple
from functools import reduce

class Lexer:
    def __init__(self, spec: List[Tuple[str, str]]) -> None:
       
        self.spec = [(token, re.compile(pattern)) for token, pattern in spec]

    def lex(self, input_str: str) -> List[Tuple[str, str]]:
        tokens = []
        tokens1 = []
        tokens2= set()
        i = 0
        ok = 1
        for _, pattern in self.spec:
            for token1 in pattern.pattern:
                if token1.isalnum():
                    tokens2.add(token1)
        
        while i < len(input_str):
            match_long = None
            token_long = None

            for j in range(i + 1, len(input_str) + 1):
                input1 = input_str[i:j]
                for token, pattern in self.spec:
                    try:
                        match = pattern.match(input1, 0)
                        if match:
                            start, end = match.span()
                            if match_long is None or len(input1[start:end]) > len(match_long):
                                match_long = input1[start:end]
                                token_long = token
                    except Exception as e:
                        break
            
            if match_long:
                tokens.append((token_long, match_long))
                i += len(match_long)
            else:
                nr = 0
                nr1 = 0
                for j in range(0,i+1):
                    if input_str[j] == '\n':
                        nr = j
                        nr1 = nr1 + 1

                if i != len(input_str) - 1:
                    if input_str[i] in tokens2:
                        if nr == 0:
                            str = f"No viable alternative at character {i + 1}, line {nr1}"
                        else:
                            str = f"No viable alternative at character {i - nr}, line {nr1}"
                    else:
                        str = f"No viable alternative at character {i}, line {nr1}"

                    tokens1.append(("", str))
                if i == len(input_str) - 1:
                    if input_str[i] not in tokens2:
                        if nr == 0:
                            str = f"No viable alternative at character {i}, line {nr1}"
                        else:
                            str = f"No viable alternative at character {i - nr}, line {nr1}"
                    else:
                        str = f"No viable alternative at character EOF, line {nr1}"
                    tokens1.append(("", str))
                i += 1 
                ok = 0
                break
        if ok == 1:
            return tokens
        else:
            return tokens1