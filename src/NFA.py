from .DFA import DFA
from dataclasses import dataclass
from collections.abc import Callable
from typing import TypeVar, Generic

EPSILON = ''  # This is how epsilon is represented in the transition function of NFAs

STATE = TypeVar('STATE')
OTHER_STATE = TypeVar('OTHER_STATE')

@dataclass
class NFA(Generic[STATE]):
    S: set[str]  # Alphabet
    K: set[STATE]  # States
    q0: STATE  # Initial state
    d: dict[tuple[STATE, str], set[STATE]]  # Transition function
    F: set[STATE]  # Final states

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        """
        Compute the epsilon closure of a given state.
        :param state: The state for which to compute the epsilon closure.
        :return: A set of states reachable from the input state using only epsilon transitions.
        """
        closure = set()
        stack = []
        stack.append(state)

        t = True
        while stack:
            t = False
            current = stack.pop()
            if current not in closure:
                closure.add(current)
                for elem in self.d.get((current, EPSILON), set()) - closure:
                    stack.append(elem)
        return closure

    def subset_construction(self) -> DFA[frozenset[STATE]]:

        states = []
        states_f = set()
        transitions = {}

        l = []
        l.append(frozenset(self.epsilon_closure(self.q0)))
        current1 = []
   
        t1 = True
        
        for c in l:
            
            for alphabet in self.S:
                epsilon = []
                for state in c:
                    if self.d.get((state,alphabet)) is not None:
                        t = list(self.d.get((state,alphabet)))
                        for i in range(len(t)):
                            for target1 in self.epsilon_closure(t[i]):
                                if target1 not in epsilon:
                                    epsilon.append(target1)

                if frozenset(set(epsilon)) != frozenset():
                 
                    if frozenset(set(epsilon)) not in current1:
                        l.append(frozenset(set(epsilon)))
            if c not in current1:
                current1.append(c)

       
        for current in current1:
            for alphabet in self.S:
                epsilon = []
                for state in current:
                    if self.d.get((state,alphabet)) is not None:
                        t = list(self.d.get((state,alphabet)))
                        for i in range(len(t)):
                            for target1 in self.epsilon_closure(t[i]):
                                if target1 not in epsilon:
                                    epsilon.append(target1)
                if frozenset(set(epsilon)) == frozenset():
                    transitions[(current, alphabet)] = frozenset({'x'})
                    if frozenset({'x'}) not in states:
                        states.append(frozenset({'x'}))
                        for alphabet in self.S:
                            transitions[(frozenset({'x'}), alphabet)] = frozenset({'x'})
                else:
                    transitions[(current, alphabet)] = frozenset(set(epsilon))
            states.append(current)
        
        for current in current1:
            for state in current:
                if state in self.F:
                    states_f.add(current)
        return DFA(
            S=self.S,
            K=set(states),
            d=transitions,
            q0=frozenset(self.epsilon_closure(self.q0)),
            F=states_f,
        )

    def remap_states(self, f: Callable[[STATE], OTHER_STATE]) -> 'NFA[OTHER_STATE]':
        pass
