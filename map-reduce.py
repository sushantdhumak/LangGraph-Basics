# ===============================================
# Map-Reduce in Graph

# Map - Break a task into smaller sub-tasks, processing each sub-task in parallel.
# Reduce - Aggregate the results across all of the completed, parallelized sub-tasks.
# ===============================================


# -----------------------------------------------
# Load environment variables
# -----------------------------------------------

from dotenv import load_dotenv

load_dotenv()


# -----------------------------------------------
# Prompts and LLM
# -----------------------------------------------

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# -----------------------------------------------
# State and Output Schema
# -----------------------------------------------

from pydantic import BaseModel
from typing_extensions import TypedDict
from typing import Annotated
import operator

class OverallState(TypedDict):
    topic: str
    subjects: list[str]
    jokes: Annotated[list, operator.add]
    best_joke : str


# -----------------------------------------------
# Generate subjects for jokes
# -----------------------------------------------

subjects_prompt = """ 
Generate a list of 3 sub-topics that are all related to this overall topic: {topic}. 
"""

class Subjects(BaseModel):
    subjects: list[str]

def generate_subjects(state: OverallState):
    
    prompt = subjects_prompt.format(topic=state["topic"])
    response = llm.with_structured_output(Subjects).invoke(prompt)

    return {"subjects": response.subjects}


# -----------------------------------------------
# Generate jokes
# -----------------------------------------------

joke_prompt = """ 
Generate a joke about {subject} 
"""

class JokeState(TypedDict):
    subject: str

class Joke(BaseModel):
    joke: str

def generate_joke(state: JokeState):

    prompt = joke_prompt.format(subject=state["subject"])
    response = llm.with_structured_output(Joke).invoke(prompt)

    return {"jokes": [response.joke]}


# -----------------------------------------------
# Joke generation - Map
# -----------------------------------------------

from langgraph.constants import Send

def continue_joke_generation(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]


# -----------------------------------------------
# Best joke selection - Reduce
# -----------------------------------------------

best_joke_prompt = """ 
Below are a bunch of jokes about {topic}. 
Select the best one! 
Return the ID of the best one, starting 0 as the ID for the first joke. 
Jokes: \n\n  {jokes} 
"""

class BestJoke(BaseModel):
    id: int

def get_best_joke(state: OverallState):

    jokes = "\n\n".join(state["jokes"])

    prompt = best_joke_prompt.format(topic=state["topic"], jokes=jokes)
    response = llm.with_structured_output(BestJoke).invoke(prompt)

    return {"best_joke": state["jokes"][response.id]}


# -----------------------------------------------
# Graph definition
# -----------------------------------------------

from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display

builder = StateGraph(OverallState)

builder.add_node("generate_subjects", generate_subjects)
builder.add_node("generate_joke", generate_joke)
builder.add_node("get_best_joke", get_best_joke)

builder.add_edge(START, "generate_subjects")
builder.add_conditional_edges("generate_subjects", continue_joke_generation, ["generate_joke"])
builder.add_edge("generate_joke", "get_best_joke")
builder.add_edge("get_best_joke", END)

graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Let's invoke the graph
# -----------------------------------------------

for msg in graph.stream({"topic": "Humans"}):
    print(msg)


# -----------------------------------------------