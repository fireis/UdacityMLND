import random
import math
import numpy as np

import operator

from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """

    def __init__(self, env, learning=True, epsilon=1, alpha=0.001):
        super(LearningAgent, self).__init__(env)  # Set the agent in the evironment
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning  # Whether the agent is expected to learn
        self.Q = dict()  # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon  # Random exploration factor
        self.alpha = alpha  # Learning factor

        # trial number counter
        self.trialN = 1


    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)



        if testing:
            self.epsilon = 0
            self.alpha = 0
        else:
            # linear decay
            # self.epsilon = self.epsilon - 0.05
            # self.epsilon = self.epsilon - self.alpha

            # exponential decay
            self.epsilon = math.exp(-self.alpha * self.trialN)

            # other decays
            # self.epsilon =math.pow(self.alpha, self.trialN)
            # self.epsilon = math.cos(self.alpha * self.trialN)

            #alpha decay
            self.alpha = self.alpha * math.pow(1.00001, self.trialN)

            self.trialN += 1

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the
            environment. The next waypoint, the intersection inputs, and the deadline
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint()  # The next waypoint
        inputs = self.env.sense(self)  # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        # removes right state as us right-of-way makes it irrelevant
        inputs.pop('right')

        state = (str(inputs), waypoint)

        return state

    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        maxQ = 0

        for action in self.valid_actions:
            qVal = self.Q[state][action]
            if qVal > maxQ:
                maxQ = qVal

        return maxQ

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        initial_q = 0
        if self.learning:
            if state not in self.Q:
                self.Q[state] = dict()
                for action in self.valid_actions:
                    self.Q[state][action] = initial_q

        return

    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()

        if self.learning:

            if self.epsilon > random.random():
                action = random.choice(self.valid_actions)

            else:
                maxQ = self.get_maxQ(state)

                # find action associated to maxQ

                actions = [action for action in self.valid_actions if self.Q[state][action] == maxQ ]
                # if the same maxQ is shared by two actions, chooses randomly which action to take
                action = random.choice(actions)

        else:
            action = self.valid_actions[np.random.randint(0, 3, 1)]

        return action

    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards
            when conducting learning. """


        if self.learning:
            qValue = self.Q[state][action]
            # Update rule not using gamma
            self.Q[state][action] = (reward * self.alpha) + (qValue * (1 - self.alpha))
        return

    def update(self):
        """ The update function is called when a time step is completed in the
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()  # Get current state
        self.createQ(state)  # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action)  # Receive a reward
        self.learn(state, action, reward)  # Q-learn

        return


def run():
    """ Driving function for running the simulation.
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment(verbose=False)

    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent)

    ##############
    # Follow the driving agent
    # Flags:
    # enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, update_delay=0, display=True, log_metrics=True, optimized=True)

    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=100, tolerance=0.00001)


if __name__ == '__main__':
    run()
