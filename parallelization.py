# ===============================================
# Parallelization in Graph - Human in loop
# ===============================================


# -----------------------------------------------
# Load environment variables
# -----------------------------------------------

from dotenv import load_dotenv

load_dotenv()


# -----------------------------------------------
# Define the State class and return Value node
# -----------------------------------------------

from typing import Any
from typing_extensions import TypedDict

class State(TypedDict):
    state : str


class ReturnNodeValue:
    def __init__(self, node_secret : str):
        self._value = node_secret
    
    def __call__(self, state: State) -> Any:
        print(f"Adding {self._value} to {state["state"]}")
        return {"state" : [self._value]}


# -----------------------------------------------
# Create a Simple graph
# -----------------------------------------------

from langgraph.graph import StateGraph, START, END
from IPython.display import display, Image

builder = StateGraph(State)

builder.add_node("a", ReturnNodeValue("I am in A"))
builder.add_node("b", ReturnNodeValue("I am in B"))
builder.add_node("c", ReturnNodeValue("I am in C"))
builder.add_node("d", ReturnNodeValue("I am in D"))

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", "c")
builder.add_edge("c", "d")
builder.add_edge("d", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

# Let's invoke the graph

graph.invoke({"state" : []})


# -----------------------------------------------
# Let's fan-out from a to b and c and fan-in to d
# -----------------------------------------------

builder = StateGraph(State)

builder.add_node("a", ReturnNodeValue("I am in A"))
builder.add_node("b", ReturnNodeValue("I am in B"))
builder.add_node("c", ReturnNodeValue("I am in C"))
builder.add_node("d", ReturnNodeValue("I am in D"))

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------

# Let's invoke the graph

from langgraph.errors import InvalidUpdateError

try:
    graph.invoke({"state" : []})
except InvalidUpdateError as e:
    print(e)


# -----------------------------------------------
# Use operator.add to perform list concatenation
# -----------------------------------------------

import operator
from typing import Annotated

class State(TypedDict):
    state : Annotated[list, operator.add]

builder = StateGraph(State)

builder.add_node("a", ReturnNodeValue("I am in A"))
builder.add_node("b", ReturnNodeValue("I am in B"))
builder.add_node("c", ReturnNodeValue("I am in C"))
builder.add_node("d", ReturnNodeValue("I am in D"))

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

# Let's invoke the graph

graph.invoke({"state" : []})


# -----------------------------------------------
# Waiting for nodes to finish
# One parallel path has more steps 
# -----------------------------------------------

builder = StateGraph(State)

builder.add_node("a", ReturnNodeValue("I am in A"))
builder.add_node("b", ReturnNodeValue("I am in B"))
builder.add_node("b1", ReturnNodeValue("I am in B1"))
builder.add_node("c", ReturnNodeValue("I am in C"))
builder.add_node("d", ReturnNodeValue("I am in D"))

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b1")
builder.add_edge(["b1", "c"], "d")
builder.add_edge("d", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

# Let's invoke the graph

graph.invoke({"state" : []})


# -----------------------------------------------
# Setting the order of state updates
# -----------------------------------------------

def sorting_reducer(left, right):

    if not isinstance(left, list):
        left = [left]

    if not isinstance(right, list):
        right = [right]

    return sorted(left + right, reverse=False)

class State(TypedDict):
    state : Annotated[list, sorting_reducer]


builder = StateGraph(State)

builder.add_node("a", ReturnNodeValue("I am in A"))
builder.add_node("b", ReturnNodeValue("I am in B"))
builder.add_node("b1", ReturnNodeValue("I am in B1"))
builder.add_node("c", ReturnNodeValue("I am in C"))
builder.add_node("d", ReturnNodeValue("I am in D"))

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b1")
builder.add_edge(["b1", "c"], "d")
builder.add_edge("d", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

# Let's invoke the graph

graph.invoke({"state" : []})


# -----------------------------------------------
# Example - Working with LLMs
# -----------------------------------------------

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Define the state class

class State(TypedDict):
    question : str
    answer : str
    context : Annotated[list, operator.add]


from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools import TavilySearchResults

# Web Search

def search_web(state):
    """
    Retrives documents from Web Search    
    """

    # Search
    
    tavily_search = TavilySearchResults(max_results=3)
    search_docs = tavily_search.invoke(state["question"])

    # Format
    
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context" : [formatted_search_docs]}


# Wiki Search

def search_wikipedia(state):
    """
    Retrives documents from Wikipedia    
    """

    # Search
    search_docs = WikipediaLoader(query=state["question"], 
                                  load_max_docs=2).load()

    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context" : [formatted_search_docs]}


# Node function to generate answer

def generate_answer(state):
    
    """ Node to answer a question """

    # Get state
    context = state["context"]
    question = state["question"]

    # Template
    answer_template = """Answer the question {question} using this context: {context}"""
    answer_instructions = answer_template.format(question=question, 
                                                       context=context)    
    
    # Answer
    answer = llm.invoke([SystemMessage(content=answer_instructions)]+[HumanMessage(content=f"Answer the question.")])
      
    # Append it to state
    return {"answer": answer}


# Build the graph

builder = StateGraph(State)

builder.add_node("search_web", search_web)
builder.add_node("search_wikipedia", search_wikipedia)
builder.add_node("generate_answer", generate_answer)

builder.add_edge(START, "search_wikipedia")
builder.add_edge(START, "search_web")
builder.add_edge("search_wikipedia", "generate_answer")
builder.add_edge("search_web", "generate_answer")
builder.add_edge("generate_answer", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))


# Let's invoke the graph

result = graph.invoke({"question" : "What is Grok LLM Model?", "context" : []})
result['answer'].content


# -----------------------------------------------