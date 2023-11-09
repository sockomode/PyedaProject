import unittest
from pyeda.inter import *
from functools import reduce
from pyeda.boolalg.bdd import BinaryDecisionDiagram

# Define variables for nodes in the graph
varX = [bddvar(f"{'x'*2}" + str(i)) for i in range(5)]
varY = [bddvar(f"{'y'*2}" + str(i)) for i in range(5)]

# Function to initialize a graph using a matrix
def initGraph() -> list[list[bool]]:
    # Initialize a 32x32 graph with default values set to False
    graphG = [[False]*32 for _ in range(32)]
    for i in range(0, 31):
        for j in range(0, 31):
            # Set edges based on specific conditions
            if(((i+3) % 32 == j % 32) or ((i+8) % 32 == j % 32)):
                graphG[i][j] = True
    return graphG

# Create a Boolean expression for a node based on its binary representation
def createExpr(nodeVal, var):
    nodeBinary = format(nodeVal, 'b').rjust(5, '0')
    BDDString = []
    for i in range(5):
        nodeName = f"{var*2}{i}"
        if(int(nodeBinary[i]) == 1):
            BDDString.append(nodeName)
        else:
            BDDString.append(f"~{nodeName}")
    return expr("&".join(BDDString))

# Create a BDD expression for a list of nodes
def createBDDString(nodeList, var):
    bddExprList = [createExpr(i, var) for i in range(len(nodeList)) if nodeList[i]]
    bddString1 = bddExprList[0]
    for i in bddExprList[1:]:
        bddString1 |= i
    return expr2bdd(bddString1)

# Search for a specific node in the BDD
def findNode(bdd, nodeVal, var):
    nodeBinary = format(nodeVal, 'b').rjust(5, '0')
    varList = [bddvar(f"{var*2}" + str(i)) for i in range(5)]
    targetNode = {varList[i]: int(nodeBinary[i]) for i in range(5)}
    resAns = bdd.restrict(targetNode)
    return resAns.is_one()

# Search for a specific edge in the BDD
def findEdge(bdd, nodeX, nodeY):
    nodeXBinary = format(nodeX, 'b').rjust(5, '0')
    nodeYBinary = format(nodeY, 'b').rjust(5, '0')
    varXList = [bddvar(f"{'x'*2}" + str(i)) for i in range(5)]
    varYList = [bddvar(f"{'y'*2}" + str(i)) for i in range(5)]
    targetEdge = {varXList[i]: int(nodeXBinary[i]) for i in range(5)}
    targetEdge.update({varYList[i]: int(nodeYBinary[i]) for i in range(5)})
    resAns = bdd.restrict(targetEdge)
    return resAns.is_one()

# Convert a graph to a BDD
def graphToBDD(graphG):
    R = [createExpr(i, 'x') & createExpr(j, 'y') for i in range(32) for j in range(32) if graphG[i][j]]
    bddString1 = R[0]
    for i in R[1:]:
        bddString1 |= i
    return expr2bdd(bddString1)

# Perform BDD operations to obtain the result set
def bddRR2(originalRR):
    tmpVarList = [bddvar(f"{'z'*2}" + str(i)) for i in range(5)]
    varXList = [bddvar(f"{'x'*2}" + str(i)) for i in range(5)]
    varYList = [bddvar(f"{'y'*2}" + str(i)) for i in range(5)]
    composedSetRR1 = originalRR.compose({varXList[i]: tmpVarList[i] for i in range(5)})
    composedSetRR2 = originalRR.compose({varYList[i]: tmpVarList[i] for i in range(5)})
    return (composedSetRR1 & composedSetRR2).smoothing(tmpVarList)

# Iteratively perform BDD operations to obtain the fixed-point result
def bddRR2star(rr2):
    while True:
        prevRR2 = rr2
        rr2 = bddRR2(rr2)
        if(rr2.equivalent(prevRR2)):
            break
    return rr2

class TestGraph(unittest.TestCase):
    def testEVEN(self):
        #These tests are the given test in the assignment page

        # If I don't have this list here gives error
        # even though I declared it already
        self.evenList = [True if i % 2 == 0 else False for i in range(32)]
        evenBDD = createBDDString(self.evenList, 'x')

        #EVEN(14) Test
        nodeFound = findNode(evenBDD,14,'x')
        self.assertTrue(nodeFound)

        #EVEN(13) Test
        nodeNotFound = findNode(evenBDD,13,'x')
        self.assertFalse(nodeNotFound)

    def testPRIME(self):
        primeList = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        newPrimeList = [True if i in primeList else False for i in range(32)]

        primeBDD = createBDDString(newPrimeList, 'y')
        #print(primeBDD)

        #PRIME(7) Test
        nodeFound = findNode(primeBDD,7,'y')
        self.assertTrue(nodeFound)

        #PRIME(2) Test
        nodeNotFound = findNode(primeBDD,2,'y')
        self.assertFalse(nodeNotFound)

    def testRR(self):

        graphG = initGraph()

        rrBDD = graphToBDD(graphG)
        #print(rrBDD)

        #RR(27,3) Test
        edgeFound = findEdge(rrBDD,27,3)
        self.assertTrue(edgeFound)

        #RR(16,20) Test
        edgeNotFound = findEdge(rrBDD,16,20)
        self.assertFalse(edgeNotFound)

    def testRR2(self):
        graphG = initGraph()

        rr1 = graphToBDD(graphG)
        rr2 = bddRR2(rr1)

        #RR2(27,6) Test
        edgeFound = findEdge(rr2,27,6)
        self.assertTrue(edgeFound)

        #RR2(27,9) Test
        edgeNotFound = findEdge(rr2,27,9)
        self.assertFalse(edgeNotFound)

    def testRR2star(self):
        graphG = initGraph()
        rr1 = graphToBDD(graphG)
        rr2 = bddRR2(rr1)
        rr2star = bddRR2star(rr2)
        edgeFound = findEdge(rr2star, 27,6)
        self.assertTrue(edgeFound)

    def testStatemnt(self):
        graphG = initGraph()
        primeList = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        newPrimeList = [True if i in primeList else False for i in range(32)]
        evenList = [True if i % 2 == 0 else False for i in range(32)]
        varX = [bddvar(f"{'x'*2}" + str(i)) for i in range(5)]
        varY = [bddvar(f"{'y'*2}" + str(i)) for i in range(5)]

        rr1 = graphToBDD(graphG)
        rr2 = bddRR2(rr1)
        rr2star = bddRR2star(rr2)

        primeBDD = createBDDString(newPrimeList, 'x')
        evenBDD = createBDDString(evenList, 'y')
        evenNodesSteps = evenBDD & rr2star

        #Could not figure out how to procede from here got stuck on 
        #How I can further figure out if there are an even number of
        #Steps !!!!!!

if __name__ == "__main__":
    
    unittest.main()
