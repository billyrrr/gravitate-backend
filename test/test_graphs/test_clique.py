"""
This is for experimenting with networkx library for matching functionality
"""
from itertools import combinations

import networkx as nx
from unittest import TestCase


class GraphCliqueTest(TestCase):

    def test_enumerate_all_cliques(self):
        # G = nx.Graph()
        # elist = [(1, 2), (2, 3), (1, 4), (4, 2)]
        # G.add_edges_from(elist)

        G = nx.Graph()
        G.add_edges_from(combinations(range(0, 5), 2))  # Add a five clique
        G.add_edges_from(combinations(range(5, 10), 2))  # Add another five clique

        res = nx.enumerate_all_cliques(G)
        # res = nx.find_cliques(G)
        #
        # for c in res:
        #     print(c)

    def test_find_k_cliques(self):
        # G = nx.Graph()
        # elist = [(1, 2), (2, 3), (1, 4), (4, 2)]
        # G.add_edges_from(elist)

        G = nx.Graph()
        G.add_edges_from(combinations(range(0, 5), 2))  # Add a five clique
        G.add_edges_from(combinations(range(5, 10), 2))  # Add another five clique

        res = list(nx.enumerate_all_cliques(G))
        # res = nx.find_cliques(G)

        traversed = set()

        def kth_iteration(k, groups):

            k_cliques = list()

            for c in res:
                if len(c) < k or len(c) == 1:
                    continue
                elif len(c) > k:
                    break
                set_c = set(c)
                print(set_c)
                # Only append clique to set_c if every one has not been grouped
                if not traversed.intersection(set_c):
                    k_cliques.append(set_c)

            while len(k_cliques) != 0:
                # print(l)
                g = k_cliques.pop()
                groups.append(g)
                for m in g:
                    traversed.add(m)
                    k_cliques = [ gr for gr in k_cliques if m not in gr ]

            print(groups)

        k = 3
        groups = list()
        while k != 0:
            kth_iteration(k, groups)
            k -= 1

