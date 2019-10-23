#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines an environment for a M shape Cheese Maze.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

from pyaixi import environment, util

action_enum = util.enum('aUp', 'aRight', 'aDown', 'aLeft')

aUp = action_enum.aUp
aRight = action_enum.aRight
aDown = action_enum.aDown
aLeft = action_enum.aLeft

class Square:
    def __init__(self, observation):
        self.observation = observation
        self.north = None
        self.east = None
        self.south = None
        self.west = None

# Describe the maze
l7 = Square(7)
l5 = Square(5)
l9 = Square(9)
l10 = Square(10)
m8 = Square(8)
m5 = Square(5)
m7 = Square(7)
r10 = Square(10)
r12 = Square(12)
r5 = Square(5)
r7 = Square(7)

l7.north = l5
l5.north = l9
l5.south = l7
l9.east = l10
l9.south = l5
l10.east = m8
l10.west = l9
m8.east = r10
m8.south = m5
m8.west = l10
m5.north = m8
m5.south = m7
m7.north = m5
r10.east = r12
r10.west = m8
r12.south = r5
r12.west = r10
r5.north = r12
r5.south = r7
r7.north = r5


class CheeseMaze(environment.Environment):
    """
            Domain characteristics:
            - environment: "Maze"
            - maximum action: 3 (2 bit)
            - maximum observation: 15 (4 bit)
            - maximum reward: 20 (5 bit)
        """
    def __init__(self, options={}):
        # Set up the base environment.
        environment.Environment.__init__(self, options=options)

        # Define the acceptable action values.
        self.valid_actions = list(action_enum.keys())

        # Define the acceptable observation values.
        # 15 stands for 1111, i.e. all walls on 4 side
        self.valid_observations = list(range(15 + 1))

        # Define the acceptable reward values.
        self.valid_rewards = list(range(20 + 1))

        # Set an initial percept.
        self.location = l10
        self.observation = l10.observation
        self.reward = 0
    # end def

    def perform_action(self, action):
        """ Receives the agent's action and calculates the new environment percept.
        """

        assert self.is_valid_action(action)

        # Save the action.
        self.action = action

        if action == aUp:
            next_loc = self.location.north
        if action == aRight:
            next_loc = self.location.east
        if action == aDown:
            next_loc = self.location.south
        if action == aLeft:
            next_loc = self.location.west

        if next_loc is not None:
            if next_loc == m7:
                self.reward = 20
                # self.is_finished = True
                # reset the environment
                self.location = l10
                self.observation = l10.observation
            else:
                self.location = next_loc
                self.observation = self.location.observation
                self.reward = 9
        else:
            self.reward = 0
    # end def

    def print(self):
        """ Returns a string indicating the status of the environment.
        """

        action_name = {aUp: "move up", aRight: "move right", aDown: "move down", aLeft: "move left"}

        coordinate = {
            l7: (1, 3),
            l5: (1, 2),
            l9: (1, 1),
            l10: (2, 1),
            m8: (3, 1),
            m5: (3, 2),
            m7: (3, 3),
            r10: (4, 1),
            r12: (5, 1),
            r5: (5, 2),
            r7: (5, 3)
        }

        message = "action: " + action_name[self.action] + \
                  ", observation: " + str(self.observation) + \
                  ", reward: %d" % self.reward
        if self.reward == 0:
            message += ", hitted the wall, maze is unchanged\n"
        else:
            maze = ""
            m_x, m_y = coordinate[self.location]
            for y in range(5):
                for x in range(7):
                    if x % 7 == 0:
                        maze += '\n'
                    if m_x == x and m_y == y:
                        maze += " m "
                    else:
                        if x == 3 and y == 3:
                            maze += " c "
                        else:
                            if 0 < x and x < 6 and y == 1:
                                maze += "   "
                            else:
                                if (x == 1 or x == 3 or x == 5) and 1 < y and y < 4:
                                    maze += "   "
                                else:
                                    maze += " w "

            if self.reward == 20:
                message += ", the agent wins this round! Maze is resetted:\n"
                message += maze + "\n"
            else:
                message += ", maze: \n" + maze + "\n"

        return message
    # end def
