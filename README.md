# Maritime_Simulation

This is a 7,5 ECTS research project done at IT Univeristy of Copenhagen. The project is a simple simulation of autonomous ships sailing in formation on a given path. They are trying to sail in either V-formation or tandem on an optimised path.

---

## Overview

The purpose of the project is to contribute to the research in Surface Autonomous Ships by implementing a system to guide the ships. Hopefully it can function as a pilot study for future research.

---

## Installation

### Setup
Clone the repository:
```bash
    git clone https://github.com/marcussimonsen/maritime-simulation
    cd maritime-simulation
```

Create a local virtual environment:
```bash
    python -m venv venv
```

Activate the environment:
```bash
    source venv/bin/activate
```
    
Download requirements:
```bash
    pip install -r requirements.txt
```

Run:
```bash
    python main.py
```


## Controls during runtime

### General

* **P** — Toggle **port placement mode**
* **D** — Toggle map layers (graph / routes / debug state)
* **Y** — Toggle sending ships immediately
* **H** — Start highway optimization
* **Left Click** — Interact with ports (context-dependent)
* **Close Window** — Quit application



### Port Placement Mode (`P`)

* **Left Click** — Place a new port at the closest coastline point
* **↑** — Increase port capacity
* **↓** — Decrease port capacity



### Creating an Order (click a port)

* **Left Click on another port** — Select destination & create order
* **↑** — Increase number of containers
* **↓** — Decrease number of containers
* **C** — Cancel order creation


### Optimization

* **H** — Run highway optimization using current ports



### UI Buttons

* **Toggle Layer Button** — Show / hide routes, graph, and debug state



### Tip

> Controls change depending on whether you are **placing ports** or **creating orders**.