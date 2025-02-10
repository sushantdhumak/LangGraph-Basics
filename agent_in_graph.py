# ===============================================
# Agent in Graph
# ===============================================

# Let's build a ReAct agent, a general agent architecture.

# act     - let the model call specific tools
# observe - pass the tool output back to the model
# reason  - let the model reason about the tool output 
#           to decide what to do next 
#           (e.g., call another tool or just respond directly)

# -----------------------------------------------
# Let's load our environment variables

from dotenv import load_dotenv
load_dotenv()


# -----------------------------------------------
# Let's build few tools
# -----------------------------------------------

from langchain_openai import ChatOpenAI

def multiply(a: int, b: int) -> int:
    """
    Multiplies a and b.

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


def divide(a: int, b: int) -> int:
    """
    Divides a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b


tools = [multiply, add, divide]

llm = ChatOpenAI(model="gpt-4o-mini")

# OpenAI model specifically defaults to parallel tool calling for efficiency
# So we will set parallel_tool_calls to False
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)


# -----------------------------------------------
# Define assistant function 
# -----------------------------------------------

from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage

sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Node function

def assistant(state: MessagesState):
    return {"messages" : [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# -----------------------------------------------
# Let's define a graph
# -----------------------------------------------

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode

# Graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Add edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

# Compile graph
react_graph = builder.compile()


# -----------------------------------------------
# Display the graph
# -----------------------------------------------

from IPython.display import Image, display

display(Image(react_graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Let's send a mathematical question to the agent
# -----------------------------------------------

messages = HumanMessage(content="Add 6 and 4. Multipliy the result by 3. Divide the output by 2")
messages = react_graph.invoke({"messages": [messages]})

for msg in messages["messages"]:
    msg.pretty_print()


# -----------------------------------------------