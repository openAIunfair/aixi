from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import random
import sys

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

from pyaixi import environment, util

test_action_enum = util.enum('a0', 'a1', 'a2')
test_observation_enum = util.enum('o0', 'o1', 'o2')
test_reward_enum = util.enum(r0=2, r1=3, r2=10)

a0 = test_action_enum.a0
a1 = test_action_enum.a1
a2 = test_action_enum.a2

o0 = test_observation_enum.o0
o1 = test_observation_enum.o1
o2 = test_observation_enum.o2

r0 = test_reward_enum.r0
r1 = test_reward_enum.r1
r2 = test_reward_enum.r2

# test_action_enum = util.enum('a0', 'a1', 'a2')
# test_observation_enum = util.enum('o0', 'o1', 'o2')
# test_reward_enum = util.enum(r0=0, r1=1, r2=10)
#
# a0 = test_action_enum.a0
# a1 = test_action_enum.a1
# a2 = test_action_enum.a2
#
# o0 = test_observation_enum.o0
# o1 = test_observation_enum.o1
# o2 = test_observation_enum.o2
#
# r0 = test_reward_enum.r0
# r1 = test_reward_enum.r1
# r2 = test_reward_enum.r2

class test(environment.Environment):
    default_probability = 0.5

    # Instance methods.

    def __init__(self, options):
        """ Construct the CoinFlip environment from the given options.

             - `options` is a dictionary of named options and their values.

            The following options in `options` are optional:
             - `coin-flip-p`: the probability that the coin will land on heads. (Defaults to 0.7.)
        """

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
            observation = o0
            reward = r0
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