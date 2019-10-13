#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines an environment for a biased 1d-Maze.
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

from pyaixi import environment, util
# Define a enumeration to represent 1D_maze actions
# left or right
maze_action_enum = util.enum('aLeft', 'aRight')

# every observation is the same regardless of the agent’s actual location.
maze_observation_enum = util.enum('oObservation')

# Define a enumeration to represent coin flip rewards e.g. win or lose, for correcting predicting
# the coin flip.
maze_reward_enum = util.enum('rLose', 'rWin')

# Define some shorthand notation for ease of reference.
aLeft = maze_action_enum.aLeft
aRight = maze_action_enum.aRight

oObservation = maze_observation_enum.oObservation

rLose = maze_reward_enum.rLose
rWin = maze_reward_enum.rWin

class Maze(environment.Environment):
    """

            Domain characteristics:

            - environment: "Maze"
            - maximum action: 1 (1 bit)
            - maximum observation: 1 (1 bit)
            - maximum reward: 1 (1 bit)


        """
    def __init__(self, options={}):
        # Set up the base environment.
        environment.Environment.__init__(self, options=options)

        # Define the acceptable action values.
        self.valid_actions = list(maze_action_enum.keys())

        # Define the acceptable observation values.
        self.valid_observations = list(maze_observation_enum.keys())

        # Define the acceptable reward values.
        self.valid_rewards = list(maze_reward_enum.keys())

        # Set an initial percept.
        self.observation = oObservation
        self.reward = 0
        self.col = random.randint(0, 3)
    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        assert self.is_valid_action(action)

        # Save the action.
        self.action = action

        self.col_to = (-1 if action == aLeft else 0) + (1 if action == aRight else 0)
        self.col_to = min(max(self.col_to + self.col, 0), 3)
        self.row = self.row_to
        self.reward = (1 if self.col_to == 2 else 0)


        return oObservation, self.reward
    # end def

    def print(self):
        """ Returns a string indicating the status of the environment.
        """

        message = "reward = %d" % self.reward + os.linesep
        for c in range(4):
            if self.row == c:
                message += "A"
            else:
                message += "*"

        return message
    # end def
