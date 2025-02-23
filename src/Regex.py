from dataclasses import dataclass
from typing import Union as TypingUnion
from .NFA import NFA

EPSILON = ''  # Epsilon transition representation

class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError("Subclasses must implement the thompson method.")

@dataclass
class Character(Regex):
    char: str

    def thompson(self) -> NFA[int]:
        start_state = 0
        accept_state = 1
        S = {self.char}
        K = {start_state, accept_state}
        q0 = start_state
        d = {(start_state, self.char): {accept_state}}
        F = {accept_state}
        return NFA(S, K, q0, d, F)

@dataclass
class Concat(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        left_nfa = self.left.thompson()
        right_nfa = self.right.thompson()

        # Create a new NFA for concatenation
        S = left_nfa.S | right_nfa.S  # Union of alphabets
        K = set()  # Set of states for the resulting NFA
        q0 = left_nfa.q0  # Start state is the same as the start state of the left NFA
        d = {}  # Transition function
        F = set()  # Set of final states for the resulting NFA

        # Calculate an offset to avoid state conflicts
        state_offset = max(left_nfa.K) + 1

        # Map states for both NFAs
        left_state_mapping = {state: state for state in left_nfa.K}
        right_state_mapping = {state: state + state_offset for state in right_nfa.K}

        # Add states from both NFAs
        for state in left_state_mapping.values():
            K.add(state)
        for state in right_state_mapping.values():
            K.add(state)

        # Add transitions for the left NFA
        for (from_state, symbol), to_states in left_nfa.d.items():
            for to_state in to_states:
                d[(left_state_mapping[from_state], symbol)] = {left_state_mapping[to_state]}

        # Add transitions for the right NFA
        for (from_state, symbol), to_states in right_nfa.d.items():
            for to_state in to_states:
                d[(right_state_mapping[from_state], symbol)] = {right_state_mapping[to_state]}

        # Add epsilon transition from the final states of the left NFA to the start state of the right NFA
        for accept_state in left_nfa.F:
            d[(left_state_mapping[accept_state], EPSILON)] = {right_state_mapping[right_nfa.q0]}

        # Set the start state
        q0 = left_state_mapping[left_nfa.q0]

        # Set the final states of the resulting NFA
        for accept_state in right_nfa.F:
            F.add(right_state_mapping[accept_state])

        return NFA(S, K, q0, d, F)



@dataclass
class Union(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        left_nfa = self.left.thompson()
        right_nfa = self.right.thompson()

        K = set()
        d = {}
        F = set()
        S = left_nfa.S | right_nfa.S
        q0 = 0

        # Calculate a unique final state
        final_state = max(left_nfa.K) + max(right_nfa.K) + 3
        F.add(final_state)

        # Add the start state (q0)
        K.add(q0)
        K.add(final_state)

        # Left state mapping (offset by 1)
        left_state_mapping = {state: state + 1 for state in left_nfa.K}

        # Add states and transitions for the left NFA
        for state in left_state_mapping.values():
            K.add(state)

        for (from_state, symbol), to_states in left_nfa.d.items():
            for to_state in to_states:
                d[(left_state_mapping[from_state], symbol)] = {left_state_mapping[to_state]}

        # Right state mapping (offset by max(left_nfa.K) + 1)
        right_state_offset = max(left_nfa.K) + 2
        right_state_mapping = {state: state + right_state_offset for state in right_nfa.K}

        # Add states and transitions for the right NFA
        for state in right_state_mapping.values():
            K.add(state)

        for (from_state, symbol), to_states in right_nfa.d.items():
            for to_state in to_states:
                d[(right_state_mapping[from_state], symbol)] = {right_state_mapping[to_state]}

        # Add epsilon transitions from start state to both NFA starts
        d[(q0, EPSILON)] = {left_state_mapping[left_nfa.q0], right_state_mapping[right_nfa.q0]}

        # Add epsilon transitions from accept states of both NFAs to the final accept state
        for accept_state_left in left_nfa.F:
            d[(left_state_mapping[accept_state_left], EPSILON)] = {final_state}
        for accept_state_right in right_nfa.F:
            d[(right_state_mapping[accept_state_right], EPSILON)] = {final_state}

        return NFA(S, K, q0, d, F)

@dataclass
class Question_Mark(Regex):

    regex: Regex

    def thompson(self) -> NFA[int]:
        base_nfa = self.regex.thompson()

        # Create a new NFA for the QuestionMark operator
        K = set()
        d = {}
        F = set()
        S = base_nfa.S
        state_offset = max(base_nfa.K) + 1  # Offset for new states

        # Map states from the base NFA
        state_mapping = {state: state + 1 for state in base_nfa.K}

        # Add all states from the base NFA
        for state in state_mapping.values():
            K.add(state)

        # Add transitions from the base NFA
        for (from_state, symbol), to_states in base_nfa.d.items():
            for to_state in to_states:
                d[(state_mapping[from_state], symbol)] = {state_mapping[to_state]}

        # Add a new start and accept state

        #print(start_state)
        start_state = 0
        accept_state = state_offset + 1
        K.add(start_state)
        K.add(accept_state)

        # Add epsilon transitions from the new start state to the base NFA start state and accept state
        d[(start_state, EPSILON)] = {state_mapping[base_nfa.q0], accept_state}

        # Add epsilon transitions from the final states of the base NFA to the new accept state
        for accept_state_base in base_nfa.F:
            d[(state_mapping[accept_state_base], EPSILON)] = {accept_state}

        # Set the new start state and final state
        q0 = start_state
        F.add(accept_state)

        return NFA(S, K, q0, d, F)


@dataclass
class Plus(Regex):
    regex: Regex

    def thompson(self) -> NFA[int]:
        base_nfa = self.regex.thompson()
        
        # Create a new NFA for the Plus operator
        K = set()
        d = {}
        F = set()
        S = base_nfa.S
        state_offset = max(base_nfa.K) + 1  # Offset for new states
        
        # Map states from the base NFA
        state_mapping = {state: state + 1 for state in base_nfa.K}

        # Add all states from the base NFA
        for state in state_mapping.values():
            K.add(state)

        # Add transitions from the base NFA
        for (from_state, symbol), to_states in base_nfa.d.items():
            for to_state in to_states:
                d[(state_mapping[from_state], symbol)] = {state_mapping[to_state]}

        # Add a new start and accept state
        start_state = 0
        accept_state = state_offset + 1
        K.add(start_state)
        K.add(accept_state)

        # Add epsilon transitions from the new start state to the base NFA start state
        d[(start_state, EPSILON)] = {state_mapping[base_nfa.q0]}

        for accept_state_base in base_nfa.F:
            d[(state_mapping[accept_state_base], EPSILON)] = {state_mapping[base_nfa.q0]}

        # Add epsilon transitions from the final states of the base NFA to the new accept state
        for accept_state_base in base_nfa.F:
            d[(state_mapping[accept_state_base], EPSILON)] = {accept_state}

        # Set the new start state and final state
        q0 = start_state
        F.add(accept_state)

        return NFA(S, K, q0, d, F)

@dataclass
class CharacterClass(Regex):
    def __init__(self, start_char: str, end_char: str):
        self.start_char = start_char
        self.end_char = end_char

    def thompson(self) -> NFA[int]:
        start_state = 0
        accept_state = 1
        S = set(chr(i) for i in range(ord(self.start_char), ord(self.end_char) + 1)) 
        K = {start_state, accept_state}
        q0 = start_state
        d = {}
        F = {accept_state}
        for char in range(ord(self.start_char), ord(self.end_char) + 1):
            d[(start_state, chr(char))] = {accept_state}

        return NFA(S, K, q0, d, F)

@dataclass
class Star(Regex):
    regex: Regex
    def thompson(self) -> NFA[int]:
        base_nfa = self.regex.thompson()

        # Create a new NFA for the Star operator
        K = set()
        d = {}
        F = set()
        S = base_nfa.S
        state_offset = max(base_nfa.K) + 1  # Offset for new states
        
        # Map states from the base NFA
        state_mapping = {state: state + 1 for state in base_nfa.K}

        # Add all states from the base NFA, remapped
        for state in state_mapping.values():
            K.add(state)

        # Add transitions from the base NFA, remapped
        for (from_state, symbol), to_states in base_nfa.d.items():
            for to_state in to_states:
                d[(state_mapping[from_state], symbol)] = {state_mapping[to_state]}

        # Add a new start and accept state
        start_state = 0
        accept_state = state_offset + 1
        K.add(start_state)
        K.add(accept_state)

        # Add epsilon transitions from the new start state to the base NFA start state and accept state
        d[(start_state, EPSILON)] = {state_mapping[base_nfa.q0], accept_state}

        # Add epsilon transitions from the final states of the base NFA to the start state (for repetition)
        for accept_state_base in base_nfa.F:
            # Add epsilon transition from base NFA's final state to the remapped start state
            d[(state_mapping[accept_state_base], EPSILON)] = {state_mapping[base_nfa.q0], accept_state}


        # Set the new start state and final state
        q0 = start_state
        F.add(accept_state)

        return NFA(S, K, q0, d, F)


def parse_regex(regex: str) -> Regex:
    stack = []
    i = 0
    while i < len(regex):
        char = regex[i]

        if char == ' ':
            i += 1
            continue

        elif char == '(':
            paren_count = 1
            sub_expr_start = i + 1
            i += 1
            while paren_count > 0 and i < len(regex):

                if regex[i] == '(':
                    paren_count += 1
                elif regex[i] == ')':
                    paren_count -= 1
                i += 1
            sub_expr_end = i - 1

            sub_expr = regex[sub_expr_start:sub_expr_end]
            sub_regex = parse_regex(sub_expr)
            stack.append(sub_regex)
        elif char == '\\':
            if i + 1 < len(regex):
                if regex[i + 1] == ' ':
                    stack.append(Character(' '))
                elif regex[i + 1] == '(':
                    stack.append(Character('('))
                    i += 1
                elif regex[i + 1] == ')':
                    stack.append(Character(')'))
                    i += 1
                elif regex[i + 1] == '+':
                    stack.append(Character('+'))
                    i += 1
                elif regex[i + 1] == '*':
                    stack.append(Character('*'))
                    i += 1
                elif regex[i + 1] == '/':
                    stack.append(Character('/'))
                    i += 1

            i += 1
        elif char == '\n':
            stack.append(Character('\n'))
            i += 1
        
           #     stack.append(Character(')'))

              
        elif char.isalnum() or char == '-' or char == '.' or char == '_' or char == ':' or char == '@':
            stack.append(Character(char))
            i += 1

        elif char == '[':
            # Procesăm clasele de caractere, de exemplu [0-9]
            i += 1
            class_start = i
            class_end = i
            while class_end < len(regex) and regex[class_end] != ']':
                class_end += 1
            if class_end == len(regex):
                raise ValueError("Unmatched opening bracket '[' in regex.")

            class_content = regex[class_start:class_end]
            i = class_end + 1

            # Verificăm dacă este un interval valid, de exemplu 0-9
            if '-' in class_content:
                parts = class_content.split('-')
                if len(parts) == 2 and parts[0].isalnum() and parts[1].isalnum():
                    # Creăm o instanță a clasei CharacterClass pentru intervalul 0-9
                    stack.append(CharacterClass(parts[0], parts[1]))
                 
        elif char == '+':
            # Procesăm operatorul `+`
            if not stack:
                raise ValueError("Operatorul `+` trebuie să urmeze o expresie validă.")
            expr = stack.pop()
            stack.append(Plus(expr))
            i += 1

        elif char == '*':
       
            if not stack:
                raise ValueError("Invalid regex: '*' operator must follow an expression.")

            expr = stack.pop()
            stack.append(Star(expr))
            i += 1
        
        elif char == '?':
            if not stack:
                raise ValueError("Operatorul `+` trebuie să urmeze o expresie validă.")
            expr = stack.pop()
            stack.append(Question_Mark(expr))
            i += 1

        elif char == '|':
            right_expr = regex[i+1:]
            left_expr = regex[0:i]
            stack.clear()
            left_regex = parse_regex(left_expr)
            right_regex = parse_regex(right_expr)
            stack.append(Union(left_regex, right_regex))
            break
        else:
            raise ValueError(f"Unsupported character: {char}")
    while len(stack) > 1:
        right = stack.pop()
        left = stack.pop()
        stack.append(Concat(left, right))
    return stack[0]
