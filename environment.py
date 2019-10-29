#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from pyaixi import util


class Environment:

    def __init__(self, options={}):
        """ Construct an agent environment.
        """

        # Set the current action to null/None.
        # (Called `m_action` and `getAction` in the C++ version.)
        self.action = None

        # Set whether the environment is finished.
        # (Called `isFinished` in the C++ version.)
        self.is_finished = False

        # Set the current observation to null/None.
        # (Called `m_observation` and `getObservation()` in the C++ version.)
        self.observation = None

        # Store the given options.
        self.options = options

        # Set the current reward to null/None.
        self.reward = None

        # Defines the acceptable action values.
        self.valid_actions = []

        # Define the acceptable observation values.
        self.valid_observations = []

        # Define the acceptable reward values.
        self.valid_rewards = []

    # end def

    def __unicode__(self):
        """ Returns a string representation of this environment instance.
        """
        return "action = " + str(self.action) + ", observation = " + \
               str(self.observation) + ", reward = " + str(self.reward)

    def action_bits(self):
        """ Returns the maximum number of bits required to represent an action.
        """

        return max([util.bits_required(action) for action in self.valid_actions])

    def is_valid_action(self, action):
        """ Returns whether the given action is valid.
        """
        return action in self.valid_actions

    # end def

    def is_valid_observation(self, observation):
        """ Returns whether the given observation is valid.
        """
        return observation in self.valid_observations

    # end def

    def is_valid_reward(self, reward):
        """ Returns whether the given reward is valid.
        """
        return reward in self.valid_rewards

    # end def

    def maximum_action(self):
        """ Returns the maximum possible action.
        """
        return max(self.valid_actions)

    # end def

    def maximum_observation(self):
        """ Returns the maximum possible observation.
        """
        return max(self.valid_observations)

    # end def

    def maximum_reward(self):
        """ Returns the maximum possible reward.
        """

        return max(self.valid_rewards)

    # end def

    def minimum_action(self):
        """ Returns the minimum possible action.
        """
        return max(self.valid_actions)

    # end def

    def minimum_observation(self):
        """ Returns the minimum possible observation.
        """
        return min(self.valid_observations)

    # end def

    def minimum_reward(self):
        """ Returns the minimum possible reward.
        """
        return min(self.valid_rewards)

    # end def

    def observation_bits(self):
        """ Returns the maximum number of bits required to represent an observation.
        """

        return max([util.bits_required(observation) for observation in self.valid_observations])

    # end def

    def percept_bits(self):
        """ Returns the maximum number of bits required to represent a percept.
        """

        return self.observation_bits() + self.reward_bits()

    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """
        # To be overriden by inheriting classes.
        pass

    # end def

    def print(self):
        """ String representation convenience method from the C++ version.
        """
        return str(self)

    # end def

    def reward_bits(self):
        """ Returns the maximum number of bits required to represent a reward.
        """

        # Find the largest sized reward.
        return max([util.bits_required(reward) for reward in self.valid_rewards])
    # end def
# end class
