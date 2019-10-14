#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines an environment for Tic Tac Toe.
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

tictactoe_observation_enum = util.enum('oEmpty', 'oAgent', 'oOpponent')

# all rewards add 3
tictactoe_reward_enum = util.enum(rInvalid=0, rLoss=1, rNull=3, rDraw=4, rWin=5)

# Define some shorthand notation for ease of reference.
oEmpty = tictactoe_observation_enum.oEmpty
oAgent = tictactoe_observation_enum.oAgent
oOpponent = tictactoe_observation_enum.oOpponent

rInvalid = tictactoe_reward_enum.rInvalid
rLoss = tictactoe_reward_enum.rLoss
rNull = tictactoe_reward_enum.rNull
rDraw = tictactoe_reward_enum.rDraw
rWin = tictactoe_reward_enum.rWin


class Tic_Tac_Toe(environment.Environment):
    """
        Domain characteristics:
        - environment: "tictactoe"
        - maximum action: 8 (4 bits)
        - maximum observation: 174672 (18 bits)
          - 174672 (decimal) = 101010101010101010 (binary)
        - maximum reward: 5 (3 bits)
    """

    # Instance methods.

    def __init__(self, options={}):

        environment.Environment.__init__(self, options=options)

        self.valid_actions = xrange(0, 16)
        # Define the acceptable observation values.
        self.valid_observations = xrange(0, 174672 + 1)

        # Define the acceptable reward values.
        self.valid_rewards = list(tictactoe_reward_enum.keys())

        # Set the initial reward.
        self.reward = 0

        # Set up the game.
        self.set_game()

    # end def

    def set_game(self):
        self.board = {}
        for r in range(3):
            for c in range(3):
                # Ensure the row exists.
                if r not in self.board:
                    self.board[r] = {}
                self.board[r][c] = oEmpty

        # Set an initial observation.
        self.compute_observation()
        self.steps = 0

    def check_win(self):

        # Check row
        for r in range(3):
            if (self.board[r][0] != oEmpty and \
                    self.board[r][0] == self.board[r][1] and \
                    self.board[r][1] == self.board[r][2]):
                return True

        # Check col
        for c in range(3):
            if (self.board[0][c] != oEmpty and \
                    self.board[0][c] == self.board[1][c] and \
                    self.board[1][c] == self.board[2][c]):
                return True

        # Check the diagonals.
        if (self.board[1][1] != oEmpty and \
                self.board[0][0] == self.board[1][1] and \
                self.board[1][1] == self.board[2][2]):
            return True

        if (self.board[1][1] != oEmpty and \
                self.board[0][2] == self.board[1][1] and \
                self.board[1][1] == self.board[2][0]):
            return True

        return False

    def compute_observation(self):

        self.observation = 0
        for r in range(3):
            for c in range(3):
                self.observation = self.board[r][c] + (4 * self.observation)

    def perform_action(self, action):

        assert self.is_valid_action(action)

        self.action = action

        self.steps += 1

        # Decode the action

        x = action // 4
        y = action % 4

        r = 0
        c = 0
        if x == 0:
            if y == 0:
                r, c = 0, 0
            elif y == 1:
                r, c = 0, 1
            elif y == 2:
                r, c = 1, 0
            elif y == 3:
                r, c = 1, 1
        elif x == 1:
            if y == 0:
                r, c = 0, 1
            elif y == 1:
                r, c = 0, 2
            elif y == 2:
                r, c = 1, 1
            elif y == 3:
                r, c = 1, 2
        elif x == 2:
            if y == 0:
                r, c = 1, 0
            elif y == 1:
                r, c = 1, 1
            elif y == 2:
                r, c = 2, 0
            elif y == 3:
                r, c = 2, 1
        else:
            if y == 0:
                r, c = 1, 1
            elif y == 1:
                r, c = 1, 2
            elif y == 2:
                r, c = 2, 1
            elif y == 3:
                r, c = 2, 2

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
        elif self.steps == 5:
            # after 5 steps, game must draw if no one win
            self.reward = rDraw
            self.set_game()
            return

        # The environment makes a random play. yuanchenhua version
        empty_cell = []
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == oEmpty:
                    empty_cell.append((r, c))

        env_random_choice = random.choice(empty_cell)
        self.board[env_random_choice[0]][env_random_choice[1]] = oOpponent

        # The environment makes a random play. official version

        # while (self.board[r][c] != oEmpty):
        #     # Keep picking board positions at random until we find an unoccupied spot.
        #     r = random.randrange(0, 3)
        #     c = random.randrange(0, 3)
        #     # end while
        # 
        #     # If we're here, we've got an unoccupied spot.
        # self.board[r][c] = oOpponent

        # check if opponent win
        if self.check_win():
            self.reward = rLoss
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
        for r in xrange(0, 3):
            for c in xrange(0, 3):
                b = self.board[r][c]
                message += "." if b == oEmpty else ("o" if b == oAgent else "x")
            message += os.linesep
        message += os.linesep

        return message
