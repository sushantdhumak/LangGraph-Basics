# ===============================================
# Filtering and trimming messages
# ===============================================

# -----------------------------------------------
# Let's load our environment variables

from dotenv import load_dotenv
load_dotenv()

# -----------------------------------------------
# Messages as State
# -----------------------------------------------

from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

messages = [AIMessage(content="So you said your were researching on LLM Agents", name="AI")]
messages.append(HumanMessage(content="Yes, I know about LLM Agents. But what others should I learn about?", name="Sushant"))

for msg in messages:
    msg.pretty_print()

llm = ChatOpenAI(model="gpt-4o-mini")
llm.invoke(messages)

# -----------------------------------------------

# Let's try with a simple graph and MessagesState

from IPython.display import Image, display
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END

# Chat Model node

def chat_model_node(state:MessagesState):
    return {"messages" : llm.invoke(state["messages"])}

# Define Graph

builder = StateGraph(MessagesState)

builder.add_node("chat_model", chat_model_node)

builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)

graph = builder.compile()

# Display Graph

display(Image(graph.get_graph().draw_mermaid_png()))

# Runs the Graph

output = graph.invoke({"messages":messages})

for msg in output["messages"]:
    msg.pretty_print()


# -----------------------------------------------
# Reducer to use the last 2 messages only
# -----------------------------------------------

from langchain_core.messages import RemoveMessage

# Nodes

def filter_messages(state:MessagesState):
    # Let's keep only last 2 messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages" : delete_messages}

def chat_model_node(state:MessagesState):
    return {"messages" : llm.invoke(state["messages"])}

# Graph

builder = StateGraph(MessagesState)

builder.add_node("filter_messages", filter_messages)
builder.add_node("chat_model", chat_model_node)

builder.add_edge(START, "filter_messages")
builder.add_edge("filter_messages", "chat_model")
builder.add_edge("chat_model", END)

graph = builder.compile()

# Display Graph

display(Image(graph.get_graph().draw_mermaid_png()))

# Message list

messages = [AIMessage("Hi.", name="AI", id="1")]
messages.append(HumanMessage("Hi.", name="Sushant", id="2"))
messages.append(AIMessage("So you said you were researching on LLM Agents?", name="AI", id="3"))
messages.append(HumanMessage("Yes, I know about LLM Agents. But what others should I learn about?", name="Sushant", id="4"))

# Invoke

output = graph.invoke({'messages': messages})

for m in output['messages']:
    m.pretty_print()


# -----------------------------------------------
# Filtering Messages - keep only last message
# -----------------------------------------------

# Node

def chat_model_node(state:MessagesState):
    return {"messages" : llm.invoke(state["messages"][-1:])}

# Graph

builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# Display Graph

display(Image(graph.get_graph().draw_mermaid_png()))

# Append a follow-up question to previous LLM response

messages.append(output['messages'][-1])
messages.append(HumanMessage(f"Tell me more about Reinforcement Learning!", name="Sushant"))

for msg in messages:
    msg.pretty_print()

# Invoke using message filtering

output = graph.invoke({'messages': messages})

for m in output['messages']:
    m.pretty_print()


# -----------------------------------------------
# Trim Messages - based on set number of tokens
# -----------------------------------------------

from langchain_core.messages import trim_messages

# Node

def chat_model_node(state:MessagesState):
    messages = trim_messages(
        state["messages"],
        max_tokens=100,
        strategy="last",
        token_counter=ChatOpenAI(model="gpt-4o-mini"),
        allow_partial=False,
    )
    return {"messages" : llm.invoke(messages)}

# Graph

builder = StateGraph(MessagesState)

builder.add_node("chat_model", chat_model_node)

builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)

graph = builder.compile()

# Display Graph

display(Image(graph.get_graph().draw_mermaid_png()))

# Append a follow-up question to previous LLM response

messages.append(output['messages'][-1])
messages.append(HumanMessage(f"Tell me more about Reinforcement Learning!", name="Sushant"))

# Invoke, using message trimming in the chat_model_node 

messages_out_trim = graph.invoke({'messages': messages})

for msg in messages_out_trim['messages']:
    msg.pretty_print()


# -----------------------------------------------