# Network-database
A network database using replica method
networked database server composed of multiple nodes operating together.

Data model: key/value store

Implementation language: Python

run a 3 node cluster that would execute code similar to the one below, settings and getting data from the cluster.

dbClient = initClient([
    "127.0.0.1:8888", "127.0.0.2:8888", "127.0.0.3:8888"
])
dbClient.set("student-1", "Israeli, Israel")
print(dbClient.get("student-1"))

The nodes can keep the data in memory (no persistence needed).
●	Replicated - all the data is replicated among the nodes

●	Code for the database node.
●	Scripts that would run the database nodes (three separate processes, simulating three different machines, communicating over the network).

The code handle the scenario of a single machine (out of 3) going down gracefully.
Pay close attention to error handling, the location of the data and how you are handling failure modes.

