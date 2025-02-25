# ===============================================
# Chatbot with external memory
# ===============================================


# -----------------------------------------------
# Let's load our environment variables
# -----------------------------------------------

from dotenv import load_dotenv
load_dotenv()


# -----------------------------------------------
# Sqlite database
# -----------------------------------------------

import sqlite3

# In Memory

conn = sqlite3.connect(database=":memory:", check_same_thread=False)

# Create a local DB file

db_path = "example.db"
conn = sqlite3.connect(database=db_path, check_same_thread=False)

# Memory checkpointer

from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver(conn=conn)


# -----------------------------------------------
# LLM Model
# -----------------------------------------------

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# -----------------------------------------------
# MessageState
# -----------------------------------------------

from langgraph.graph import MessagesState

class State(MessagesState):
    summary : str


# -----------------------------------------------
# Call Model to get Summary
# -----------------------------------------------

from langchain_core.messages import SystemMessage

def call_model(state: State):

    # Get summary if exist
    summary = state.get("summary", "")

    if summary:
        system_message = f"Summary of earlier conversation: {summary} "
        messages = [SystemMessage(content=system_message) + state["messages"]]
    else:
        messages = state["messages"]
    
    response = llm.invoke(messages)

    return {"messages" : response}


# -----------------------------------------------
# Summarize the conversation
# -----------------------------------------------

from langchain_core.messages import HumanMessage, RemoveMessage

def summarize_conversation(state: State):

    summary = state.get("summary", "")
    
    if summary:

        summary_message = {
            f"This is summary for previous conversation : {summary}\n\n"
            "Extend the summary by taking into account the new message above"
            }
        
    else:
        summary_message = "Create Summary for the above conversation"

    # Add history to our prompt
    
    message = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(message)

    # Keep only last 2 messages

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary" : response.content, "messages" : delete_messages}


# -----------------------------------------------
# Generate Summary based on the conversation length
# -----------------------------------------------

from langgraph.graph import END

def should_continue(state : State):
    """
    Returns the next node to exceute.
    """

    messages = state["messages"]

    # If there are more than 6 messages, we will summarize the conversation

    if len(messages) > 6:
        return summarize_conversation
    
    return END


# -----------------------------------------------
# Adding Memory using checkpointer
# -----------------------------------------------

from langgraph.graph import StateGraph, START
from IPython.display import Image, display

# Graph

workflow = StateGraph(State)

# Nodes

workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

# Edges

workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile with checkpointer

graph = workflow.compile(checkpointer=memory)

# Display graph

display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Use of Threads
# -----------------------------------------------

config = {"configurable" : {"thread_id" : "5"}}

# Conversation

input_message = HumanMessage(content="Hi! I am Sushant")
output = graph.invoke({"messages" : [input_message]}, config)

for msg in output["messages"][-1:]:
    msg.pretty_print()


input_message = HumanMessage(content="What is my name?")
output = graph.invoke({"messages" : [input_message]}, config)

for msg in output["messages"][-1:]:
    msg.pretty_print()


input_message = HumanMessage(content="I like LLM and RL Agents")
output = graph.invoke({"messages" : [input_message]}, config)

for msg in output["messages"][-1:]:
    msg.pretty_print()


# Persiting State

config = {"configurable" : {"thread_id" : "5"}}
graph_state = graph.get_state(config)
graph_state


# -----------------------------------------------