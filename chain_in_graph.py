# ===============================================
# Chain in Graph
# ===============================================

# Let's build up to a simple chain that combines 4 concepts:

# Using chat messages as our graph state
# Using chat models in graph nodes
# Binding tools to our chat model
# Executing tool calls in graph nodes

# -----------------------------------------------

from dotenv import load_dotenv
load_dotenv()

# -----------------------------------------------
# Let's create a list of messages
# -----------------------------------------------

from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage

messages = [AIMessage(content=f"So you said you were researching LLM Agents?", name="Model")]
messages.append(HumanMessage(content=f"Yes, that's correct.", name="Sushant"))
messages.append(AIMessage(content=f"Great, what would you like to learn about.", name="Model"))
messages.append(HumanMessage(content=f"I want to learn about the 3 best Agentic framworks.", name="Sushant"))

for msg in messages:
    msg.pretty_print()


# -----------------------------------------------
# Let's load a chat model and invoke above list of messages
# -----------------------------------------------

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o-mini")

result = model.invoke(messages)

pprint(result.content)
pprint(result.response_metadata)


# -----------------------------------------------
# Let's create and use a simple tool
# -----------------------------------------------

def multiply(a: int, b: int) -> int:
    """
    Multiply a and b.

    Args:
        a: first int
        b: second int
    """	

    return a * b

llm_with_tools = model.bind_tools([multiply])

tool_call = llm_with_tools.invoke([HumanMessage(content=f"What is 2 multiplied by 3", name="Sushant")])

pprint(tool_call)
pprint(tool_call.additional_kwargs['tool_calls'])


# -----------------------------------------------
# Let's create a graph state for the list of messages
# -----------------------------------------------

from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

initial_message = [AIMessage(content="Hello! How can I assist you?", name="Model"),
                   HumanMessage(content="I want to learn about LLM Agents", name="Sushant")
                  ]

new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")

add_messages(initial_message, new_message)

pprint(messages)


# -----------------------------------------------
# Let's use reducer functioncreate a graph state
# -----------------------------------------------

from langgraph.graph import MessagesState

class MessagesState(MessagesState):
    pass


# -----------------------------------------------
# Let's use MessagesState with a graph
# -----------------------------------------------

from langgraph.graph import StateGraph, START, END

# Build a node
def tool_calling_llm(state: MessagesState):
    return {"messages" : [llm_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)

builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)

# Compile graph 
graph = builder.compile()

# View
from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Let's invoke the graph with a simple message
# -----------------------------------------------

messages = graph.invoke({"messages": HumanMessage(content="Hello! How are you?")})

for msg in messages["messages"]:
    msg.pretty_print()


# -----------------------------------------------
# Now, let's invoke the graph with multiplication question
# -----------------------------------------------

messages = graph.invoke({"messages": HumanMessage(content="What is 2 multiplied by 3")})

for msg in messages["messages"]:
    msg.pretty_print()