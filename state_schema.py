# ===============================================
# State Schema in Graph
# ===============================================


# -----------------------------------------------
# Let's define a state schema using a TypedDict
# -----------------------------------------------

from typing_extensions import TypedDict
from typing import Literal

class TypeDictState(TypedDict):
    name : str
    mood : Literal["Happy", "Sad"]


# -----------------------------------------------
# Let's define the Graph
# -----------------------------------------------

import random
from langgraph.graph import StateGraph, START, END

# Adding Nodes

def node_1(state):
    print("--- Node_1 ---")
    return {"name" : state["name"] + " is ...."}

def node_2(state):
    print("--- Node_2 ---")
    return {"mood" : "Happy"}

def node_3(state):
    print("--- Node_3 ---")
    return {"mood" : "Sad"}

def decide_mood(state) -> Literal["node_2", "node_3"]:
    if random.random() < 0.5:
        return "node_2"    
    else:
        return "node_3"

# Defining Graph

builder = StateGraph(TypeDictState)

builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

graph = builder.compile()

# Visualzing Graph

from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))

# Rin the Graph

graph.invoke({"name" : "Sushant"})


# -----------------------------------------------
# Let's define a state schema using DataClass
# -----------------------------------------------

from dataclasses import dataclass

@dataclass
class DataClassState:
    name : str
    mood : Literal["Happy", "Sad"]

# Changing previous nodes

def node_dc(state):
    print("---Node_dc----")
    return {"name" : state.name + " is ...." }

# Define Graph

builder_dataclass = StateGraph(DataClassState)

builder_dataclass.add_node("node_dc", node_dc)
builder_dataclass.add_node("node_2", node_2)
builder_dataclass.add_node("node_3", node_3)

builder_dataclass.add_edge(START, "node_dc")
builder_dataclass.add_conditional_edges("node_dc", decide_mood)
builder_dataclass.add_edge("node_2", END)
builder_dataclass.add_edge("node_3", END)

graph_dc = builder_dataclass.compile()

# Visualizing Graph

from IPython.display import Image, display
display(Image(graph_dc.get_graph().draw_mermaid_png()))

# Let's run the graph

graph_dc.invoke(DataClassState(name="Sushant", mood="Happy"))


# -----------------------------------------------
# Let's define a state schema using Pydantic
# -----------------------------------------------

from pydantic import BaseModel, field_validator, ValidationError

class PydanticState(BaseModel):
    name : str
    mood : str

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, value):
        if value not in ["Happy", "Sad"]:
            raise ValueError("Value must be either Happy or Sad")
        return value

try:
    state = PydanticState(name="Sushant", mood="Mad")
except ValidationError as e:
    print("Validation error :", e)

# Changing previous nodes

def node_pd(state):
    print("---Node_pd----")
    return {"name" : state.name + " is ...." }

# Define a Graph

builder_pydantic = StateGraph(PydanticState)

builder_pydantic.add_node("node_pd", node_pd)
builder_pydantic.add_node("node_2", node_2)
builder_pydantic.add_node("node_3", node_3)

builder_pydantic.add_edge(START, "node_pd")
builder_pydantic.add_conditional_edges("node_pd", decide_mood)
builder_pydantic.add_edge("node_2", END)
builder_pydantic.add_edge("node_3", END)

graph_pd = builder_pydantic.compile()

# Visualizing Graph

from IPython.display import Image, display
display(Image(graph_pd.get_graph().draw_mermaid_png()))

# Running the graph

graph_pd.invoke(PydanticState(name="Sushant", mood="Happy"))


# -----------------------------------------------