#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines a class for the MC-AIXI-CTW agent.
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

import monte_carlo_search_tree
import util
import ctw_context_tree
import agent

from agent import action_update, percept_update
from monte_carlo_search_tree import decision_node


class MC_AIXI_CTW_Undo:
    """ A class to save details from a MC-AIXI-CTW agent to restore state later.
    """

    # Instance methods.

    def __init__(self, agent):
        """ Store values from the given agent that can be used to revert that agent to a previous state.
        """

        # Copy the main attributes of the given agent into this class.
        self.age = agent.age
        self.total_reward = agent.total_reward
        self.history_size = agent.history_size()
        self.last_update = agent.last_update
    # end def


# end class


class MC_AIXI_CTW_Agent(agent.Agent):
    """ This class represents a MC-AIXI-CTW agent.

        It includes much of the high-level logic for choosing suitable actions.
        In particular, the agent maintains an internal model of the environment using
        a context tree.

        It uses this internal model to to predict the probability of future outcomes:

         - `get_predicted_action_probability()`
         - `percept_probability()`

        as well as to generate actions and precepts according to the model distribution:

         - `generate_action()`
         - `gen_percept()`
         - `generate_percept_and_update()`
         - `generate_random_action()`

        Actions are chosen via the UCT algorithm, which is orchestrated by a
        high-level search function and a playout policy:

         - `search()`
         - `playout()`
         - `horizon`
         - `mc_simulations`
         - `search_tree`

        Several functions decode/encode actions and percepts between the
        corresponding types (i.e. `action_enum`, `percept_enum`) and generic
        representation by symbol lists:

         - `decode_action()`
         - `decode_observation()`
         - `decode_percept()`
         - `decode_reward()`
         - `encode_action()`
         - `encode_percept()`

        There are various attributes which describe the agent and its
        interaction with the environment so far:

         - `age`
         - `average_reward`
         - `history_size()`
         - `horizon`
         - `last_update`
         - `maximum_action()`
         - `maximum_bits_needed()`
         - `maximum_reward()`
         - `total_reward`
    """

    # Instance methods.

    def __init__(self, environment=None, options=None, ctw=None):
        """ Construct a MC-AIXI-CTW learning agent from the given configuration values and the environment.

             - `environment` is an instance of the pyaixi.Environment class that the agent with interact with.
             - `options` is a dictionary of named options and their values.

            `options` must contain the following mandatory options:
             - `agent-horizon`: the agent's planning horizon.
             - `ct-depth`: the depth of the context tree for this agent, in symbols/bits.
             - `mc-simulations`: the number of simulations to run when choosing new actions.

            The following options are optional:
             - `learning-period`: the number of cycles the agent should learn for.
                                  Defaults to '0', which is indefinite learning.
        """

        # Set up the base agent options, which handles getting and setting the learning period, amongst other basic
        # values.
        agent.Agent.__init__(self, environment=environment, options=options)

        # The agent's context tree depth.
        # Retrieved from the given options under 'ct-depth'. Mandatory.
        if options is None:
            options = {}
        assert 'ct-depth' in options, \
            "The required 'ct-depth' context tree depth option is missing from the given options."

        self.depth = int(options['ct-depth'])

        if ctw is None:
            self.context_tree = ctw_context_tree.CTWContextTree(self.depth)
        else:
            self.context_tree = ctw

        # The length of the agent's planning horizon.
        # Retrieved from the given options under 'agent-horizon'. Mandatory.
        assert 'agent-horizon' in options, \
            "The required 'agent-horizon' search horizon option is missing from the given options."
        self.horizon = int(options['agent-horizon'])

        # The number of simulations to conduct when choosing new actions via the UCT algorithm.
        # Retrieved from the given options under 'mc-simulations'. Mandatory.
        assert 'mc-simulations' in options, \
            "The required 'mc-simulations' Monte Carlo simulations count option is missing from the given options."
        self.mc_simulations = int(options['mc-simulations'])

        self.reset()

    # end def

    def decode_action(self, symbol_list):
        """ Returns the action decoded from the beginning of the given list of symbols.

            - `symbol_list`: the symbol list to decode the action from.
        """

        return util.decode(symbol_list, self.environment.options['action-bits'])

    # end def

    def decode_observation(self, symbol_list):
        """ Returns the observation decoded from the given list of symbols.

            - `symbol_list`: the symbol list to decode the observation from.
        """

        return util.decode(symbol_list, self.environment.options['observation-bits'])
    # end def

    def decode_reward(self, symbol_list):
        """ Returns the reward decoded from the beginning of the given list of symbols.

            - `symbol_list`: the symbol list to decode the reward from.
        """

        return util.decode(symbol_list, self.environment.options['reward-bits'])
    # end def

    def decode_percept(self, symbol_list):
        """ Returns the percept (observation and reward) decoded from the beginning of
            the given list of symbols.

            - `symbol_list`: the symbol list to decode the percept from.
        """

        # Check if we've got exactly enough symbols.
        reward_bits = self.environment.options['reward-bits']
        observation_bits = self.environment.options['observation-bits']

        assert len(symbol_list) >= (reward_bits + observation_bits), \
            "The given symbol list isn't long enough to contain a percept."

        # Get the reward symbols from the given symbol list, starting with the
        # reward, then getting the observation from the list after that.
        reward_symbols = symbol_list[:reward_bits]
        observation_symbols = symbol_list[reward_bits:(reward_bits + observation_bits)]

        # Decode the obtained symbols.
        reward = self.decode_reward(reward_symbols)
        observation = self.decode_observation(observation_symbols)

        # Return the decoded percept as a tuple of observation and reward.
        return observation, reward

    # end def

    def encode_action(self, action):
        """ Returns the given action encoded as a list of symbols.

            - `action`: the action to encode.
        """

        return util.encode(action, self.environment.options['action-bits'])

    # end def

    def encode_percept(self, observation, reward):
        """ Returns the given percept (an observation, reward part) as a list of symbols.

            - `observation`: the observation part of the percept to encode.
            - `reward`: the reward part of the percept to encode.
        """

        # Add first the encoded reward, then the encoded observation to the list of output symbols.
        symbol_list = util.encode(reward, self.environment.options['reward-bits'])
        symbol_list += util.encode(observation, self.environment.options['observation-bits'])

        # Return the generated list.
        return symbol_list

    # end def

    def generate_action(self):
        """ Returns an action generated according to the agent's history
            statistics by doing rejection sampling from the context tree.
        """

        assert self.last_update == percept_update, "An action after a percept"

        t = 0
        action = None

        while action not in self.environment.valid_actions and t <= 5:
            action = self.decode_action(self.context_tree.generate_random_symbols(self.environment.options['action-bits']))
            t += 1

        if action in self.environment.valid_actions:
            return action

        return max(self.environment.valid_actions, key=lambda x: self.get_predicted_action_probability(x))
    # end def

    def generate_percept(self):
        """ Returns a percept (an observation, reward pair) distributed according to the agent's history
            statistics by sampling from the context tree.
        """

        assert self.last_update == action_update, "A percept after an action"

        observation, reward = self.decode_percept(self.context_tree.generate_random_symbols(self.environment.options['percept-bits']))

        return observation, reward
    # end def

    def generate_percept_and_update(self):
        assert self.last_update == action_update, "Can only perform an percept update after an action update"

        observation, reward = self.generate_percept()
        self.model_update_percept(observation, reward)

        return observation, reward

    # end def

    def get_predicted_action_probability(self, action):
        binary_action = self.encode_action(action)

        return self.context_tree.predict(binary_action)

    def get_predicted_percept_probability(self, observation, reward):


        binary_percept = self.encode_percept(observation,reward)

        return self.context_tree.predict(binary_percept)

    # end def

    def history_size(self):
        """ Returns the length of the stored history for an agent.
        """

        return len(self.context_tree.history)

    # end def

    def maximum_bits_needed(self):
        """ Returns the maximum number of bits needed to represent actions or percepts.
            NOTE: this is for binary alphabets.
        """

        return max(self.environment.options['percept-bits'], self.environment.options['action-bits'])

    # end def

    def model_revert(self, undo_instance):
        revert_size = self.history_size() - undo_instance.history_size

        self.age = undo_instance.age
        self.total_reward = undo_instance.total_reward
        self.last_update = undo_instance.last_update

        self.context_tree.revert(revert_size)

    # end def

    def model_size(self):
        """ Returns the size of the agent's model.
        """
        return self.context_tree.size()

    # end def

    def model_update_action(self, action):
        # The last update must have been a percept, else this action update is invalid.
        assert self.last_update == percept_update, "Can only perform an action update after a percept update."

        # Update the agent's internal model of the world after performing an action.

        # Get the symbols that represent this action.
        action_symbols = self.encode_action(action)

        # Update the context tree.
        self.context_tree.update(action_symbols)

        # Update other properties.
        self.age += 1
        self.last_update = action_update

    # end def

    def model_update_percept(self, observation, reward):
        """ Update the agent's model of the world with a percept from the
            environment.

            - `observation`: the observation that was received.
            - `reward`: the reward that was received.
        """

        # The last update must have been an action, else this percept update is invalid.
        assert self.last_update == action_update, "Can only perform a percept update after an action update."

        # Update the internal model after performing a percept.

        # Get the symbols that represent this percept from the given observation and reward.
        percept_symbols = self.encode_percept(observation, reward)

        # Are we still meant to be learning?
        if (self.learning_period > 0) and (self.age > self.learning_period):
            # No. Update, but don't learn.
            self.context_tree.update_history(percept_symbols)
        else:
            # Yes. Update and learn.
            self.context_tree.update(percept_symbols)
        # end if

        # Update other properties.
        self.total_reward += reward
        self.last_update = percept_update

    # end def

    def playout(self, horizon):
        """ Simulate agent/enviroment interaction for a specified amount of steps
            (the given horizon value) where the agent actions are chosen uniformly
            at random and percepts are generated.

            Returns the total reward from the simulation.

            - `horizon`: the number of complete action/percept steps
                         (the search horizon) to simulate.
        """
        sum__reward = 0.0

        for i in range(horizon):
            action = self.generate_random_action()
            self.model_update_action(action)

            _, reward = self.generate_percept_and_update()
            sum__reward += reward

        return sum__reward

    # end def

    def reset(self):
        """ Resets the agent and clears the context tree.
        """

        # Reset the context tree.
        self.context_tree.clear()

        # Reset the basic agent details.
        agent.Agent.reset(self)

    # end def

    def search(self):
        """ Returns the best action for this agent as determined using the Monte-Carlo Tree Search
            (predictive UCT).
        """

        # Use rhoUCT to search for the next action.
        undo_instance = MC_AIXI_CTW_Undo(self)
        mc_search_tree = monte_carlo_search_tree.MonteCarloSearchNode(decision_node)

        for i in range(self.mc_simulations):
            mc_search_tree.sample(self, self.horizon)
            self.model_revert(undo_instance)

        #Return best action according to their expected reward. Break ties randomly
        return max(mc_search_tree.children.keys(), key=lambda x: mc_search_tree.children[x].mean+random.random()*0.0000001)
    # end def
# end class
