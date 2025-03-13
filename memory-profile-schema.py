# ===============================================
# Memory Profile Schema in LangGraph
# ===============================================


# -----------------------------------------------
# Load environment variables
# -----------------------------------------------

from dotenv import load_dotenv
load_dotenv()


# -----------------------------------------------
# Defining a User Profile Schema
# -----------------------------------------------

# Using TypedDict

from typing import TypedDict, List

class UserProfile(TypedDict):
    """
    User profile schema with typed fields
    """
    user_name: str  # The user's preferred name
    interests: List[str]  # A list of the user's interests


# -----------------------------------------------
# Saving schema to the store
# -----------------------------------------------

user_profile: UserProfile = {
    "user_name": "Sushant",
    "interests": ["AI", "Machine Learning", "Deep Learning"],
}

# Save it to the store

from langgraph.store.memory import InMemoryStore
memory_store = InMemoryStore()

# Namespace for the memory to save
user_id = "1"
namespace_for_memory = (user_id, "memory")

# Save a memory to namespace as key and value
key = "user_profile"
value = user_profile
memory_store.put(namespace_for_memory, key, value)

# # Search
# for m in memory_store.search(namespace_for_memory):
#     print(m.dict())

# # Search by namespace and key
# profile = memory_store.get(namespace_for_memory, "user_profile")
# profile.value


# -----------------------------------------------
# Chatbot with Profile Schema
# -----------------------------------------------

from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Bind schema to model
model_with_structure = llm.with_structured_output(UserProfile)

# Invoke the model to produce structured output that matches the schema
structured_output = model_with_structure.invoke([HumanMessage("My name is Sushant. I like to learn AI Agents.")])
structured_output


# -----------------------------------------------

from IPython.display import Image, display

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.store.base import BaseStore

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables.config import RunnableConfig

# Chatbot instruction
MODEL_SYSTEM_MESSAGE = """
You are a helpful assistant with memory that provides information about the user. 
If you have memory for this user, use it to personalize your responses.
Here is the memory (it may be empty): {memory}
"""

# Create new memory from the chat history and any existing memory
CREATE_MEMORY_INSTRUCTION = """
Create or update a user profile memory based on the user's chat history. 
This will be saved for long-term memory. If there is an existing memory, simply update it. 
Here is the existing memory (it may be empty): {memory}
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
    if existing_memory and existing_memory.value:
        memory_dict = existing_memory.value
        formatted_memory = (
            f"Name: {memory_dict.get('user_name', 'Unknown')}\n"
            f"Interests: {', '.join(memory_dict.get('interests', []))}"
        )
    else:
        formatted_memory = None

    # Format the memory in the system prompt
    system_msg = MODEL_SYSTEM_MESSAGE.format(memory=formatted_memory)

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
    if existing_memory and existing_memory.value:
        memory_dict = existing_memory.value
        formatted_memory = (
            f"Name: {memory_dict.get('user_name', 'Unknown')}\n"
            f"Interests: {', '.join(memory_dict.get('interests', []))}"
        )
    else:
        formatted_memory = None

    # Format the memory in the system prompt
    system_msg = MODEL_SYSTEM_MESSAGE.format(memory=formatted_memory)

    # Respond using memory as well as the chat history
    response = model_with_structure.invoke([SystemMessage(content=system_msg)] + state["messages"])

    store.put(namespace, key, response) # {"memory" : response.content}


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
input_messages = [HumanMessage(content="Hi, my name is Sushant and I like to drive around Pune.")]

# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

# ----------------------

# Namespace for the memory to save
user_id = "1"
namespace = (user_id, "memory")
existing_memory = across_thread_memory.get(namespace, "user_memory")
# existing_memory.value


# -----------------------------------------------
# When can it fail?

from typing import List, Optional

class OutputFormat(BaseModel):
    preference: str
    sentence_preference_revealed: str

class TelegramPreferences(BaseModel):
    preferred_encoding: Optional[List[OutputFormat]] = None
    favorite_telegram_operators: Optional[List[OutputFormat]] = None
    preferred_telegram_paper: Optional[List[OutputFormat]] = None

class MorseCode(BaseModel):
    preferred_key_type: Optional[List[OutputFormat]] = None
    favorite_morse_abbreviations: Optional[List[OutputFormat]] = None

class Semaphore(BaseModel):
    preferred_flag_color: Optional[List[OutputFormat]] = None
    semaphore_skill_level: Optional[List[OutputFormat]] = None

class TrustFallPreferences(BaseModel):
    preferred_fall_height: Optional[List[OutputFormat]] = None
    trust_level: Optional[List[OutputFormat]] = None
    preferred_catching_technique: Optional[List[OutputFormat]] = None

class CommunicationPreferences(BaseModel):
    telegram: TelegramPreferences
    morse_code: MorseCode
    semaphore: Semaphore

class UserPreferences(BaseModel):
    communication_preferences: CommunicationPreferences
    trust_fall_preferences: TrustFallPreferences

class TelegramAndTrustFallPreferences(BaseModel):
    pertinent_user_preferences: UserPreferences

# -------------------------------------

from pydantic import ValidationError

# Bind schema to model
model_with_structure = llm.with_structured_output(TelegramAndTrustFallPreferences)

# Conversation
conversation = """
Operator: How may I assist with your telegram, sir?
Customer: I need to send a message about our trust fall exercise.
Operator: Certainly. Morse code or standard encoding?
Customer: Morse, please. I love using a straight key.
Operator: Excellent. What's your message?
Customer: Tell him I'm ready for a higher fall, and I prefer the diamond formation for catching.
Operator: Done. Shall I use our "Daredevil" paper for this daring message?
Customer: Perfect! Send it by your fastest carrier pigeon.
Operator: It'll be there within the hour, sir.
"""

# Invoke the model
try:
    model_with_structure.invoke(f"""Extract the preferences from the following conversation:
    <convo>
    {conversation}
    </convo>
    """)
except ValidationError as e:
    print(e)


# -----------------------------------------------
# Trustcall for creating and updating profile schemas
# -----------------------------------------------

# Conversation
conversation = [HumanMessage(content="Hi, I'm Sushant."), 
                AIMessage(content="Nice to meet you, Sushant."), 
                HumanMessage(content="I really like to drive around Pune and Mumbai.")]


from trustcall import create_extractor

# Schema 
class UserProfile(BaseModel):
    """
    User profile schema with typed fields
    """
    user_name: str = Field(description="The user's preferred name")
    interests: List[str] = Field(description="A list of the user's interests")

# Initialize the model
model = ChatOpenAI(model="gpt-4o", temperature=0)

# Create the extractor
trustcall_extractor = create_extractor(
    model,
    tools=[UserProfile],
    tool_choice="UserProfile"
)

# Instruction
system_msg = "Extract the user profile from the following conversation"

# Invoke the extractor
result = trustcall_extractor.invoke({"messages": [SystemMessage(content=system_msg)] + conversation})

for m in result["messages"]: 
    m.pretty_print()


# -----------------------------------------------
# Trustcall on challenging schemas
# -----------------------------------------------

bound = create_extractor(
    model,
    tools=[TelegramAndTrustFallPreferences],
    tool_choice="TelegramAndTrustFallPreferences",
)

# Conversation
conversation = """
Operator: How may I assist with your telegram, sir?
Customer: I need to send a message about our trust fall exercise.
Operator: Certainly. Morse code or standard encoding?
Customer: Morse, please. I love using a straight key.
Operator: Excellent. What's your message?
Customer: Tell him I'm ready for a higher fall, and I prefer the diamond formation for catching.
Operator: Done. Shall I use our "Daredevil" paper for this daring message?
Customer: Perfect! Send it by your fastest carrier pigeon.
Operator: It'll be there within the hour, sir.
"""

result = bound.invoke(
    f"""Extract the preferences from the following conversation:
<convo>
{conversation}
</convo>"""
)

# Extract the preferences
result["responses"][0]


# -----------------------------------------------
# Chatbot with profile schema updating using Trustcall
# -----------------------------------------------

# Schema 
class UserProfile(BaseModel):
    """ Profile of a user """
    user_name: str = Field(description="The user's preferred name")
    user_location: str = Field(description="The user's location")
    interests: list = Field(description="A list of the user's interests")

# Create the extractor
trustcall_extractor = create_extractor(
    model,
    tools=[UserProfile],
    tool_choice="UserProfile", # Enforces use of the UserProfile tool
)

# Chatbot instruction
MODEL_SYSTEM_MESSAGE = """
You are a helpful assistant with memory that provides information about the user. 
If you have memory for this user, use it to personalize your responses.
Here is the memory (it may be empty): {memory}
"""

# Extraction instruction
TRUSTCALL_INSTRUCTION = """
Create or update the memory (JSON doc) to incorporate information from the following conversation:
"""

# -------------------------------------

def call_model(state: MessagesState, config: RunnableConfig, store: BaseStore):

    """Load memory from the store and use it to personalize the chatbot's response."""
    
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Retrieve memory from the store
    namespace = ("memory", user_id)
    existing_memory = store.get(namespace, "user_memory")

    # Format the memories for the system prompt
    if existing_memory and existing_memory.value:
        memory_dict = existing_memory.value
        formatted_memory = (
            f"Name: {memory_dict.get('user_name', 'Unknown')}\n"
            f"Location: {memory_dict.get('user_location', 'Unknown')}\n"
            f"Interests: {', '.join(memory_dict.get('interests', []))}"      
        )
    else:
        formatted_memory = None

    # Format the memory in the system prompt
    system_msg = MODEL_SYSTEM_MESSAGE.format(memory=formatted_memory)

    # Respond using memory as well as the chat history
    response = model.invoke([SystemMessage(content=system_msg)]+state["messages"])

    return {"messages": response}

# -------------------------------------

def write_memory(state: MessagesState, config: RunnableConfig, store: BaseStore):

    """Reflect on the chat history and save a memory to the store."""
    
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Retrieve existing memory from the store
    namespace = ("memory", user_id)
    existing_memory = store.get(namespace, "user_memory")
        
    # Get the profile as the value from the list, and convert it to a JSON doc
    existing_profile = {"UserProfile": existing_memory.value} if existing_memory else None
    
    # Invoke the extractor
    result = trustcall_extractor.invoke({"messages": [SystemMessage(content=TRUSTCALL_INSTRUCTION)]+state["messages"], "existing": existing_profile})
    
    # Get the updated profile as a JSON object
    updated_profile = result["responses"][0].model_dump()

    # Save the updated profile
    key = "user_memory"
    store.put(namespace, key, updated_profile)

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

# -------------------------------------

# User input 
input_messages = [HumanMessage(content="Hi, my name is Sushant and I like to drive around Pune.")]

# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

# -------------------------------------

# Namespace for the memory to save
user_id = "1"
namespace = (user_id, "memory")
existing_memory = across_thread_memory.get(namespace, "user_memory")
# existing_memory.value

# -------------------------------------

# User input 
input_messages = [HumanMessage(content="I also enjoy going to bakeries")]

# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

# -------------------------------------

# We supply a thread ID for short-term (within-thread) memory
# We supply a user ID for long-term (across-thread) memory 
config = {"configurable": {"thread_id": "2", "user_id": "1"}}

# User input 
input_messages = [HumanMessage(content="What bakeries do you recommend for me?")]

# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()


# -----------------------------------------------