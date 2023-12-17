# valueIterationAgents.py
# -----------------------


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        '''
        formula:
        V(s) = max(Q(s,a)) for all actions a
        '''
        for _ in range(self.iterations):
            new_values = self.values.copy()
            for state in self.mdp.getStates():
                if  self.mdp.isTerminal(state): continue
                Q_values = [-float('inf')]
                for action in self.mdp.getPossibleActions(state):
                    Q_values.append(self.computeQValueFromValues(state, action))
                new_values[state] = max(Q_values)
            self.values = new_values



    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        '''
        formula:
        Q*(s, a) = sum_s' of T(s, a, s') [R(s, a, s') + gamma V*(s')]

        '''

        Q = 0
        for nextState, T in self.mdp.getTransitionStatesAndProbs(state, action):
            Q += T * (self.mdp.getReward(state, action, nextState) + self.discount * self.values[nextState])
        return Q

        util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        '''
        formula:
        policy(s) = arg_max_{a in actions} Q(s, a)
        '''

        if self.mdp.isTerminal(state): return None

        Q_values = []
        for action in self.mdp.getPossibleActions(state):
            Q_values.append((self.computeQValueFromValues(state, action), action))
        return max(Q_values)[1]
        
        util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)


class PrioritizedSweepingValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"

        predecessors = self.computePredecessors()
        priorityQueue  = util.PriorityQueue()
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state): continue
            maxQ = self.computeMaxQValue(state)
            diff = abs(self.values[state] - maxQ)
            priorityQueue.push(state, -diff)

        for _ in range(self.iterations):
            if priorityQueue.isEmpty(): break
            state = priorityQueue.pop()
            if  self.mdp.isTerminal(state): continue
            maxQ = self.computeMaxQValue(state)
            self.values[state] = maxQ
            for predecessor in predecessors.get(state, set()):
                maxQ = self.computeMaxQValue(predecessor)
                diff = abs(self.values[predecessor] - maxQ)
                if diff > self.theta:
                    priorityQueue.update(predecessor, -diff)


        
    def computeMaxQValue(self, state):
        return max([self.computeQValueFromValues(state, action) for action in self.mdp.getPossibleActions(state)])

    def computePredecessors(self):
        predecessors = {}
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state): continue
            for action in self.mdp.getPossibleActions(state):
                for nextState, T in self.mdp.getTransitionStatesAndProbs(state, action):
                    if T == 0: continue
                    if nextState in predecessors:
                        predecessors[nextState].add(state)
                    else:
                        predecessors[nextState] = {state}
        return predecessors
        