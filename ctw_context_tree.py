#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Define classes to implement context trees according to the Context Tree Weighting algorithm.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import random

# Ensure xrange is defined on Python 3.
from six.moves import xrange

# The value ln(0.5).
# This value is used often in computations and so is made a constant for efficiency reasons.
log_half = math.log(0.5)


class CTWContextTreeNode:

    def __init__(self, tree=None):
        """ Construct a node of the context tree.
        """

        # The children of this node.
        self.children = {}

        # The tree object associated with this node.
        self.tree = tree

        # The cached KT estimate of the block log probability for this node.
        # This value is computed only when the node is changed by the update or revert methods.
        self.log_kt = 0

        # The cached weighted log probability for this node.
        # This value is computed only when the node is changed by the update or revert methods.
        self.log_probability = 0.0

        # The count of the symbols in the history subsequence relevant to this node.
        self.symbol_count = {0: 0, 1: 0}


    # end def

    def is_leaf_node(self):
        """ Return True if the node is a leaf node, False otherwise.
        """

        # If this node has no children, it's a leaf node.
        return self.children == {}

    # end def

    def log_kt_multiplier(self, symbol):
        """ Returns the logarithm of the KT-estimator update multiplier.
           The log KT estimate of the conditional probability of observing a zero given
           we have observed `a` zeros and `b` ones at the current node is
             log(Pr_kt(0 | 0^a 1^b)) = log((a + 1/2)/(a + b + 1))
           Similarly, the estimate of the conditional probability of observing a one is
             log(Pr_kt(1 |0^a 1^b)) = log((b + 1/2)/(a + b + 1))
           - `symbol`: the symbol for which to calculate the log KT estimate of
             conditional probability.
             0 corresponds to calculating `log(Pr_kt(0 | 0^a 1^b)` and
             1 corresponds to calculating `log(Pr_kt(1 | 0^a 1^b)`.
        """

        return math.log((self.symbol_count[symbol] + 0.5) / (self.visits() + 1))

    # end def

    def revert(self, symbol):
        """ Reverts the node to its state immediately prior to the last update.
            This involves updating the symbol counts, recalculating the cached
            probabilities, and deleting unnecessary child nodes.
            - `symbol`: the symbol used in the previous update.
        """
        self.symbol_count[symbol] -= 1

        assert self.symbol_count[symbol] >= 0, "Symbol count should be non-negative"

        self.log_kt -= self.log_kt_multiplier(symbol)
        
        del_list = []

        #Update ctw tree size if new node is added
        for child in self.children.keys():
            if self.children[child].visits() == 0:
                self.tree.tree_size -= self.children[child].size()
                del_list.append(child)

        #Delete empty child
        for child in del_list:
            del self.children[child]

        self.update_log_probability()
    # end def

    def size(self):
        """ The number of descendants of this node.
        """

        # Iterate over the direct children of this node, collecting the size of each sub-tree.
        return 1 + sum([child.size() for child in self.children.values()])

    # end def

    def update(self, symbol):
        """ Updates the node after having observed a new symbol.
            This involves updating the symbol counts and recalculating the cached probabilities.
            - `symbol`: the symbol that was observed.
        """
        self.log_kt += self.log_kt_multiplier(symbol)
        self.update_log_probability()
        self.symbol_count[symbol] += 1
    # end def

    def update_log_probability(self):

        if not self.children:
            self.log_probability = self.log_kt
        else:
            child_sum = sum([child.log_probability for child in self.children.values()])
            
            if child_sum <= self.log_kt:
                self.log_probability = log_half + self.log_kt + math.log(1 + math.exp(child_sum - self.log_kt))
            else:
                self.log_probability = log_half + child_sum + math.log(1 + math.exp(self.log_kt - child_sum))

    # end def

    def visits(self):
        """ Returns the number of times this context has been visited.
            This is the sum of the visits of the (immediate) child nodes.
        """

        return self.symbol_count[0] + self.symbol_count[1]

    # end def

    def show(self):
        symbols = '0:' + str(self.symbol_count[0]) + '  1:' + str(self.symbol_count[1])
        children = ""

        for symbol, child in self.children.items():
            children += str(symbol) + child.show() + ','

        return '{' + symbols + '||' + children + '}'


# end class


class CTWContextTree:

    def __init__(self, depth):
        """ Create a context tree of specified maximum depth.
            Nodes are created as needed.
            - `depth`: the maximum depth of the context tree.
        """

        # An list used to hold the nodes in the context tree that correspond to the current context.
        # It is important to ensure that `update_context()` is called before accessing the contents
        # of this list as they may otherwise be inaccurate.
        self.context = []

        # The maximum depth of the context tree.
        assert depth >= 0, "The given tree depth must be greater than zero."
        self.depth = depth

        # The history (a list) of symbols seen by the tree.
        self.history = []

        # The root node of the context tree.
        self.root = CTWContextTreeNode(tree=self)

        # The size of this tree.
        self.tree_size = 1

        self.history_size = 0

    # end def

    def clear(self):
        """ Clears the entire context tree including all nodes and history.
        """

        # Reset the history.
        self.history = []

        # Set a new root object, and reset the tree size.
        self.root.tree = None
        del self.root
        self.root = CTWContextTreeNode(tree=self)
        self.tree_size = 1

        # Reset the context.
        self.context = []

    # end def

    def generate_random_symbols(self, symbol_count):
        """ Returns a symbol string of a specified length by sampling from the context tree.
            - `symbol_count`: the number of symbols to generate.
        """
        symbol_list = self.generate_random_symbols_and_update(symbol_count)

        self.revert(symbol_count)

        return symbol_list

    # end def

    def generate_random_symbols_and_update(self, symbol_count):
        """ Returns a specified number of random symbols distributed according to
            the context tree statistics and update the context tree with the newly
            generated symbols.
            - `symbol_count`: the number of symbols to generate.
        """

        symbol_list = []

        for i in range(symbol_count):
            # assert 0.99 <= self.predict([0])+self.predict([1]) <= 1.01, "Pro sum should be equal to 1"

            threshold = self.predict([0])

            symbol = 0 if random.random() < threshold else 1

            symbol_list.append(symbol)
            self.update([symbol])

        return symbol_list

    # end def

    def predict(self, symbol_list):
        """ Returns the conditional probability of a symbol (or a list of symbols), considering the history.
            Given a history sequence `h` and a symbol `y`, the estimated probability is given by
              rho(y | h) = rho(hy)/rho(h)
            where `rho(h) = P_w^epsilon(h)` is the weighted probability estimate of observing `h`
            evaluated at the root node `epsilon` of the context tree.
            - `symbol_list` The symbol (or list of symbols) to estimate the conditional probability of.
                            0 corresponds to `rho(0 | h)` and 1 to `rho(1 | h)`.
        """

        if len(self.history) + len(symbol_list) <= self.depth:
            return 0.5 ** len(symbol_list)

        rho_h = self.root.log_probability
        self.update(symbol_list)
        rho_hy = self.root.log_probability

        probability = rho_hy - rho_h

        self.revert(len(symbol_list))

        return math.exp(probability)
    # end def

    def revert(self, symbol_count=1):
        """ Restores the context tree to its state prior to a specified number of updates.

            - `num_symbols`: the number of updates (symbols) to revert. (Default of 1.)
        """

        assert symbol_count >= 0, "The given symbol count should be greater than 0"

        for i in range(symbol_count):
            symbol = self.history.pop(0)
            self.history_size -= 1

            self.update_context()

            for node in reversed(self.context):
                node.revert(symbol)

    def size(self):
        """ Returns the number of nodes in the context tree.
        """

        # Return the value stored and updated by the children nodes.
        return self.tree_size

    # end def

    def update(self, symbol_list):
        """ Updates the context tree with a new (binary) symbol, or a list of symbols.
            Recalculates the log weighted probabilities and log KT estimates for each affected node.
            - `symbol_list`: the symbol (or list of symbols) with which to update the tree.
                              (The context tree is updated with symbols in the order they appear in the list.)
        """
        for symbol in symbol_list:
            self.update_context()

            for node in reversed(self.context):
                node.update(symbol)

            self.update_history([symbol])
            
    # end def

    def update_context(self):
        """ Calculates which nodes in the context tree correspond to the current
            context, and adds them to `context` in order from root to leaf.
            In particular, `context[0]` will always correspond to the root node
            and `context[self.depth]` corresponds to the relevant leaf node.
            Creates the nodes if they do not exist.
        """
        self.context = [self.root]
        parent = self.root

        for i in range(len(self.history)):

            symbol = self.history[i]

            if symbol not in parent.children:
                child = CTWContextTreeNode(tree=self)
                parent.children[symbol] = child

                self.tree_size += 1

            parent = parent.children[symbol]
            self.context.append(parent)
            
            if i == self.depth-1:
                break
            # end def

    def update_history(self, symbol_list):
        """ Appends a symbol (or a list of symbols) to the tree's history without updating the tree.
            - `symbol_list`: the symbol (or list of symbols) to add to the history.
        """

        # Ensure that we have a list, by making this a list if it's a single symbol.

        for symbol in symbol_list:
            self.history = [symbol] + self.history
            self.history_size += 1

    # end def

    def show(self):
        return self.root.show()
# end class
