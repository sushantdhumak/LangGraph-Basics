# ===============================================
# Breakpoints in Graph - Human in loop
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
graph = builder.compile(checkpointer=memory, interrupt_before=["tools"])

# Show graph
display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Give input and run the graph
# -----------------------------------------------

input_message = {"messages" : HumanMessage(content="Multiply 4 with 3")}

thread = {"configurable" : {"thread_id" : "2"}}

for event in graph.stream(input_message, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Get the state and next node

state = graph.get_state(thread)
state.next

# User feedback

user_approval = input("Do you want to call a tool? (Yes/No)")

# Continue from current state

if user_approval == "Yes" :

    for event in graph.stream(None, thread, stream_mode="values"):
        event['messages'][-1].pretty_print()

else:
    print("Operation Cancelled by the User")


# -----------------------------------------------