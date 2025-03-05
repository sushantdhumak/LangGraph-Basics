# ===============================================
# Sub-graphs
# ===============================================

# Loading Environment Variables

from dotenv import load_dotenv
load_dotenv()


# -----------------------------------------------
# Let's consider a toy example:

# 1. System that accepts logs
# 2. Performs two separate sub-tasks by different agents (summarize logs, find failure modes)
# 3. Perform these two operations in two different sub-graphs.


# -----------------------------------------------
# Structure of the logs
# -----------------------------------------------

from typing_extensions import TypedDict
from typing import List, Optional, Annotated

class log(TypedDict):
    id: int
    question : str
    answer : str
    docs : Optional[List]
    grade : Optional[int]
    grader : Optional[str]
    feedback : Optional[str]


# -----------------------------------------------
# Sub-graph for failure analysis
# -----------------------------------------------

# Failure Analysis Input State

class FailureAnalysisState(TypedDict):
    cleaned_logs : List[log]
    failures : List[log]
    fa_summary : str
    processed_logs : List[str]

# Failure Analysis Output State

class FailureAnalysisOutputState(TypedDict):
    fa_summary : str
    processed_logs : List[str]

# Defining the functions for graph nodes

def get_failures(state):
    """
    Get logs that contains a failure
    """

    cleaned_logs = state["cleaned_logs"]
    failures = [log for log in cleaned_logs if "grade" in log]

    return {"failures": failures}

def generate_summary(state):
    """
    Generate summary of failures
    """
    
    failures = state["failures"]
    # Add fxn: fa_summary = summarize(failures)
    fa_summary = "Poor quality retrieval of Chroma documentation."
    
    return {"fa_summary": fa_summary, "processed_logs": [f"failure-analysis-on-log-{failure['id']}" for failure in failures]}


# Let's build the sub-graph

from langgraph.graph import StateGraph, START, END
from IPython.display import display, Image

fa_builder = StateGraph(input=FailureAnalysisState,output=FailureAnalysisOutputState)

# Nodes

fa_builder.add_node("get_failures", get_failures)
fa_builder.add_node("generate_summary", generate_summary)

# Edges

fa_builder.add_edge(START, "get_failures")
fa_builder.add_edge("get_failures", "generate_summary")
fa_builder.add_edge("generate_summary", END)

# Compile graph

graph = fa_builder.compile()

# Visualize graph

# display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Sub-graph for Question Summarization
# -----------------------------------------------

# Question Summarization Input State

class QuestionSummarizationState(TypedDict):
    cleaned_logs : List[log]
    report : str
    qs_summary : str
    processed_logs : List[str]

# Question Summarization Output State

class QuestionSummarizationOutputState(TypedDict):
    report : str
    processed_logs : List[str]

# Defining the functions for graph nodes

def generate_summary(state):
    """
    Generate summary of questions
    """
    
    cleaned_logs = state["cleaned_logs"]
    # Add fxn: summary = summarize(cleaned_logs)
    summary = "Questions focused on usage of ChatOllama and Chroma vector store."
    
    return {"qs_summary": summary, "processed_logs": [f"summary-on-log-{log['id']}" for log in cleaned_logs]}

def send_to_slack(state):
    """
    Send summary to Slack
    """
    
    qs_summary = state["qs_summary"]
    # Add fxn: report = report_generation(qs_summary)
    report = "foo bar baz"
    
    return {"report": report}


# Let's build the sub-graph

qs_builder = StateGraph(input=QuestionSummarizationState,output=QuestionSummarizationOutputState)

# Nodes

qs_builder.add_node("generate_summary", generate_summary)
qs_builder.add_node("send_to_slack", send_to_slack)

# Edges

qs_builder.add_edge(START, "generate_summary")
qs_builder.add_edge("generate_summary", "send_to_slack")
qs_builder.add_edge("send_to_slack", END)

# Compile graph

graph = qs_builder.compile()

# Visualize graph

# display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Adding sub-graphs to parent graph
# -----------------------------------------------

from operator import add

# Parent Entry graph state

class EntryGraphState(TypedDict):
    raw_logs : List[log]
    cleaned_logs : List[log] #Annotated[List[log], add]
    fa_summary : str
    report : str
    processed_logs : Annotated[List[str], add]

# Defining the functions for graph nodes

def clean_logs(state):
    # Get logs
    raw_logs = state["raw_logs"]
    # Data cleaning raw_logs -> docs 
    cleaned_logs = raw_logs
    return {"cleaned_logs": cleaned_logs}

# Let's build the parent graph

entry_builder = StateGraph(EntryGraphState)

# Nodes

entry_builder.add_node("clean_logs", clean_logs)
entry_builder.add_node("question_summarization", qs_builder.compile())
entry_builder.add_node("failure_analysis", fa_builder.compile())

# Edges

entry_builder.add_edge(START, "clean_logs")
entry_builder.add_edge("clean_logs", "failure_analysis")
entry_builder.add_edge("clean_logs", "question_summarization")
entry_builder.add_edge("failure_analysis", END)
entry_builder.add_edge("question_summarization", END)

# Compile graph

graph = entry_builder.compile()

# Visualize graph

display(Image(graph.get_graph(xray=1).draw_mermaid_png()))


# -----------------------------------------------
# Run graph using dummy log data
# -----------------------------------------------

question_answer = log(
    id="1",
    question="How can I import ChatOllama?",
    answer="To import ChatOllama, use: 'from langchain_community.chat_models import ChatOllama.'",
)

question_answer_feedback = log(
    id="2",
    question="How can I use Chroma vector store?",
    answer="To use Chroma, define: rag_chain = create_retrieval_chain(retriever, question_answer_chain).",
    grade=0,
    grader="Document Relevance Recall",
    feedback="The retrieved documents discuss vector stores in general, but not Chroma specifically",
)

raw_logs = [question_answer,question_answer_feedback]

graph.invoke({"raw_logs": raw_logs})

