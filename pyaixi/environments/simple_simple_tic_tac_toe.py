#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines an environment for Simplest Tic Tac Toe.
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

# Ensure xrange is defined on Python 3.
from six.moves import xrange
from pyaixi import environment, util

simple_tictactoe_observation_enum = util.enum('oEmpty', 'oAgent')

# all rewards add 3
simple_tictactoe_reward_enum = util.enum(rInvalid=0, rNull=3, rWin=10)

# Define some shorthand notation for ease of reference.
oEmpty = simple_tictactoe_observation_enum.oEmpty
oAgent = simple_tictactoe_observation_enum.oAgent


rInvalid = simple_tictactoe_reward_enum.rInvalid
rNull = simple_tictactoe_reward_enum.rNull
rWin = simple_tictactoe_reward_enum.rWin


class Simple_Tic_Tac_Toe(environment.Environment):
    """
        Domain characteristics:
        - environment: "tictactoe"
        - maximum action: 9 (4 bits)
        - maximum observation:   512 (9 bits)
        - maximum reward: 5 (3 bits)
    """

    # Instance methods.

    def __init__(self, options={}):

        environment.Environment.__init__(self, options=options)

        self.valid_actions = xrange(0, 4)
        # Define the acceptable observation values.
        self.valid_observations = xrange(0, 16)

        # Define the acceptable reward values.
        self.valid_rewards = list(simple_tictactoe_reward_enum.keys())

        # Set the initial reward.
        self.reward = 0

        # Set up the game.
        self.set_game()

    # end def

    def set_game(self):
        self.board = {}
        for r in range(2):
            for c in range(2):
                # Ensure the row exists.
                if r not in self.board:
                    self.board[r] = {}
                self.board[r][c] = oEmpty

        # Set an initial observation.
        self.compute_observation()

    def check_win(self):

        # Check the diagonals.
        if (self.board[1][1] != oEmpty and \
                self.board[0][0] == self.board[1][1]):
            return True

        if (self.board[0][1] != oEmpty and \
                self.board[1][0] == self.board[0][1]):
            return True

        return False

    def compute_observation(self):

        self.observation = 0
        for r in range(2):
            for c in range(2):
                self.observation = self.board[r][c] + (2 * self.observation)

    def perform_action(self, action):

        assert self.is_valid_action(action)

        self.action = action

        # Decode the action

        r = action // 2
        c = action % 2

        # r = 0
        # c = 0
        # if x == 0:
        #     if y == 0:
        #         r, c = 0, 0
        #     elif y == 1:
        #         r, c = 0, 1
        #     elif y == 2:
        #         r, c = 1, 0
        #     elif y == 3:
        #         r, c = 1, 1
        # elif x == 1:
        #     if y == 0:
        #         r, c = 0, 1
        #     elif y == 1:
        #         r, c = 0, 2
        #     elif y == 2:
        #         r, c = 1, 1
        #     elif y == 3:
        #         r, c = 1, 2
        # elif x == 2:
        #     if y == 0:
        #         r, c = 1, 0
        #     elif y == 1:
        #         r, c = 1, 1
        #     elif y == 2:
        #         r, c = 2, 0
        #     elif y == 3:
        #         r, c = 2, 1
        # else:
        #     if y == 0:
        #         r, c = 1, 1
        #     elif y == 1:
        #         r, c = 1, 2
        #     elif y == 2:
        #         r, c = 2, 1
        #     elif y == 3:
        #         r, c = 2, 2

        # invalid move, reward and reset game
        if self.board[r][c] != oEmpty:
            self.reward = rInvalid
            self.set_game()
            return

        # The agent move
        self.board[r][c] = oAgent

        # check win
        if self.check_win():
            self.reward = rWin
            self.set_game()
            return

        # if the game dose not end
        self.reward = rNull
        self.compute_observation()

        return self.observation, self.reward

    def print(self):
        message = "action = %s, observation = %s, reward = %s (%d), board:" % \
                  (self.action, self.observation, self.reward, (self.reward - 3)) + os.linesep

        # Display the current state of the board.
        for r in range(0, 2):
            for c in range(0, 2):
                b = self.board[r][c]
                message += "." if b == oEmpty else ("A" if b == oAgent else "x")
            message += os.linesep
        message += os.linesep

        return message
