from .DFA import DFA
from .NFA import NFA
#from .Regex import Regex, parse_regex
#from .Lexer import Lexer


class Parser():
    def __init__(self) -> None:
        """
        Constructorul primește un șir de intrare și îl stochează.
        """
        #self.input = ""  

    def parse(self, input: str) -> str:
       
        i = 0
        a1 = []
        while i < len(input):
            if input[i] == '(':
                close_index = self.find_closing_parenthesis(input, i)
                inner = self.parse(input[i+1:close_index])
                a1.append(f"Parant ({inner})")
                i = close_index + 1
            elif input[i] >= 'a' and input[i] <= 'z':
                a1.append(f'Var "{input[i]}"')
                i += 1
            elif input[i] >= '0' and input[i] <= '9':
                a1.append(f'Val {input[i]}')
                i += 1
            elif input[i] == '+':
                left = self.parse(input[0:i])
                right = self.parse(input[i+1:])
                return f"Plus ({left}) ({right})"
            elif input[i] == '*':
                left = self.parse(input[0:i])
                right = self.parse(input[i+1:])
                return f"Mult ({left}) ({right})"
            elif input[i] == '/':
                left = self.parse(input[0:i])
                right = self.parse(input[i+1:])
                return f"Div ({left}) ({right})"
            elif input[i] == '-':
                left = self.parse(input[0:i])
                right = self.parse(input[i+1:])
                return f"Minus ({left}) ({right})"
            elif input[i] == '.':
                left = self.parse(input[1:i])
                right = self.parse(input[i+1:])
                return f'Lambda ({left}) -> {right}'
            else:
                i += 1  

        return ''.join(a1)

    def find_closing_parenthesis(self, input: str, open_index: int) -> int:
        stack = 1
        for i in range(open_index + 1, len(input)):
            if input[i] == '(':
                stack += 1
            elif input[i] == ')':
                stack -= 1
                if stack == 0:
                    return i
        return -1 
