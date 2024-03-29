import random

import environment
import util

test_action_enum = util.enum('a0', 'a1', 'a2')
test_observation_enum = util.enum('o0', 'o1', 'o2')
test_reward_enum = util.enum(r0=3, r1=1, r2=0)

a0 = test_action_enum.a0
a1 = test_action_enum.a1
a2 = test_action_enum.a2

o0 = test_observation_enum.o0
o1 = test_observation_enum.o1
o2 = test_observation_enum.o2

r0 = test_reward_enum.r0
r1 = test_reward_enum.r1
r2 = test_reward_enum.r2


class test(environment.Environment):
    default_probability = 0.5

    # Instance methods.

    def __init__(self, options):

        # Set up the base environment.
        environment.Environment.__init__(self, options = options)

        # Define the acceptable action values.
        self.valid_actions = list(test_action_enum.keys())

        # Define the acceptable observation values.
        self.valid_observations = list(test_observation_enum.keys())

        # Define the acceptable reward values.
        self.valid_rewards = list(test_reward_enum.keys())

        self.probability = self.default_probability
        # end if

        # Make sure the probability value is valid.
        assert 0.0 <= self.probability <= 1.0

        # Set an initial percept.
        self.observation = o0
        self.reward = 0
    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        assert self.is_valid_action(action)

        # Save the action.
        self.action = action

        observation = None
        reward = None

        # Flip the coin, set observation and reward appropriately.
        if action == a0:
            if random.random() > 0.2:
                observation = o0
                reward = r0
            else:
                observation = o2
                reward = r1
        elif action == a1:
            observation = o1
            reward = r1
        elif action == a2:
            observation = o2
            reward = r2
        else:
            print(action)
        # end if

        # Store the observation and reward in the environment.
        self.observation = observation
        self.reward = reward
    # end def