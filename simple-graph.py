# ===============================================
# The Simplest Graph
# ===============================================

# -----------------------------------------------
# Let's define the State of the graph
# -----------------------------------------------

from typing_extensions import TypedDict

class State(TypedDict):
    graph_state: str


# -----------------------------------------------
# Let's define Nodes for the graph
# -----------------------------------------------

def node_1(state):
    print("---Node 1---")
    return {"graph_state": state['graph_state'] + " I am"}

def node_2(state):
    print("---Node 2---")
    return {"graph_state": state['graph_state'] + " Happy!"}

def node_3(state):
    print("---Node 3---")
    return {"graph_state" : state['graph_state'] + " Sad!"}


# -----------------------------------------------
# Let's define Edges for the graph
# Condtional Edge
# -----------------------------------------------

import random
from typing import Literal

def decide_mood(state) -> Literal["node_2", "node_3"]:
    
    user_input = state['graph_state']

    if random.random() < 0.5:

        # 50% of the time, we return Node 2
        return "node_2"
    
    # 50% of the time, we return Node 3
    return "node_3"


# -----------------------------------------------
# Let's construct the Graph
# -----------------------------------------------

from langgraph.graph import StateGraph, START, END

# Build graph
builder = StateGraph(State)

builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Compile graph
graph = builder.compile()


# -----------------------------------------------
# Let's view the Graph
# -----------------------------------------------

from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Let's Invoke the Graph
# -----------------------------------------------

print(graph.invoke({"graph_state" : "Hi, This is Sushant."}))