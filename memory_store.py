# ===============================================
# Memory Store in LangGraph
# ===============================================


# -----------------------------------------------
# Load environment variables
# -----------------------------------------------

from dotenv import load_dotenv
load_dotenv()


# -----------------------------------------------
# Memory Store
# -----------------------------------------------

import uuid
from langgraph.store.memory import InMemoryStore

memory_store = InMemoryStore()

# Namespace for the memory to save
user_id = "1"
namespace_for_memory = (user_id, "memories")

# Save a memory to namespace as key and value
key = str(uuid.uuid4())

# Value as a dictionary
value = {"food_choice" : "Veg Sandwitch"}

# Put the memory in the store
memory_store.put(namespace_for_memory, key, value)

# Memory type
memories = memory_store.search(namespace_for_memory)
print(type(memories))

# Get the Memory Metadata from the store
print(memories[0].dict())

# Get the Memory Content from the store
print(memories[0].key, memories[0].value)

# Get the memory by namespace and key
memory = memory_store.get(namespace_for_memory, key)
print(memory.dict())
# print(memory.key, memory.value)


# -----------------------------------------------
# Chatbot with Long-term Memory
# -----------------------------------------------

# Chat Model

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# -----------------------------------------------

from IPython.display import Image, display

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.store.base import BaseStore

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables.config import RunnableConfig

# Chatbot instruction
MODEL_SYSTEM_MESSAGE = """
You are a helpful assistant with memory that provides information about the user. 
If you have memory for this user, use it to personalize your responses.
Here is the memory (it may be empty): {memory}
"""

# Create new memory from the chat history and any existing memory
CREATE_MEMORY_INSTRUCTION = """"
You are collecting information about the user to personalize your responses.

CURRENT USER INFORMATION:
{memory}

INSTRUCTIONS:
1. Review the chat history below carefully
2. Identify new information about the user, such as:
   - Personal details (name, location)
   - Preferences (likes, dislikes)
   - Interests and hobbies
   - Past experiences
   - Goals or future plans
3. Merge any new information with existing memory
4. Format the memory as a clear, bulleted list
5. If new information conflicts with existing memory, keep the most recent version

Remember: Only include factual information directly stated by the user. Do not make assumptions or inferences.

Based on the chat history below, please update the user information:
"""


# -----------------------------------------------

def call_model(state: MessagesState, config: RunnableConfig, store: BaseStore):
    
    """
    Load memory from the store and use it to personalize the chatbot's response.
    """

    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Retrieve memory from the store
    namespace = (user_id, "memory")
    key = "user_memory"
    existing_memory = store.get(namespace, key)

    # Extract the actual memory content if it exist and add a prefix
    if existing_memory:
        existing_memory_content = existing_memory.value.get("memory")
    else:
        existing_memory_content = "No existing memory found"

    # Format the memory in the system prompt
    system_msg = MODEL_SYSTEM_MESSAGE.format(memory=existing_memory_content)

    # Respond using memory as well as the chat history
    response = llm.invoke([SystemMessage(content=system_msg)] + state["messages"])

    return {"messages" : [response]}


# -----------------------------------------------

def write_memory(state: MessagesState, config:RunnableConfig, store: BaseStore):
    """
    Reflect on the chat history and save a memory to the store.
    """

    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Retrieve memory from the store
    namespace = (user_id, "memory")
    key = "user_memory"
    existing_memory = store.get(namespace, key)

    # Extract the actual memory content if it exist and add a prefix
    if existing_memory:
        existing_memory_content = existing_memory.value.get("memory")
    else:
        existing_memory_content = "No existing memory found"

    # Format the memory in the system prompt
    system_msg = MODEL_SYSTEM_MESSAGE.format(memory=existing_memory_content)

    # Respond using memory as well as the chat history
    response = llm.invoke([SystemMessage(content=system_msg)] + state["messages"])

    store.put(namespace, key, {"memory" : response.content})


# -----------------------------------------------
# Define a graph

builder = StateGraph(MessagesState)

# Nodes
builder.add_node("call_model", call_model)
builder.add_node("write_memory", write_memory)

# Edges
builder.add_edge(START, "call_model")
builder.add_edge("call_model", "write_memory")
builder.add_edge("write_memory", END)

# Store for long-term (across-thread) memory
across_thread_memory = InMemoryStore()

# Checkpointer for short-term (within-thread) memory
within_thread_memory = MemorySaver()

# Compile the graph with the checkpointer and store
graph = builder.compile(checkpointer=within_thread_memory, store=across_thread_memory)

# Visualize
display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Run the graph

# We supply a thread ID for short-term (within-thread) memory
# We supply a user ID for long-term (across-thread) memory
 
config = {"configurable": {"thread_id": "1", "user_id": "1"}}

# ----------------------

# User input 
input_messages = [HumanMessage(content="Hi, my name is Sushant")]

# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

# ----------------------

# User input 
input_messages = [HumanMessage(content="I like to drive around Pune")]

# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

# ----------------------

# Chat History
thread = {"configurable": {"thread_id": "1"}}
state = graph.get_state(thread).values

for m in state["messages"]: 
    m.pretty_print()

# ----------------------

# Namespace for the memory to save
user_id = "1"
namespace = (user_id, "memory")
existing_memory = across_thread_memory.get(namespace, "user_memory")
existing_memory.dict()


# -----------------------------------------------
# Run the graph using new thread_id

config = {"configurable": {"thread_id": "2", "user_id": "1"}}

# User input 
input_messages = [HumanMessage(content="Hi! Where would you recommend to drive around Pune?")]

# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

# ----------------------

# User input 
input_messages = [HumanMessage(content="Great, are there any restaurants nearby that I can check out? I like a croissant after driving.")]

# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()


# -----------------------------------------------