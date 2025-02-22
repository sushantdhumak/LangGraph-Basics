# -----------------------------------------------
# Let's use multiple state schemas in a single graph
# to solve below problems
# Internal nodes may pass information that is *not required* 
# in the graph's input / output.
# We may also want to use different input / output 
# schemas for the graph.
# -----------------------------------------------

# -----------------------------------------------
# Private State
# For anything needed as part of the intermediate working 
# logic of the graph, but not relevant for the overall 
# graph input or output.
# -----------------------------------------------

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display

# Create States

class PrivateState(TypedDict):
    baz : int

class OverallState(TypedDict):
    foo : int

# Define nodes using states

def node1(state: OverallState) -> PrivateState:
    print("--- Node 1 ---")
    return {"baz" : state["foo"] + 1}

def node2(state: PrivateState) -> OverallState:
    print("--- Node 2 ----")
    return {"foo" : state["baz"] + 1}

# Build a graph

builder = StateGraph(OverallState)

# Adding Nodes

builder.add_node("node1", node1)
builder.add_node("node2", node2)

# Adding Edges

builder.add_edge(START, "node1")
builder.add_edge("node1", "node2")
builder.add_edge("node2", END)

graph = builder.compile()

# Display the graph

display(Image(graph.get_graph().draw_mermaid_png()))

# Run the graph

graph.invoke({"foo" : 1})


# -----------------------------------------------
# Input/Output Schema - using single schema
# -----------------------------------------------

class OverallState(TypedDict):
    question : str    
    answer : str
    notes : str

def thinking_node(state: OverallState):
    return {"answer" : "bye", "notes" : "... his name is Sushant."}

def answer_node(state: OverallState):
    return {"answer" : "bye Sushant!"}

builder = StateGraph(OverallState)

builder.add_node("thinking_node", thinking_node)
builder.add_node("answer_node", answer_node)

builder.add_edge(START, "thinking_node")
builder.add_edge("thinking_node", "answer_node")
builder.add_edge("answer_node", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

graph.invoke({"question":"hi"})


# -----------------------------------------------
# Input/Output Schema - using multiple schema
# -----------------------------------------------

class InputState(TypedDict):
    question : str

class OutputState(TypedDict):
    answer : str

class OverallState(TypedDict):
    question : str
    answer : str
    notes : str


def thinking_node(state:InputState):
    return {"answer" : "bye", "notes" : "... his name is Sushant."}

def answer_node(state:OverallState) -> OutputState:
    return {"answer" : "Bye Sushant."}


builder = StateGraph(OverallState, input=InputState, output=OutputState)

builder.add_node("thinking_node", thinking_node)
builder.add_node("answer_node", answer_node)

builder.add_edge(START, "thinking_node")
builder.add_edge("thinking_node", "answer_node")
builder.add_edge("answer_node", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

graph.invoke({"question" : "hi"})


# -----------------------------------------------