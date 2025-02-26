# ===============================================
# Streaming - Human in loop
# ===============================================


# -----------------------------------------------
# Let's load our environment variables
# -----------------------------------------------

from dotenv import load_dotenv
load_dotenv()


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
        return "summarize_conversation"
    
    return END


# -----------------------------------------------
# Adding Memory using checkpointer
# -----------------------------------------------

from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
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

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Display graph

display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Stream using Stream mode = "updates"
# -----------------------------------------------

config = {"configurable" : {"thread_id" : "1"}}

input_message = HumanMessage(content="Hi! I am Sushant")

for chunk in graph.stream({"messages" : [input_message]}, config, stream_mode="updates"):
    print(chunk)

# Print just the state update

for chunk in graph.stream({"messages" : [input_message]}, config, stream_mode="updates"):
    chunk["conversation"]["messages"].pretty_print()


# -----------------------------------------------
# Stream using Stream mode = "values"
# -----------------------------------------------

config = {"configurable" : {"thread_id" : "2"}}

input_message = HumanMessage(content="Hi! I am Sushant")

for event in graph.stream({"messages" : [input_message]}, config, stream_mode="values"):
    for msg in event["messages"]:
        msg.pretty_print()
    print("---"*25)


# -----------------------------------------------
# Streaming tokens using Stream mode = "values"
# -----------------------------------------------

config = {"configurable" : {"thread_id" : "3"}}

input_message = HumanMessage(content="Tell me about the RL Agents")

async for event in graph.astream_events({"messages" : [input_message]}, config, version="v2"):
    print(f"Node: {event['metadata'].get('langgraph_node', '')}. Type: {event['event']}. Name: {event['name']}")


# -----------------------------------------------
# Streaming tokens for a specific node
# -----------------------------------------------

node_to_stream = "conversation"

config = {"configurable" : {"thread_id" : "4"}}

input_message = HumanMessage(content="Tell me about the RL Agents")

async for event in graph.astream_events({"messages" : [input_message]}, config, version="v2"):

    if event["event"] == "on_chat_model_stream" and event["metadata"].get('langgraph_node', '') == node_to_stream:
        print(event["data"])


# -----------------------------------------------
# Streaming tokens for a node using 'chunk' key
# -----------------------------------------------

node_to_stream = "conversation"

config = {"configurable" : {"thread_id" : "5"}}

input_message = HumanMessage(content="Tell me about the RL Agents")

async for event in graph.astream_events({"messages" : [input_message]}, config, version="v2"):

    if event["event"] == "on_chat_model_stream" and event["metadata"].get('langgraph_node', '') == node_to_stream:
        data = event["data"]
        print(data["chunk"].content, end="|")


# -----------------------------------------------