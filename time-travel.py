# ===============================================
# Time Travel in Graph - Human in loop
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
graph = builder.compile(checkpointer=memory)

# Show graph
display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Give input and run the graph
# -----------------------------------------------

input_message = {"messages" : HumanMessage(content="Multiply 4 with 3")}

thread = {"configurable" : {"thread_id" : "1"}}

for event in graph.stream(input_message, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()


# -----------------------------------------------
# Browsing history
# -----------------------------------------------

# Get current state
graph.get_state(thread)

# Get state history for the thread
all_states = [s for s in graph.get_state_history(thread)]

len(all_states)
all_states[-2]


# -----------------------------------------------
# Replaying - re-run from any prior steps
# -----------------------------------------------

to_replay = all_states[-2]

# Look at the state
to_replay.values

# Next node
to_replay.next

# Config
to_replay.config

# Replay from this checkpoint

for event in graph.stream(None, to_replay.config, stream_mode="values"):
    event['messages'][-1].pretty_print()


# -----------------------------------------------
# Forking - Same steps with different output
# -----------------------------------------------

to_fork = all_states[-2]

# Look at the state
to_fork.values["messages"]

# Config
to_fork.config

# Modify the state
fork_config = graph.update_state(
    to_fork.config,
    {
        "messages" : [HumanMessage(content="Multiply 8 with 6",
                                   id = to_fork.values["messages"][0].id)],        
    },
)

# Check config after state modification
to_fork.config

# Get state history
all_states = [state for state in graph.get_state_history(thread) ]
all_states[0].values["messages"]

# Check the current state
graph.get_state({'configurable' : {'thread_id' : '1'}})

# Run the Graph
for event in graph.stream(None, fork_config, stream_mode="values"):
    event['messages'][-1].pretty_print()


# -----------------------------------------------