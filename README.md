# Python to FlexSim connection
Demo script for connecting Python with FlexSim.

The script:
* creates a socket connection between Python and FlexSim
* opens an instance of FlexSim
* sends information through the socket to classify products in different racks (toy example)
* closes the connection and the FlexSim instance

### Instructions:
1. Modify the FlexSimConnection class instantiation to point to your local instalation of FlexSim and the path to the "connection_demo.fsm" file.
Line 99 of the "connection_demo.py" file:
```
    FS = FlexSimConnection(
        flexsimPath = "C:/Program Files/FlexSim 2022/program/flexsim.exe",
        modelPath = "C:/Users/.../socket_test_13.fsm",
        verbose = True,
        visible = True
        )
```
2. Run "connection_demo.py".

### Versions:
Python: v3.8.10
FlexSim: 2022.0.0