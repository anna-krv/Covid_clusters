# -*- coding: utf-8 -*-
"""
Class that implements disjoint sets data structure (integers are stored in).

Created on Wed Aug    5 11:54:09 2020

@author: Anna Kravets
"""


class DisjointSets:
    """Mimics division of integers 0..n-1 into sets that do not intersect.

    Implements FIND SET operation on an integer and UNION operation on sets.
    Uses virtual trees with path compression and union-by-rank for more
    efficient operations.

    Attributes
    ----------
    parents: list
        stores index of parent for each element
    ranks: list
        stores ranks of elements - upper bound on number of children of the
        element.
    tree_size: list
        is true and sensible only for roots of trees

    """

    def __init__(self, n):
        """
        Create n sets, each set containing one integer i where i in [0..n-1].

        Args:
            n (int): number of elements.

        Returns
        -------
            None.

        """
        self.parents = [i for i in range(n)]
        self.ranks = [0]*n
        self.tree_size = [1]*n

    def union(self, id1, id2):
        """
        Merge sets containing id1 and id2, if they are distinct. Update ranks.

        Args:
            id1 (int): one of ints.
            id2 (int): one of ints.

        Returns
        -------
            None.

        """
        parent1 = self.find_set(id1)
        parent2 = self.find_set(id2)
        if parent1 == parent2:
            return

        new_parent = parent2 if self.ranks[parent2] >= self.ranks[parent1] \
            else parent1
        old_parent = parent1 if self.ranks[parent2] >= self.ranks[parent1] \
            else parent2

        self.parents[old_parent] = new_parent

        if self.ranks[new_parent] == self.ranks[old_parent]:
            self.ranks[new_parent] += 1

        self.tree_size[new_parent] += self.tree_size[old_parent]

    def find_set(self, i):
        """
        Find representative id of the set to which the element i belongs.

        Implement path compression.

        Args:
            i (int): element for which the set is being looked up.

        Returns
        -------
            int: representative id of the set containing ith element.

        """
        parent = self.parents[i]
        if self.parents[parent] != parent:
            self.parents[i] = self.find_set(parent)
        return self.parents[i]

    def get_all_sets(self):
        """
        Generate list of sets of elements.

        Returns
        -------
            all_sets (list): contains sets that have been formed.

        """
        all_sets = dict()
        for i in range(len(self.parents)):
            parent = self.find_set(i)
            if parent in all_sets:
                all_sets[parent].add(i)
            else:
                all_sets[parent] = {i}
        return list(all_sets.values())
