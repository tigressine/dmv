# Dependency Metric Visualizer
Analyze the I/A scatter plot of your software architecture with this easy visualizer! This tool is inspired by Robert Martin's textbook on software design: *Clean Architecture* (chapter 14).

# Usage
To use this script, execute `dmv.py` with 1 argument: a `JSON` file detailing your software's architecture. Here's an exmple with an architecture file named `my_architecture.json`:
```
  $ python3 dmv.py my_architecture.json
```

# Sample
A sample architecture named `data_viewer.json` is located in [samples](../samples/data_viewer.json). When analyzed, this architecture produces [these metrics](../samples/data_viewer.data) and this graph:   
![GRAPH NOT AVAILABLE](../samples/data_viewer.png)
