# encoding: latin2
""" AZP-R-Tabu
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from past.utils import old_div
__author__ = "Juan C. Duque"
__credits__= "Copyright (c) 2009-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

import numpy
import time as tm
from .componentsAlg import AreaManager
from .componentsAlg import BasicMemory
from .componentsAlg import RegionMaker

__all__ = ['execAZPRTabu']
        
def execAZPRTabu(y, w, pRegions, initialSolution=[], convTabu=0):
    """Reactive tabu variant of Automatic Zoning Procedure (AZP-R-Tabu) 

    AZP-R-Tabu aggregates N zones (areas) into M regions. "The M output
    regions should be formed of internally connected, contiguous, zones."
    ([Openshaw_Rao1995]_ pp 428).

    AZP-R-Tabu is a variant of the AZP algorithm that incorporates a seach
    process, called Reactive Tabu Search algorithm [Battiti_Tecchiolli1994]_.
    The main difference between the reactive tabu and the tabu search, devised
    by [Glover1977]_ , is that the former does not require to define
    the number of times a reverse move is prohibited (tabuLength). This
    parameter is dynamically adjusted by the algorithm.
    
    In [Openshaw_Rao1995]_ the objective function is not defined because
    AZP-Tabu can be applied to any function, F(Z). "F(Z) can be any function
    defined on data for the M regions in Z, and Z is the allocation of each of
    N zones to one of M regions such that each zone is assigned to only one
    region" ([Openshaw_Rao1995]_ pp 428)." In clusterPy we Minimize F(Z),
    where Z is the within-cluster sum of squares from each area to the
    attribute centroid of its cluster.

    NOTE: The original algorithm proposes to start from a random initial
    feasible solution. Previous computational experience showed us that this
    approach leads to poor quality solutions. In clusterPy we started from an
    initial solution that starts with a initial set of seeds (as many seed as
    regions) selected using the K-means++ algorithm. From those seeds, other
    neighbouring areas are assigned to its closest (in attribute space)
    growing region. This strategy has proven better results. ::

        layer.cluster('azpRTabu',vars,regions,<wType>,<std>,<initialSolution>,<convTabu>,<dissolve>,<dataOperations>)

    :keyword vars: Area attribute(s) (e.g. ['SAR1','SAR2']) 
    :type vars: list
    :keyword regions: Number of regions 
    :type regions: integer
    :keyword wType: Type of first-order contiguity-based spatial matrix: 'rook' or 'queen'. Default value wType = 'rook'. 
    :type wType: string
    :keyword std: If = 1, then the variables will be standardized.
    :type std: binary
    :keyword initialSolution: List with a initial solution vector. It is useful when the user wants a solution that is not very different from a preexisting solution (e.g. municipalities,districts, etc.). Note that the number of regions will be the same as the number of regions in the initial feasible solution (regardless the value you assign to parameter "regions"). IMPORTANT: make sure you are entering a feasible solution and according to the W matrix you selected, otherwise the algorithm will not converge.
    :type initialSolution: list
    :keyword convTabu: Stop the search after convTabu nonimproving moves (nonimproving moves are those moves that do not improve the current solution. Note that "improving moves" are different to "aspirational moves"). If convTabu=0 the algorithm will stop after Int(M/N) nonimproving moves. Default value convTabu = 0.
    :type convTabu: integer
    :keyword dissolve: If = 1, then you will get a "child" instance of the layer that contains the new regions. Default value = 0. Note:. Each child layer is saved in the attribute ayer.results. The first algorithm that you run with dissolve=1 will have a child layer in layer.results[0]; the second algorithm that you run with dissolve=1 will be in layer.results[1], and so on. You can export a child as a shapefile with layer.result[<1,2,3..>].exportArcData('filename')
    :type dissolve: binary
    :keyword dataOperations: Dictionary which maps a variable to a list of operations to run on it. The dissolved layer will contains in it's data all the variables specified in this dictionary. Be sure to check the input layer's fieldNames before use this utility.
    :type dataOperations: dictionary

    The dictionary structure must be as showed bellow.

    >>> X = {}
    >>> X[variableName1] = [function1, function2,....]
    >>> X[variableName2] = [function1, function2,....]

    Where functions are strings wich represents the name of the 
    functions to be used on the given variableName. Functions 
    could be,'sum','mean','min','max','meanDesv','stdDesv','med',
    'mode','range','first','last','numberOfAreas. By deffault just
    ID variable is added to the dissolved map.
    
    """
    print("Running original AZP-R-Tabu algorithm (Openshaw and Rao, 1995)")
    print("Number of areas: ", len(y))
    if initialSolution != []:
        print("Number of regions: ", len(numpy.unique(initialSolution)))
        pRegions = len(numpy.unique(initialSolution))
    else:
        print("Number of regions: ", pRegions)
    if pRegions >= len(y):
        message = "\n WARNING: You are aggregating "+str(len(y))+" into"+\
        str(pRegions)+" regions!!. The number of regions must be an integer"+\
        " number lower than the number of areas being aggregated"
        raise Exception(message) 

    if convTabu <= 0:
        convTabu = old_div(len(y),pRegions)  #  convTabu = 230*numpy.sqrt(pRegions)
    distanceType = "EuclideanSquared" 
    distanceStat = "Centroid"
    objectiveFunctionType = "SS"
    selectionType = "Minimum"
    am = AreaManager(w, y, distanceType)
    start = tm.time()
    print("Constructing regions")
    rm = RegionMaker(am, pRegions,
                    initialSolution=initialSolution,
                    distanceType=distanceType,
                    distanceStat=distanceStat,
                    selectionType=selectionType,
                    objectiveFunctionType=objectiveFunctionType)
    Sol = rm.returnRegions()
    print("initial Solution: ", Sol)
    print("initial O.F: ", rm.objInfo)

    # LOCAL SEARCH

    print("Performing local search")
    rm.reactiveTabuMove(convTabu)
    time = tm.time() - start
    Sol = rm.returnRegions()
    Of = rm.objInfo
    print("FINAL SOLUTION: ", Sol)
    print("FINAL OF: ", Of)
    output = { "objectiveFunction": Of,
    "runningTime": time,
    "algorithm": "azpRtabu",
    "regions": len(Sol),
    "r2a": Sol,
    "distanceType": distanceType,
    "distanceStat": distanceStat,
    "selectionType": selectionType,
    "ObjectiveFuncionType": objectiveFunctionType} 
    print("Done")
    return output
