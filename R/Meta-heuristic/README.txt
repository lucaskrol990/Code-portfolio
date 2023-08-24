This folder contains a meta-heuristic which can be used to solve the LRPCC problem. 

The LRPCC problem considers the minimization of transportation related costs. There is one depot and n customers which have to be supplied with goods by electrical vehicles (with infinite size). The customers have a timeframe in which they can be supplied and chargers can be placed at the customers, at a certain cost, where the electrical vehicles can be charged. The objective is to find the optimal number of vehciles, the route they drive and their charging schemes, as well as the optimal placement of the chargers, to minimize the resulting costs.

This problem is NP-hard and therefore has to be solved by heuristics. The proposed meta-heuristics is unique not only in its operators, but also because it contains Tabu list, which disallows certain charger locations and yielded considerable improvements upon the standard meta-heuristic. 

The meta-heuristic has been benchmarked on 300 different instances, provided by the teacher, which had different focusses (some focusses on finding the optimal placement of chargers, others on finding the optimal routes etc.). Our meta-heuristic outperformed all other heuristics proposed in class, including the teacher's, finding the optimal solution for 231 out of the 300 instances. On the other instances, the meta-heuristic was off by at most 1% from the optimal solution. 

A detailed description of the problem and the meta-heuristic can be found in Description_problem_and_heuristic.pdf

The main code file is Algorithm.R
