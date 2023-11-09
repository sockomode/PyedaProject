import unittest
from pyeda.inter import *
from functools import reduce
from pyeda.boolalg.bdd import BinaryDecisionDiagram

# Define variables for nodes in the graph
var_x = [bddvar(f"{'x'*2}" + str(i)) for i in range(5)]
var_y = [bddvar(f"{'y'*2}" + str(i)) for i in range(5)]

# Function to initialize a graph using a matrix
def init_graph() -> list[list[bool]]:
    # Initialize a 32x32 graph with default values set to False
    graph_g = [[False]*32 for _ in range(32)]
    for i in range(0, 31):
        for j in range(0, 31):
            # Set edges based on specific conditions
            if(((i+3) % 32 == j % 32) or ((i+8) % 32 == j % 32)):
                graph_g[i][j] = True
    return graph_g

# Create a Boolean expression for a node based on its binary representation
def create_expr(node_val, var):
    node_binary = format(node_val, 'b').rjust(5, '0')
    bdd_string = []
    for i in range(5):
        node_name = f"{var*2}{i}"
        if(int(node_binary[i]) == 1):
            bdd_string.append(node_name)
        else:
            bdd_string.append(f"~{node_name}")
    return expr("&".join(bdd_string))

# Create a BDD expression for a list of nodes
def create_bdd_string(node_list, var):
    bdd_expr_list = [create_expr(i, var) for i in range(len(node_list)) if node_list[i]]
    bdd_string1 = bdd_expr_list[0]
    for i in bdd_expr_list[1:]:
        bdd_string1 |= i
    return expr2bdd(bdd_string1)

# Search for a specific node in the BDD
def find_node(bdd, node_val, var):
    node_binary = format(node_val, 'b').rjust(5, '0')
    var_list = [bddvar(f"{var*2}" + str(i)) for i in range(5)]
    target_node = {var_list[i]: int(node_binary[i]) for i in range(5)}
    res_ans = bdd.restrict(target_node)
    return res_ans.is_one()

# Search for a specific edge in the BDD
def find_edge(bdd, node_x, node_y):
    node_x_binary = format(node_x, 'b').rjust(5, '0')
    node_y_binary = format(node_y, 'b').rjust(5, '0')
    var_x_list = [bddvar(f"{'x'*2}" + str(i)) for i in range(5)]
    var_y_list = [bddvar(f"{'y'*2}" + str(i)) for i in range(5)]
    target_edge = {var_x_list[i]: int(node_x_binary[i]) for i in range(5)}
    target_edge.update({var_y_list[i]: int(node_y_binary[i]) for i in range(5)})
    res_ans = bdd.restrict(target_edge)
    return res_ans.is_one()

# Convert a graph to a BDD
def graph_to_bdd(graph_g):
    R = [create_expr(i, 'x') & create_expr(j, 'y') for i in range(32) for j in range(32) if graph_g[i][j]]
    bdd_string1 = R[0]
    for i in R[1:]:
        bdd_string1 |= i
    return expr2bdd(bdd_string1)

# Perform BDD operations to obtain the result set
def bdd_rr2(original_rr):
    tmp_var_list = [bddvar(f"{'z'*2}" + str(i)) for i in range(5)]
    var_x_list = [bddvar(f"{'x'*2}" + str(i)) for i in range(5)]
    var_y_list = [bddvar(f"{'y'*2}" + str(i)) for i in range(5)]
    composed_set_rr1 = original_rr.compose({var_x_list[i]: tmp_var_list[i] for i in range(5)})
    composed_set_rr2 = original_rr.compose({var_y_list[i]: tmp_var_list[i] for i in range(5)})
    return (composed_set_rr1 & composed_set_rr2).smoothing(tmp_var_list)

# Iteratively perform BDD operations to obtain the fixed-point result
def bdd_rr2star(rr2):
    while True:
        prev_rr2 = rr2
        rr2 = bdd_rr2(rr2)
        if(rr2.equivalent(prev_rr2)):
            break
    return rr2

class TestGraph(unittest.TestCase):
    def test_even(self):
        # These tests are the given test in the assignment page

        # If I don't have this list here gives error
        # even though I declared it already
        self.even_list = [True if i % 2 == 0 else False for i in range(32)]
        even_bdd = create_bdd_string(self.even_list, 'x')

        # EVEN(14) Test
        node_found = find_node(even_bdd, 14, 'x')
        self.assertTrue(node_found)

        # EVEN(13) Test
        node_not_found = find_node(even_bdd, 13, 'x')
        self.assertFalse(node_not_found)

    def test_prime(self):
        prime_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        new_prime_list = [True if i in prime_list else False for i in range(32)]

        prime_bdd = create_bdd_string(new_prime_list, 'y')
        # print(prime_bdd)

        # PRIME(7) Test
        node_found = find_node(prime_bdd, 7, 'y')
        self.assertTrue(node_found)

        # PRIME(2) Test
        node_not_found = find_node(prime_bdd, 2, 'y')
        self.assertFalse(node_not_found)

    def test_rr(self):

        graph_g = init_graph()

        rr_bdd = graph_to_bdd(graph_g)
        # print(rr_bdd)

        # RR(27,3) Test
        edge_found = find_edge(rr_bdd, 27, 3)
        self.assertTrue(edge_found)

        # RR(16,20) Test
        edge_not_found = find_edge(rr_bdd, 16, 20)
        self.assertFalse(edge_not_found)

    def test_rr2(self):
        graph_g = init_graph()

        rr1 = graph_to_bdd(graph_g)
        rr2 = bdd_rr2(rr1)

        # RR2(27,6) Test
        edge_found = find_edge(rr2, 27, 6)
        self.assertTrue(edge_found)

        # RR2(27,9) Test
        edge_not_found = find_edge(rr2, 27, 9)
        self.assertFalse

def test_rr2star(self):
        graph_g = init_graph()
        rr1 = graph_to_bdd(graph_g)
        rr2 = bdd_rr2(rr1)
        rr2star = bdd_rr2star(rr2)
        edge_found = find_edge(rr2star, 27, 6)
        self.assertTrue(edge_found)

    def test_statement(self):
        graph_g = init_graph()
        prime_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        new_prime_list = [True if i in prime_list else False for i in range(32)]
        even_list = [True if i % 2 == 0 else False for i in range(32)]
        var_x = [bddvar(f"{'x'*2}" + str(i)) for i in range(5)]
        var_y = [bddvar(f"{'y'*2}" + str(i)) for i in range(5)]

        rr1 = graph_to_bdd(graph_g)
        rr2 = bdd_rr2(rr1)
        rr2star = bdd_rr2star(rr2)

        prime_bdd = create_bdd_string(new_prime_list, 'x')
        even_bdd = create_bdd_string(even_list, 'y')
        even_nodes_steps = even_bdd & rr2star


if __name__ == "__main__":
    unittest.main()
Let me know if you need anything else!
