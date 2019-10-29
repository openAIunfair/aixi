#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines an environment for Extended Tiger

Created by Fan Ji u6356164
Date: 12/10/2019
"""

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

import environment
import util

# Define a enumeration to represent extended tiger actions,
# including stand, listen, open the left door, and open the right door
extended_tiger_action_enum = util.enum('aStand', 'aListen', 'aOpenLeft', 'aOpenRight')

# Define a enumeration to represent extended tiger observations
# including the tiger hiding behind left door or right door.
# before action aListen, 'oNull' represent the observation
extended_tiger_observation_enum = util.enum('oNull', 'oLeft', 'oRight')

# Define a enumeration to represent extended tiger rewards
extended_tiger_reward_enum = util.enum(rInvalid=90, rListen=99, rStand=99, rTiger=0, rGold=130)

# Define some shorthand notation for ease of reference.
aStand = extended_tiger_action_enum.aStand
aListen = extended_tiger_action_enum.aListen
aOpenLeft = extended_tiger_action_enum.aOpenLeft
aOpenRight = extended_tiger_action_enum.aOpenRight

oNull = extended_tiger_observation_enum.oNull
oLeft = extended_tiger_observation_enum.oLeft
oRight = extended_tiger_observation_enum.oRight

rInvalid = extended_tiger_reward_enum.rInvalid
rListen = extended_tiger_reward_enum.rListen
rStand = extended_tiger_reward_enum.rStand
rTiger = extended_tiger_reward_enum.rTiger
rGold = extended_tiger_reward_enum.rGold


class ExtendedTiger(environment.Environment):
    """ Extended Tiger. The problem setting is similar to Tiger, except that now the
        agent begins sitting down on a chair. The actions available to the agent are: stand,
        listen, open the left door, and open the right door. Before an agent can successfully
        open one of the two doors, it must stand up. However, the listen action only provides
        information about the tiger’s whereabouts when the agent is sitting down. Thus it
        is necessary for the agent to plan a more intricate series of actions before it sees
        the optimal solution. Any invalid action (e.g. attempting to stand when already
        standing) will result in a penalty of 10.

        Domain characteristics:

        - environment: "extended_tiger"
        - maximum action: 4 (2 bits)
        - maximum observation: 3 (2 bits)
        - maximum reward: 130 (8 bits)

        Configuration options:
        - `tiger-listen-p`:  If the agent performs the listen action, it receives a penalty of -
                        1 and an observation that correctly describes where the tiger is with 0.85 probability.
    """

    # Instance attributes.

    # Set the default probability for the biased coin, when none is supplied from the options.
    default_probability = 1

    # Instance methods.

    def __init__(self, options={}):
        """ Construct the ExtendedTiger environment from the given options.

             - `options` is a dictionary of named options and their values.

            The following options in `options` are optional:
             - `tiger_listen`: the probability that the listen gives a correct result. (Defaults to 0.85.)
        """

        # Set up the base environment.
        environment.Environment.__init__(self, options=options)

        # Define the acceptable action values.
        self.valid_actions = list(extended_tiger_action_enum.keys())

        # Define the acceptable observation values.
        self.valid_observations = list(extended_tiger_observation_enum.keys())

        # Define the acceptable reward values.
        self.valid_rewards = list(extended_tiger_reward_enum.keys())

        # Determine the probability of the coin landing on heads.
        if 'tiger_listen' not in options:
            options["tiger_listen"] = self.default_probability
        # end if
        self.probability = float(options["tiger_listen"])

        # Make sure the probability value is valid.
        assert 0.0 <= self.probability <= 1.0

        # Set an initial percept.
        self.observation = oNull
        self.reward = 0

        # Set the initial environment by randomly put tiger and gold behind different door
        self.tiger = oLeft if random.random() < 0.5 else oRight
        self.gold = oRight if self.tiger == oLeft else oLeft
        self.sitting = True

    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        assert self.is_valid_action(action)

        # Save the action.
        self.action = action

        self.reward = rInvalid

        if action == aListen and self.sitting:
            self.observation = self.tiger if random.random() > self.default_probability else self.gold
            self.reward = rListen
        elif action == aStand and self.sitting:
            self.reward = rStand
            self.sitting = False
        elif action == aOpenLeft and not self.sitting:
            self.reward = rGold if self.tiger == oRight else rTiger
            self.tiger = oLeft if random.random() < 0.5 else oRight
            self.gold = oRight if self.tiger == oLeft else oLeft
            self.sitting = True
            self.observation = oNull
        elif action == aOpenRight and not self.sitting:
            self.reward = rGold if self.tiger == oLeft else rTiger
            self.tiger = oLeft if random.random() < 0.5 else oRight
            self.gold = oRight if self.tiger == oLeft else oLeft
            self.sitting = True
            self.observation = oNull



         ## invalid action
    # end def

    def print(self):
        """ Returns a string indicating the status of the environment.
        """
        action = {aListen: 'listen', aStand: 'stand', aOpenRight: 'open the right door',
                  aOpenLeft: 'open the left door'}

        reward = {rInvalid: 'invalid action(-10)',
                  rTiger: 'eaten by tiger(-100)',
                  rGold: 'find the gold(30)',
                  rStand: 'Stand up(-1)',
                  rListen: 'listen(-1)'}

        observation = {oNull: 'have not attempted to listen',
                       oRight: 'tiger should be at right door',
                       oLeft: 'tiger should be at left door'}

        sitting = {True: 'sitting', False: 'standing'}

        message = 'After ' + action[self.action] + ' Observation is ' + observation[self.observation] + ' Reward is ' \
                  + reward[self.reward] + ' current status: ' + sitting[self.sitting]
        return message
    # end def
# end class
