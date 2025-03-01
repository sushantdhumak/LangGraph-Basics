# ===============================================
# Dynamic Breakpoints in Graph - Human in loop
# ===============================================


# -----------------------------------------------
# Load environment variables
# -----------------------------------------------

from dotenv import load_dotenv

load_dotenv()


# -----------------------------------------------
# Graph with NodeInterrupt
# -----------------------------------------------

from langgraph.graph import StateGraph, START, END
from langgraph.errors import NodeInterrupt
from langgraph.checkpoint.memory import MemorySaver

from typing_extensions import TypedDict
from IPython.display import display, Image

class State(TypedDict):
    input: str

# Define Node functions
def step_1(state:State) -> State:
    print("---Step 1---")
    return state

def step_2(state:State) -> State:
    # Conditional NodeInterrupt
    if len(state['input']) > 5:
        raise NodeInterrupt(f"Received input that is longer than 5 characters: {state['input']}")
    
    print("---Step 2---")
    return state

def step_3(state:State) -> State:
    print("---Step 3---")
    return state

# Create Graph
builder = StateGraph(state_schema=State)

# Add nodes
builder.add_node("step_1", step_1)
builder.add_node("step_2", step_2)
builder.add_node("step_3", step_3)

# Add edges
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
builder.add_edge("step_3", END)

memory = MemorySaver()

graph = builder.compile(checkpointer=memory)

# Show Graph
display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Give input and run the graph
# -----------------------------------------------

input_message = {"input" : "Hello World!"}

thread = {"configurable" : {"thread_id" : "2"}}

for event in graph.stream(input_message, thread, stream_mode="values"):
    print(event)

# Get the state and next node

state = graph.get_state(thread)
print(state.next)

# State log

print(state.tasks)


# -----------------------------------------------
# To resume the graph let's update the state
# -----------------------------------------------

graph.update_state(thread, {"input" : "Hello"},)

for event in graph.stream(None, thread, stream_mode="values"):
    print(event)


# -----------------------------------------------