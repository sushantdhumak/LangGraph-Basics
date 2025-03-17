# ===============================================
# Connecting to a LangGraph Platform Deployment
# ===============================================

# -----------------------------------------------
# Deployment Creation
# -----------------------------------------------

# $ docker compose up

# Once running, we can access the deployment through:
      
# API: http://localhost:8123
# Docs: http://localhost:8123/docs
# LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123

# Using the API  

# LangGraph Server exposes many API endpoints for interacting with the deployed agent.

# We can group these endpoints into a few common agent needs:

# **Runs**: Atomic agent executions
# **Threads**: Multi-turn interactions or human in the loop
# **Store**: Long-term memory


# -----------------------------------------------
# The LangGraph SDKs (Python and JS) provide a 
# developer-friendly interface to interact with 
# the LangGraph Server API presented above.
# -----------------------------------------------

from langgraph_sdk import get_client

# Connect via SDK
url_for_cli_deployment = "http://localhost:8123"
client = get_client(url=url_for_cli_deployment)


# -----------------------------------------------
# Remote Graph
# -----------------------------------------------

from langgraph.pregel.remote import RemoteGraph
from langchain_core.messages import convert_to_messages
from langchain_core.messages import HumanMessage, SystemMessage

# Connect via remote graph
url = "http://localhost:8123"
graph_name = "task_maistro" 
remote_graph = RemoteGraph(graph_name, url=url)


# -----------------------------------------------
# Create a thread

thread = await client.threads.create()
thread

# -----------------------------------------------
# Check any existing runs on a thread

runs = await client.runs.list(thread["thread_id"])
print(runs)

# -----------------------------------------------
# Ensure we've created some ToDos and saved them to my user_id

user_input = "Add a ToDo to finish booking travel to Hong Kong by end of next week. Also, add a ToDo to call parents back about Thanksgiving plans."
config = {"configurable": {"user_id": "Test"}}
graph_name = "task_maistro" 

run = await client.runs.create(thread["thread_id"], graph_name, input={"messages": [HumanMessage(content=user_input)]}, config=config)

# -----------------------------------------------
# Kick off a new thread and a new run

thread = await client.threads.create()

user_input = "Give me a summary of all ToDos."
config = {"configurable": {"user_id": "Test"}}
graph_name = "task_maistro" 

run = await client.runs.create(thread["thread_id"], graph_name, input={"messages": [HumanMessage(content=user_input)]}, config=config)

# -----------------------------------------------
# Check the run status

print(await client.runs.get(thread["thread_id"], run["run_id"]))

# -----------------------------------------------
# Wait until the run completes

await client.runs.join(thread["thread_id"], run["run_id"])
print(await client.runs.get(thread["thread_id"], run["run_id"]))


# -----------------------------------------------
# Streaming Runs
# -----------------------------------------------

user_input = "What ToDo should I focus on first."

async for chunk in client.runs.stream(thread["thread_id"], 
                                      graph_name, 
                                      input={"messages": [HumanMessage(content=user_input)]},
                                      config=config,
                                      stream_mode="messages-tuple"):

    if chunk.event == "messages":
        print("".join(data_item['content'] for data_item in chunk.data if 'content' in data_item), end="", flush=True)


# -----------------------------------------------
# Threads
# -----------------------------------------------

# -----------------------------------------------
# Check thread State

thread_state = await client.threads.get_state(thread['thread_id'])

for m in convert_to_messages(thread_state['values']['messages']):
    m.pretty_print()

# -----------------------------------------------
# Copy threads

copied_thread = await client.threads.copy(thread['thread_id'])

# -----------------------------------------------
# Check the state of the copied thread

copied_thread_state = await client.threads.get_state(copied_thread['thread_id'])

for m in convert_to_messages(copied_thread_state['values']['messages']):
    m.pretty_print()


# -----------------------------------------------
# Human in the loop
# -----------------------------------------------

# -----------------------------------------------
# Get the history of the thread

states = await client.threads.get_history(thread['thread_id'])

# -----------------------------------------------
# Pick a state update to fork

to_fork = states[-2]

to_fork['values'] # This is the state

to_fork['values']['messages'][0]['id'] # This is the message id

to_fork['next'] # This is the next node

to_fork['checkpoint_id'] # This is the checkpoint id

# -----------------------------------------------
# Edit the state with ID

forked_input = {"messages": HumanMessage(content="Give me a summary of all ToDos that need to be done in the next week.",
                                         id=to_fork['values']['messages'][0]['id'])}

# Update the state, creating a new checkpoint in the thread

forked_config = await client.threads.update_state(
    thread["thread_id"],
    forked_input,
    checkpoint_id=to_fork['checkpoint_id']
)

# Run the graph from the new checkpoint in the thread

async for chunk in client.runs.stream(thread["thread_id"], 
                                      graph_name, 
                                      input=None,
                                      config=config,
                                      checkpoint_id=forked_config['checkpoint_id'],
                                      stream_mode="messages-tuple"):

    if chunk.event == "messages":
        print("".join(data_item['content'] for data_item in chunk.data if 'content' in data_item), end="", flush=True)


# -----------------------------------------------
# Across thread memory
# -----------------------------------------------

# -----------------------------------------------
# Search items

items = await client.store.search_items(
    ("todo", "general", "Test"),
    limit=5,
    offset=0
)
items['items']

# -----------------------------------------------
# Add items

from uuid import uuid4

await client.store.put_item(
    ("testing", "Test"),
    key=str(uuid4()),
    value={"todo": "Test SDK put_item"},
)

items = await client.store.search_items(
    ("testing", "Test"),
    limit=5,
    offset=0
)
items['items']

# -----------------------------------------------
# Delete items

[item['key'] for item in items['items']] # Get the keys

# Delete by key

await client.store.delete_item(
       ("testing", "Test"),
        key='3de441ba-8c79-4beb-8f52-00e4dcba68d4',
    )

# Check

items = await client.store.search_items(
    ("testing", "Test"),
    limit=5,
    offset=0
)
items['items']


# -----------------------------------------------