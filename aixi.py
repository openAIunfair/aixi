#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime
import random

from mc_aixi_ctw import MC_AIXI_CTW_Agent
from environments.coin_flip import CoinFlip
from environments.extended_tiger import  ExtendedTiger


def interaction_loop(agent=None, environment=None, options={}):
    # Determine exploration options. (Default: don't explore, don't decay.)
    explore_rate = float(options.get("exploration", 0.0))
    explore = (explore_rate > 0)
    explore_decay = float(options.get("explore-decay", 1.0))
    assert 0.0 <= explore_rate
    assert 0.0 <= explore_decay and explore_decay <= 1.0

    # Determine termination age. (Default: don't terminate)
    terminate_age = int(options.get("terminate-age", 0))
    terminate_check = (terminate_age > 0)
    assert 0 <= terminate_age

    # Determine the cycle after which the agent stops learning (if ever.)
    learning_period = int(options.get("learning-period", 0))
    assert 0 <= learning_period

    # Agent/environment interaction loop.
    cycle = 1
    while not environment.is_finished:
        # Check for agent termination.
        if terminate_check and agent.age > terminate_age:
            break
        # end if

        # Save the current time to compute how long this cycle took.
        cycle_start = datetime.datetime.now()

        # Get a percept from the environment.
        observation = environment.observation
        reward = environment.reward

        # If we're outside the learning period, stop exploring.
        if learning_period > 0 and cycle > learning_period:
            explore = False
        # end if

        # Update the agent's environment model with the new percept.
        agent.model_update_percept(observation, reward)  # TODO: implement

        # Determine best exploitive action, or explore.
        explored = False
        if explore and (random.random() < explore_rate):
            # Yes, we're still exploring.
            # Generate a random action to explore.
            explored = True
            # end if
            action = agent.generate_random_action()
        # end if
        else:
            action = agent.search()  # TODO: implement
        # end else

        # Send the action to the environment.
        environment.perform_action(action)

        # Update the agent's environment model with the chosen action.
        agent.model_update_action(action)  # TODO: implement

        # Calculate how long this cycle took.
        time_taken = datetime.datetime.now() - cycle_start

        # Log this cycle.
        message = "%d, %s, %s, %s, %s, %f, %d, %f, %s, %d" % \
                  (cycle, str(observation), str(reward),
                   str(action), str(explored), explore_rate,
                   agent.total_reward, agent.average_reward(),
                   str(time_taken), agent.model_size())
        print(message)

        # Update exploration rate.
        if explore:
            explore_rate *= explore_decay
        # end def

        # Update the cycle count.
        cycle += 1
    # end while

    # Print summary to standard output.
    message = "SUMMARY:" + os.linesep + \
              "agent age: %d" % agent.age + os.linesep + \
              "average reward: %f" % agent.average_reward()

    print(message)
# end def


def main():
    # Define some default configuration values.

    default_options = {"agent": "mc_aixi_ctw", "agent-horizon": 5, "ct-depth": 50, "environment": "extended_tiger",
                       "exploration": 0.99, "explore-decay": 0.99, "learning-period": 0, "mc-simulations": 200,
                       "profile": False, "terminate-age": 0, "verbose": False}

    # Print an initial message header.
    message = "cycle, observation, reward, action, explored, " + \
              "explore_rate, total reward, average reward, time, model size"
    print(message)

    options = {}
    environment = ExtendedTiger()
    # Copy environment-dependent configuration options to the options.
    options["action-bits"] = environment.action_bits()
    options["observation-bits"] = environment.observation_bits()
    options["percept-bits"] = environment.percept_bits()
    options["reward-bits"] = environment.reward_bits()
    options["max-action"] = environment.maximum_action()
    options["max-observation"] = environment.maximum_observation()
    options["max-reward"] = environment.maximum_reward()

    environment.set_options(options)
    agent = MC_AIXI_CTW_Agent(environment, default_options)

    if not bool(options.get("profile", False)):
        interaction_loop(agent=agent, environment=environment, options=default_options)
    # end def
# end def

# Start the main function if this file has been executed, and not just imported.
if __name__ == "__main__":
    main()
# end def
