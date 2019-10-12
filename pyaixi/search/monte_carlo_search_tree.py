#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Define a class to implement a Monte Carlo search tree.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import os
import random
import sys

# Insert the package's parent directory into the system search path, so that this package can be
# imported when the aixi.py script is run directly from a release archive.
PROJECT_ROOT = os.path.realpath(os.path.join(os.pardir, os.pardir))
sys.path.insert(0, PROJECT_ROOT)

from pyaixi import util

# An enumeration type used to specify the type of Monte Carlo search node.
# Chance nodes represent a set of possible observation
# (one child per observation) while decision nodes
# represent sets of possible actions (one child per action).
# Decision and chance nodes alternate.
nodetype_enum = util.enum('chance', 'decision')

# Define some short cuts for ease of reference.
chance_node = nodetype_enum.chance
decision_node = nodetype_enum.decision


class MonteCarloSearchNode:
    """ A class to represent a node in the Monte Carlo search tree.
        The nodes in the search tree represent simulated actions and percepts
        between an agent following an upper confidence bounds (UCB) policy and a generative
        model of the environment represented by a context tree.

        The purpose of the tree is to determine the expected reward of the
        available actions through sampling. Sampling proceeds several time steps
        into the future according to the size of the agent's horizon.
        (`MC_AIXI_CTW_Agent.horizon`)
 
        The nodes are one of two types (`nodetype_enum`), decision nodes are those
        whose children represent actions from the agent and chance nodes are those
        whose children represent percepts from the environment.

        Each MonteCarloSearchNode maintains several bits of information:

          - The current value of the sampled expected reward
            (`MonteCarloSearchNode.mean`, `MonteCarloSearchNode.expectation`).

          - The number of times the node has been visited during the sampling
            (`MonteCarloSearchNode.visits`).

          - The type of the node (MonteCarloSearchNode.type).

          - The children of the node (`MonteCarloSearchNode.children`).
            The children are stored in a dictionary indexed by action (if
            it is a decision node) or percept (if it is a chance node).

        The `MonteCarloSearchNode.sample` method is used to sample from the current node and
        the `MonteCarloSearchNode.selectAction` method is used to select an action according
        to the UCB policy.
    """

    # Class attributes.

    # Exploration constant for the UCB action policy.
    exploration_constant = 2.0

    # Unexplored action bias.
    unexplored_bias = 1000000000.0

    # Instance methods.

    def __init__(self, nodetype):
        """ Create a new search node of the given type.
        """

        # The children of this node.
        # The symbols used as keys at each level may be either action or observation,
        # depending on what type of node this is.
        self.children = {}

        # The sampled expected reward of this node.
        self.mean = 0.0

        # The type of this node indicates whether its children represent actions
        # (decision node) or percepts (chance node).
        assert nodetype in nodetype_enum, "The given value %s is a not a valid node type." % str(nodetype)
        self.type = nodetype

        # The number of times this node has been visited during sampling.
        self.visits = 0

    # end def

    def sample(self, agent, horizon):
        """ Returns the accumulated reward from performing a single sample on this node.

            - `agent`: the agent doing the sampling

            - `horizon`: how many cycles into the future to sample
        """

        reward = 0.0

        if horizon == 0:
            # reach the depth and return the final reward
            return reward

        elif self.type == chance_node:
            # if the node is chance node
            observation, r = agent.generate_percept_and_update()

            if observation not in self.children.keys():
                self.children[observation] = MonteCarloSearchNode(decision_node)

            reward = r + self.children[observation].sample(agent, horizon - 1)

        elif self.visits == 0:
            # if the node has not been explored
            # pick actions through roll out policy and return the sum of reward
            reward = agent.playout(horizon)

        else:

            action = self.select_action(agent)
            agent.model_update_action(action)

            if action not in self.children.keys():
                self.children[action] = MonteCarloSearchNode(chance_node)

            reward = self.children[action].sample(agent, horizon)

        self.mean = (reward + 1.0 * self.mean * self.visits) / (self.visits + 1.0)
        self.visits += 1

        return reward

    # end def

    def select_action(self, agent):
        """ Returns an action selected according to UCB policy.

             - `agent`: the agent which is doing the sampling.
        """

        best_action = None
        max_priority = float('-inf')
        unexplored_list = list()
        for action in agent.environment.valid_actions:

            if action not in self.children.keys() or self.children[action].visits == 0:
                # if this selected child has not been explored
                # a new nod is added to the search tree
                # current_priority = self.unexplored_bias
                unexplored_list.append(action)
            else:

                selected_child = self.children[action]
                # UCB policy in Definition 6

                # m is the remaining search horizon
                m = agent.horizon

                # each instantaneous reward is bounded in the interval [a,b]
                interval = agent.environment.maximum_reward()-agent.environment.minimum_reward()

                # a_ucb(h) = argmax....(Definition 6)
                current_priority = 1.0 * selected_child.mean / (1.0 * m * interval) + \
                                   self.exploration_constant * \
                                   math.sqrt(math.log(self.visits) / selected_child.visits)

                if current_priority > max_priority:
                    best_action = action
                    max_priority = current_priority

        # select action uniformly at random in the unexplored action list.
        if len(unexplored_list) > 0:
            return random.choice(unexplored_list)

        return best_action
    # end def
# end class
