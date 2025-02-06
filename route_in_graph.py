# ===============================================
# Route in Graph
# ===============================================

# 1. Add a node that will call our tool.
# 2. Add a conditional edge that will look at the chat model model output, 
#    and route to our tool calling node or simply end if no tool call is performed.

# -----------------------------------------------
# Let's load our environment

from dotenv import load_dotenv
load_dotenv()


# -----------------------------------------------
# Let's define a function to act as our tool
# -----------------------------------------------

def multiply(a: int, b: int) -> int:
    """
    Multiplies a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# -----------------------------------------------
# Let's bind our tool to our chat model
# -----------------------------------------------

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

llm_with_tools = llm.bind_tools([multiply])


# -----------------------------------------------
# Let's build our graph
# -----------------------------------------------

from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

# -----------------------------------------------
# Node function to call our tool

def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# -----------------------------------------------
# Build graph

builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply]))
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", END)

# -----------------------------------------------
# Compile graph

graph = builder.compile()

# -----------------------------------------------
# View

from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Let's invoke the graph with a simple message
# -----------------------------------------------

from langchain_core.messages import HumanMessage

messages = graph.invoke({"messages": HumanMessage(content="Hello! How are you?")})

for msg in messages["messages"]:
    msg.pretty_print()


# -----------------------------------------------
# Let's invoke with a math multiplication message
# -----------------------------------------------

from langchain_core.messages import HumanMessage

messages = graph.invoke({"messages": HumanMessage(content="What is 4 multiplied by 3")})

for msg in messages["messages"]:
    msg.pretty_print()


# -----------------------------------------------