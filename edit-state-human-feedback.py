# ===============================================
# Editing a state in Graph - Human in loop
# ===============================================


# -----------------------------------------------
# Load environment variables
# -----------------------------------------------

from dotenv import load_dotenv

load_dotenv()


# -----------------------------------------------
# Tools - functions
# -----------------------------------------------

from langchain_openai import ChatOpenAI

def multiply(a: int, b: int) -> int:
    """
    Multiply a and b.

    Args:
        a: first int
        b: second int
    """

    return a * b


def add(a: int, b: int) -> int:
    """
    Adds a and b.

    Args:
        a: first int
        b: second int
    """

    return a + b


def divide(a: int, b: int) -> float:
    """
    Divides a and b.

    Args:
        a: first int
        b: second int
    """

    return a / b


tools = [add, multiply, divide]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)


# -----------------------------------------------
# Define a Graph
# -----------------------------------------------

from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from IPython.display import Image, display

# System Message
sys_message = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Mode
def assistant(state:MessagesState):
    return {"messages" : [llm_with_tools.invoke([sys_message] + state["messages"])]}

builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["assistant"])

# Show graph
display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Give input and run the graph
# -----------------------------------------------

input_message = {"messages" : HumanMessage(content="Multiply 4 with 3")}

thread = {"configurable" : {"thread_id" : "1"}}

for event in graph.stream(input_message, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Get the state and next node

state = graph.get_state(thread)
# state.next
state

# Update the state

graph.update_state(
    thread,
    {"messages" : [HumanMessage(content="No, multiply 6 with 5")]}
)

# Let's check new state

new_state = graph.get_state(thread).values

for msg in new_state["messages"]:
    msg.pretty_print()

# Let's proceed ahead from current new state

for event in graph.stream(None, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

for event in graph.stream(None, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()


# -----------------------------------------------
# Awaiting user Input
# -----------------------------------------------

sys_message = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Human feedback node with no input

def human_feedback(state:MessagesState):
    pass

# Assistant node

def assistant(state:MessagesState):
    return {"messages" : [llm_with_tools.invoke([sys_message] + state["messages"])]}

# Graph

builder = StateGraph(MessagesState)

# Nodes

builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_node("human_feedback", human_feedback)

# Edges

builder.add_edge(START, "human_feedback")
builder.add_edge("human_feedback", "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "human_feedback")

memory = MemorySaver()

graph = builder.compile(checkpointer=memory, interrupt_before=["human_feedback"])

# Show graph
display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Give input and run the graph
# -----------------------------------------------

input_message = {"messages" : HumanMessage(content="Multiply 5 with 6")}

thread = {"configurable" : {"thread_id" : "2"}}

# Run the graph until the human feedback
for event in graph.stream(input_message, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Get user input
user_input = input("Tell me how you want to update the state: ")

# Update the state

graph.update_state(
    thread,
    {"messages" : [HumanMessage(content=user_input)]},
    as_node="human_feedback"
)

# Continue the graph

for event in graph.stream(None, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Final graph execution

for event in graph.stream(None, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()


# -----------------------------------------------