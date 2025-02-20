# -----------------------------------------------
# Let's dive into reducers, which specify how state 
# updates are performed on specific keys / channels 
# in the state schema.
# -----------------------------------------------


# -----------------------------------------------
# Overwriting state - 'TypeDict' as state schema
# -----------------------------------------------

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display

class state(TypedDict):
    foo : int

def node1(state):
    print("---Node 1---")
    return {"foo" : state["foo"] + 1}
    
builder = StateGraph(state)

builder.add_node("node1", node1)

builder.add_edge(START, "node1")
builder.add_edge("node1", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

graph.invoke({"foo" : 1})


# -----------------------------------------------
# Branching the nodes - parallel excecution
# -----------------------------------------------

def node1(state):
    print("---Node1---")
    return {"foo" : state["foo"] + 1}

def node2(state):
    print("---Node2---")
    return {"foo" : state["foo"] + 1}

def node3(state):
    print("---Node3---")
    return {"foo" : state["foo"] + 1}

builder = StateGraph(state)

builder.add_node("node1", node1)
builder.add_node("node2", node2)
builder.add_node("node3", node3)

builder.add_edge(START, "node1")
builder.add_edge("node1", "node2")
builder.add_edge("node1", "node3")
builder.add_edge("node2", END)
builder.add_edge("node3", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

# -----------------------------------------------

from langgraph.errors import InvalidUpdateError

try:
    graph.invoke({"foo" : 1})
except InvalidUpdateError as e:
    print(f"Input Valudation Error : {e}")

# Output:

# ---Node1---
# ---Node2---
# ---Node3---
# Input Valudation Error : 
# At key 'foo': Can receive only one value per step. 
# Use an Annotated key to handle multiple values.


# -----------------------------------------------
# Reducers - How to perform update
# -----------------------------------------------

from operator import add
from typing import Annotated

class state(TypedDict):
    foo : Annotated[list[int], add]

def node1(state):
    print("---Node 1----")
    return {"foo" : [state["foo"][-1] + 1]}

def node2(state):
    print("---Node 2----")
    return {"foo" : [state["foo"][-1] + 1]}

def node3(state):
    print("---Node 3----")
    return {"foo" : [state["foo"][-1] + 1]}

builder = StateGraph(state)

builder.add_node("node1", node1)
builder.add_node("node2", node2)
builder.add_node("node3", node3)

builder.add_edge(START, "node1")
builder.add_edge("node1", "node2")
builder.add_edge("node1", "node3")
builder.add_edge("node2", END)
builder.add_edge("node3", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

graph.invoke({"foo" : [1]})

# Output

# ---Node 1----
# ---Node 2----
# ---Node 3----

# {'foo': [1, 2, 3, 3]}

# -----------------------------------------------
# Let's try with None Value

try:
    graph.invoke({"foo" : None})
except TypeError as e:
    print(f"Type Error : {e}")

# Type Error : 
# can only concatenate list (not "NoneType") to list


# -----------------------------------------------
# Custom Reducers

# Let's define custom reducer logic to combine lists 
# and handle cases where either or both of the inputs 
# might be None.
# -----------------------------------------------

def reduce_list(left: list | None, right: list | None):

    """Safely combine two lists, handling cases where either or both inputs might be None.

    Args:
        left (list | None): The first list to combine, or None.
        right (list | None): The second list to combine, or None.

    Returns:
        list: A new list containing all elements from both input lists.
        If an input is None, it's treated as an empty list.
    """

    if left is None:
        left = []

    if right is None:
        right = []

    return left + right

class CustomReducerState(TypedDict):
    foo : Annotated[list[int], reduce_list]

def node1(state):
    print("---Node1---")
    return {"foo": [3]}

builder = StateGraph(CustomReducerState)

builder.add_node("node1", node1)

builder.add_edge(START, "node1")
builder.add_edge("node1", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

try:
    print(graph.invoke({"foo" : None}))
except TypeError as e:
    print(f"Type Error : {e}")


# -----------------------------------------------
# Let's use a built-in reducer - add_messages 
# to handle messages in state
# -----------------------------------------------

from typing import Annotated
from langgraph.graph import MessagesState
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

class CustomMessagesState(TypedDict):
    messages : Annotated[list[AnyMessage], add_messages]
    added_key1 : str
    added_key2 : str

class ExtendedMessagesState(MessagesState):
    added_key1 : str
    added_key2 : str


# -----------------------------------------------
# Let's use add_message reducer

from langchain_core.messages import AIMessage, HumanMessage

# Intial State
initial_messages = [
    AIMessage(content="Hello! How can I assist you?", name="Model"),
    HumanMessage(content="I am looking for information on LLM Agents", name="Sushant")
]

# New message to be added
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")

add_messages(initial_messages, new_message)

# Output
# [AIMessage(content='Hello! How can I assist you?', name='Model', id='75abda06-3358-4246-94a5-3ffa246a9947'),
#  HumanMessage(content='I am looking for information on LLM Agents', name='Sushant', id='0059e5c4-e83a-425a-bf6f-53c40e3bace9'),
#  AIMessage(content='Sure, I can help with that. What specifically are you interested in?', name='Model', id='e19ce5c0-82f1-4670-9a02-dace3701c0a6')]


# -----------------------------------------------
# If we pass a message with the same ID as an existing one 
# in our `messages` list, it will get overwritten!

# Intial State
initial_messages = [
    AIMessage(content="Hello! How can I assist you?", name="Model", id="1"),
    HumanMessage(content="I am looking for information on LLM Agents", name="Sushant", id="2")
]

# New message to be added
new_message = HumanMessage(content="I am looking for information on Python", name="Model", id="2")

add_messages(initial_messages, new_message)


# -----------------------------------------------
# Removal of messages
# -----------------------------------------------

from langchain_core.messages import RemoveMessage

# Message list
messages = [AIMessage("Hi.", name="Bot", id="1")]
messages.append(HumanMessage("Hi.", name="Sushant", id="2"))
messages.append(AIMessage("So you said you were researching LLM Agents?", name="Bot", id="3"))
messages.append(HumanMessage("Yes, I know about LLM Agents. But what others should I learn about?", name="Sushant", id="4"))

# Isolate messaged to delete
delete_message = [RemoveMessage(id=m.id) for m in messages[:-2]]
# print(delete_message)

add_messages(messages, delete_message)

# Output
# [AIMessage(content='So you said you were researching LLM Agents?', name='Bot', id='3'),
#  HumanMessage(content='Yes, I know about LLM Agents. But what others should I learn about?', name='Sushant', id='4')]