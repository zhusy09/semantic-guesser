""" Left child, right sibling tree.
Inspired by Cormen's Introduction to Algorithms 3rd edition (p. 247).

@author: Rafa

"""

from learning.tree.abstract import Tree, TreeNode
import json
from math import log
from collections import deque

class DefaultTreeNode (TreeNode):
    """ A base class for tree nodes """

    def __init__(self, key):
        self.leftchild    = None
        self.rightsibling = None
        self.parent       = None
        self.key          = key
        self.value        = 0
        self._entropy     = 0

    def __str__(self):
        return self.key

    def print_nested(self, indent_level=0):
        s = indent_level * '\t' + self.key + ' ' + str(self.value) + '\n'
        for c in self.children():
            s += c.print_nested(indent_level + 1)
        return s

    def increment_value(self, delta, cumulative=True):
        x = self
        while x:
            x.value += delta
            x = x.parent if cumulative else None

    def find(self, key):
        return self.child(key)

    def is_leaf(self):
        return not self.leftchild

    def has_children(self):
        return not self.is_leaf()

    def children(self):
        children = list()
        c = self.leftchild  # c is the current child
        # moving to the right until the last child
        while c is not None:
            children.append(c)
            c = c.rightsibling
        return children

    def remove(self, child):
        children = self.children()
        if child not in children:
            return False

        if child == self.leftchild:
            self.leftchild = child.rightsibling
            return True

        target = children.index(child)

        try:
            children[target-1].rightsibling = children[target+1]
        except:
            children[target-1].rightsibling = None

        return True

    def trim(self, threshold, update_values):
        subtract = 0  # the total value trimmed from the subtree

        for c in self.children():
#             if c.value <= threshold:
#                 subtract += c.value
#                 self.remove(c)
#             else:
            subtract += c.trim(threshold, update_values)
            # re-evaluate c after it has trimmed its subtree
            if c.value <= threshold:
                subtract += c.value
                self.remove(c)
        # updates this value
        self.value -= subtract if update_values else 0
        # propagates the impact of trimming on value
        return subtract

    def create_node(self, key, value=0):
        """ A factory-style method to make things more extensible """
        newnode = DefaultTreeNode(key)
        newnode.value = value
        return newnode

    def insert(self, key=None, node=None, value=0):
        """Inserts a child to this node.
        If it already exists, do nothing...
        In both cases, returns the child.
        """
        newchild = self.create_node(key, value) if key is not None else node
        newchild.parent = self

        if self.leftchild is None:
            self.leftchild = newchild
        else:
            c = self.leftchild  # c is the current child

            while True:
                # if key is already there, do nothing
                if c.key == key:
                    #c.value += 1
                    return c
                if c.rightsibling is None:  # if reached the last child
                    # add the key as right sibling of the last child
                    c.rightsibling = newchild
                    break

                c = c.rightsibling  # moving to the right

        return newchild

    def add_child(self, childnode):
        if self.leftchild is None:
            self.leftchild = childnode
        else:
            c = self.leftchild  # c is the current child

            while True:
                if c.rightsibling is None:  # if reached the last child
                    c.rightsibling = childnode
                    break

                c = c.rightsibling  # moving to the right
        childnode.parent = self

    def child(self, key):
        """Returns the child corresponding to the key
        or None.
        """
        c = self.leftchild  # current child
        while c is not None:
            if c.key == key:
                return c
            else:
                c = c.rightsibling
        return None

    def siblings(self):
        if self.parent is None:
            return []
        else:
            siblings = []
            for child in self.parent.children():
                if child is not self:
                    siblings.append(child)
            return siblings

    def entropy(self):
        self._entropy = 0
        total = self.value

        for c in self.children():
            p = float(c.value)/total
            self._entropy -= p * log(p,2)

        return self._entropy

    def leaves(self):
        """Return array with all leafs within the subtree
        rooted at this node."""
        queue = deque()
        queue.append(self)

        leafs = []

        while len(queue):
            node = queue.pop()
            if node.is_leaf():
                leafs.append(node)
            else:
                queue += reversed(node.children())

        return leafs

    def leafCount(self):
        count = 0
        for c in self.children():
            if c.is_leaf():
                count += 1
            else:
                count += c.leafCount()

        return count


    def wrap(self):
        """ Returns a representation of this node (including all children)
        as a single object, JSON-style.
        """
        children = list()
        for child in self.children():
            children.append(child.wrap())
        if len(children) == 0:
            return {'key': self.key, 'value': self.value}
        else:
            return {'key': self.key, 'value': self.value,
                    'children': children, 'entropy': self._entropy}

    def flat(self):
        """ Non-recursive depth search.
        Adds every visited node to a list and returns it.
        Parents are guaranteed to preceed their children.
        """
        nodes = []

        to_visit = deque([self])

        while to_visit:
            curr = to_visit.popleft()

            # visit
            nodes.append(curr)

            children = curr.children()
            if len(children) > 0:
                to_visit.extendleft(curr.children())

        return nodes

    def __repr__(self):
        return self.__str__()


class DefaultTree (Tree):

    def __init__(self, root=None):
        if root is None:
            self.root = DefaultTreeNode('root')
            self.root.value = 0
        else:
            self.root = root

    def insert(self, path, freq=1, cumulative=True):
        """Insert a subtree.
        Since the tree is cumulative, increments the value of all
        nodes in the path.

        Args:
            path: a list of keys, from root to leaf, e.g.:
                ['connect', 'join', 'copulate', 'sleep_together']
            freq: frequency of the leaf,
            cumulative: if True, increment freq. of all nodes in the path,
                otherwise, assigns freq. to the leaf only
        """

        currNode = self.root

        # insert all keys into the tree, increasing their value
        for key in path:
            if cumulative:
                currNode.value += freq
            currNode = currNode.insert(key=key)

        # increments the count of the leaf
        currNode.value += freq

    def leaves(self):
        return self.root.leaves()

    def hashtable(self):
        """ Returns a hashtable containing all nodes in the tree,
        accessible by key.
        Each  key points to a list  of nodes, since there  can be
        more than one node with the same key in the tree.
        """
        ht = {}

        # Breadth-First Search
        queue = deque()
        queue.append(self.root)

        while len(queue) > 0:
            node = queue.popleft()

            if node.key in ht:
                ht[node.key].append(node)
            else:
                ht[node.key] = [node]

            for child in node.children():
                queue.append(child)

        return ht

    def flat(self):
        return self.root.flat()

    def trim(self, threshold, update_values=True):
        self.root.trim(threshold, update_values)

    def path(self, key, root=None):
        if not root:
            root = self.root

        # trivial case, root has the key
        if root.key == key:
            return [root]

        # if one of the children has the key, insert
        # this node to the front of the path an return it
        # otherwise, search among the children
        child = root.leftchild
        while child:
            path = self.path(key, child)
            if path:
                path.insert(0, root)
                return path
            child = child.rightsibling

        return None

    def updateEntropy(self, node=None):
        """ The __entropy of the nodes is not updated
        every time the structure changes cause it can be
        too expensive. You need to update this attribute
        manually by calling this method.

        """
        if node is None:
            self.updateEntropy(self.root)
        else:
            node.entropy()  # calculates entropy
            for c in node.children():
                self.updateEntropy(c)

    def updateValue(self):
        nodes = self.flat()

        # clear values of internal nodes
        for node in nodes:
            if not node.is_leaf():
                node.value = 0

        # visit nodes in reverse order, so that
        # parents always come after their children
        for node in reversed(nodes):
            if node.parent:
                node.parent.value += node.value


    def toJSON(self):
        return json.dumps(self.root.wrap())


class TreeCut(object):
    def __init__(self, tree, cut):
        self.cut  = cut
        self.tree = tree

        self.leaf2cut = {} # leaf -> [cut members] mapping
        self.cut_ids = set()

        self._build_indexes()

    def _build_indexes(self):
        self.leaf2cut = {}
        # Maintain index where the key is a leaf key and the value
        # is a set of nodes that dominate the key node on the cut.
        # The value array has len > 1 when a node has multiple parents.
        # *Only leaf nodes are mapped*.
        for c in self.cut:
            leaves = c.leaves()
            for leaf in leaves:
                if leaf.key not in self.leaf2cut:
                    self.leaf2cut[leaf.key] = set()
                self.leaf2cut[leaf.key].add(c)

            if len(leaves) == 0:
                if c.key not in self.leaf2cut:
                    self.leaf2cut[c.key] = set()
                self.leaf2cut[c.key].add(c)

        self.cut_ids = set([id(c) for c in self.cut])

    def __iter__(self):
        return iter(self.cut)

    def size(self):
        return len(self.cut)

    def abstract(self, n):
        """Returns the nodes that represent leaf node n in the tree cut"""
        key = ''

        if hasattr(n, 'key'): # if synset or TreeNode
            key = n.key
        else: # assume it's str
            key = n

        if key in self.leaf2cut:
            return self.leaf2cut[key]
        else:
            return None

    def abstract_synset(self, syn):
        try:
            key = 's.' + syn.name()
            return self.leaf2cut[key]
        except:
            return self.leaf2cut[syn.name()]

    def __contains__(self, item):
        return id(item) in self.cut_ids


    def __getstate__(self):
        ids = [node.id for node in self.cut]
        return {
            'cut': ids,
            'tree': self.tree
        }

    def __setstate__(self, d):
        self.tree = d['tree']
        cut_ids = set(d['cut']) # the ids of cut nodes
        self.cut = []
        for depth, node in DepthFirstIterator(self.tree.root):
            if node.id in cut_ids:
                self.cut.append(node)
        self._build_indexes()


class DepthFirstIterator(object):

    def __init__(self, node):
        self.to_visit = deque()
        self.to_visit.append((0, node))

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.to_visit) == 0:
            raise StopIteration
        else:
            depth, node = self.to_visit.popleft()
            children = node.children()
            for child in reversed(children):
                self.to_visit.appendleft((depth+1, child))

            return (depth, node)
