from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

STATE = TypeVar('STATE')

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]
    
    def accept(self, word: str) -> bool:

        s = self.q0

        for ch in word:
            if(s,ch) in self.d:
                s = self.d[(s,ch)]
        
        if s in self.F:
            return True
        else:
            return False


    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
      
        pass
    
    
    def minimize(self) -> 'DFA':
        states_l = list(self.K)


        v = {}

        for i in range(len(states_l)):
            for j in range(len(states_l)):
                v[(states_l[i], states_l[j])] = False

        for i in range(len(states_l)):
            for j in range(i):
                if (((states_l[i] in self.F) and (states_l[j] not in self.F)) or ((states_l[i] not in self.F) and (states_l[j] in self.F))):
                    v[(states_l[i],states_l[j])] = True

        t = 1
        while t != 0:
            t = 0
            for i in range(len(states_l)):
                for j in range(0,i):
                    if v[(states_l[i], states_l[j])] == False:
                        for alphabet in self.S:
                            if v[(self.d.get((states_l[i], alphabet)), self.d.get((states_l[j], alphabet)))] == True:
                                v[(states_l[i], states_l[j])] = True
                                t = 1
                            elif v[(self.d.get((states_l[j], alphabet)),self.d.get((states_l[i], alphabet)) )] == True:
                                v[(states_l[i], states_l[j])] = True
                                t = 1

    
        visited = set()
        states_minimize = set()
       
        for i in range(len(states_l)):
            if states_l[i] not in visited:

                group1 = set()
                for j in range(i+1, len(states_l)):
                    if states_l[j] not in visited:
                        if v[(states_l[i], states_l[j])] == False and v[(states_l[j], states_l[i])] == False:
                            group1.add(states_l[j])
                group1.add(states_l[i])
                visited.update(group1)
                states_minimize.add(frozenset(group1))
        
        transitions = {}
        final_states = set()
        
        for alphabet in self.S:
            for group in states_minimize:
                for i in range(len(list(group))):
                    for state1 in states_minimize:
                        if self.d.get((list(group)[i], alphabet)) in state1:
                            x = state1
                    transitions[(frozenset(group), alphabet)] = frozenset(x)
    
        state1 = list(states_minimize)
        for group in states_minimize:
            for i in range(len(list(group))):
                if list(group)[i] in self.F:
                    final_states.add(frozenset(set(group)))

        for state in states_minimize:
            if self.q0 in state:
                x1 = state
        start_state = x1

        return DFA(
            S=self.S,
            K=states_minimize,
            q0=start_state,
            d=transitions,
            F=final_states
        )


        