# ProvMark
Usage: ./fullAutomation \<Tools\> \<Tools Base Directory\> \<Control Directory\> \<Benchmark Directory\> [\<Trial\>, \<Ouput File\>]

Example for generating benchmark for syscall create using SPADE with Graphviz storage:
~~~~
./fullAutomation.py spg /path/to/spade/base/directory ./benchmarkProgram/control ./benchmarkProgram/cmdCreat 2 ./result.clingo
~~~~

#### Tools:
- spg:    SPADE with Graphviz storage
- spn:    SPADE with Neo4j storage
- opu:    OPUS
- cam:    CamFlow

#### Tools Base Directory:
- Base directory of the chosen tool, it is assumed that if you want to execute this benchmarking system on certain provenance collecting tools, you should have installed that tools with all dependencies required by the tools.

#### Control / Benchmark Directory:
- Base directory of the control / benchmark program
- Point the script to the syscall choice and control program choice for the benchmarking process

#### Trial (Default: 2):
- Number of trial executed for each graph for generalization
- More trial will result in longer processing time, but provide a more accurate result as multiple trial can help to filter out uncertainty and unrelated elements and noise

#### Output file (Dafault: ./result.clingo):
- Location of the output file in clingo graph format

# Provenance Collecting Tools supported
We assumed that you have already install the provenance collecting tools and their repsective dependency properly before choosing that tools for the ProvMark system. The installation guide, dependencies and details documentations of the three tools can be found in the follow links.

- SPADE [https://github.com/ashish-gehani/SPADE]
- OPUS [https://www.cl.cam.ac.uk/research/dtg/fresco/opus/]
- CamFlow [http://camflow.org/]

# Use of Clingo
The content inside the directory Clingo is an external work provided by University of Potsdam as part of the Potassco. It is distributed under MIT License and the developer remain their right for the distribution of the binary and code. We provide a local copy of the compiled version 5.2.1 for convenience only. You should always search for the original code and binary of Clingo from the original developer. Here is a link to the original developer [http://potassco.sourceforge.net/]

# System Description

## Stage 1 Execute provenance collecting tools of choice on chosen syscall benchmark program (and control program)
In this step, the chosen syscall and control program will be prepared in a clean stage. Then the chosen provenance collecting tools will be started and record provenance of the execution of those program with multiple trial. The provenance collecting tools will create one set of provenance result per trial per program. These result is the raw data from the provenance collecting tools and are further processed and analysis in our system to generate benchmark. Currently, there are three type of output format supported. Graphviz dot format, neo4j format (in full db or cypher dump of the db) and the prov-json format.

## Stage 2 Transform raw result to Clingo graph format
Clingo is a Answer Set Programming language that provides powerful modelling ability to solve combinatorial problems. We make use of it to solve the complicated graph compaison problems for matching vertics and edges in multiple trial of benchmark program execution for generalization of graph and identification of additional elements (benchmark of a syscall for certain provenance collecting tools). In this steps, the system will run a different script to transform the raw result generated by the provenance collecting tools to clingo graph formatfor further processing. As those provenance information is supposed to describing the execution trace of the chosen syscall program, it is always possible to transform into directed graph. Each trial result will be transformed into one clingo graph for the next stage.

## Stage 3 Generalize resulting graph for multiple trial
In this stage, multiple clingo graph descirbing the multiple trial of the same program execution will be put together to compare. The clingo graph will match the elements in the graph two by two and provide a matching list of nodes and edges with least edit distance. Then the properties in the graph will be compared one by one, noises will be identified and removed. The result of this stage should be a generalized graph for the control program and another generalized graph for the chosen syscall program. The should contains the information which is truely related to the program execution with minimum noise.

## Stage 4 Generating benchmark of chosen syscall for chosen provenance collecting tool
This is the last stage of the benchmarking system execution. In this stage, the two generalized graph will be compared to each other. As we assume that the chosen syscall is always a few steps or command more than the control program execution and they are both executed based on a same stage environment with the same language. So the additional elements in the generalized syscall graph shows the patterns that can be used as a benchmark to identify this syscall when we are using the chosen provenance collecting tools. All those addtional branchesand properties will be identified and summarized in the result file in clingo format. Currently, this is the end of the full system. The clingo format graph can be transformed into other directed graph format if needed in the future.

# Result File Format

- Node

~~~~
n<graph identifier>(<node identifier>,<type>)
~~~~

- Edge (Directed edge)

~~~~
e<graph identifier>(<edge identifier>, <start node identifier>, <end node identifier>, <type>)
~~~~

- Properties

~~~~
l<graph identifier>(<node / edge identifier>, <key>, <value>)
~~~~
