#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines an environment for AIXI agents.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from pyaixi import util

class Environment:
    """ Base class for the various agent environments.
        Each individual environment should inherit from this class and implement the appropriate methods.
        In particular, the constructor should set up the environment as appropriate, including
        setting the initial observation and reward, as well as setting appropriate
        values for the configuration options:
         - `agent-actions`
         - `observation-bits`
         - `reward-bits`
        Following this, the agent and environment interact in a cyclic fashion. The
        agent receives the observation and reward using `Environment.getObservation`
        and `Environment.getReward` before supplying the environment with an action
        via `Environment.performAction`.
        Upon receiving an action, the environment updates the observation and reward.
        At the beginning of each cycle, the value of `Environment::isFinished` is checked.
        If it is true then there is no more interaction between the agent and environment,
        and the program exits. Otherwise the interaction continues indefinitely.
    """

    def __init__(self, options = {}):
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
        # (Called `m_reward` in the C++ version.)
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
    # end def

    # Make a compatible string function for the current Python version.
    if sys.version_info[0] >= 3:
        # For Python 3.
        def __str__(self):
            return self.__unicode__()
        # end def
    else:
        # For Python 2.
        def __str__(self):
            return self.__unicode__().encode('utf8')
        # end def
    # end def

    def action_bits(self):
        """ Returns the maximum number of bits required to represent an action.
        """

        # Find the largest sized observation.
        maximum_bits = 0
        for action in self.valid_actions:
            bits_for_this_action = util.bits_required(action)
            if bits_for_this_action > maximum_bits:
                maximum_bits = bits_for_this_action
            # end if
        # end for

        return maximum_bits
    # end def

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

        # The largest action is the last in the list of valid actions.
        # Else, it's null/None.
        return self.valid_actions[-1] if len(self.valid_actions) > 0 else None
    # end def

    def maximum_observation(self):
        """ Returns the maximum possible observation.
        """

        # The largest observation is the last in the list of valid observations.
        # Else, it's null/None.
        return self.valid_observations[-1] if len(self.valid_observations) > 0 else None
    # end def

    def maximum_reward(self):
        """ Returns the maximum possible reward.
        """

        # The largest reward is the last in the list of valid rewards.
        # Else, it's null/None.
        return self.valid_rewards[-1] if len(self.valid_rewards) > 0 else None
    # end def

    def minimum_action(self):
        """ Returns the minimum possible action.
        """

        # The smallest action is the first in the list of valid actions.
        # Else, it's null/None.
        return self.valid_actions[1] if len(self.valid_actions) > 0 else None
    # end def

    def minimum_observation(self):
        """ Returns the minimum possible observation.
        """

        # The smallest observation is the first in the list of valid observations.
        # Else, it's null/None.
        return self.valid_observations[1] if len(self.valid_observations) > 0 else None
    # end def

    def minimum_reward(self):
        """ Returns the minimum possible reward.
        """

        # The smallest reward is the first in the list of valid rewards.
        # Else, it's null/None.
        return self.valid_rewards[1] if len(self.valid_rewards) > 0 else None
    # end def

    def observation_bits(self):
        """ Returns the maximum number of bits required to represent an observation.
        """

        # Find the largest sized observation.
        maximum_bits = 0
        for observation in self.valid_observations:
            bits_for_this_observation = util.bits_required(observation)
            if bits_for_this_observation > maximum_bits:
                maximum_bits = bits_for_this_observation
            # end if
        # end for

        return maximum_bits
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
        maximum_bits = 0
        for reward in self.valid_rewards:
            bits_for_this_reward = util.bits_required(reward)
            if bits_for_this_reward > maximum_bits:
                maximum_bits = bits_for_this_reward
            # end if
        # end for

        return maximum_bits
    # end def
# end class