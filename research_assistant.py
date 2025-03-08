# ===============================================
# Research Assistant - LangGraph
# ===============================================


# -----------------------------------------------
# Loading Environment variables
# -----------------------------------------------

from dotenv import load_dotenv
load_dotenv


# -----------------------------------------------
# LLM Model
# -----------------------------------------------

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)


# ***********************************************
# Generate Analyst - Structure and State
# ***********************************************

from pydantic import BaseModel, Field
from typing import List
from typing_extensions import TypedDict

class Analyst(BaseModel):
    affiliation: str = Field(
        description="Primary affiliation of the analyst.",
    )
    name: str = Field(
        description="Name of the analyst."
    )
    role: str = Field(
        description="Role of the analyst in the context of the topic.",
    )
    description: str = Field(
        description="Description of the analyst focus, concerns, and motives.",
    )

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"


class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations.",
    )


class GenerateAnalystsState(TypedDict):
    topic: str                  # Research topic
    max_analysts: int           # Maximum number of analysts
    human_analyst_feedback: str # Human analyst feedback
    analysts: List[Analyst]     # List of analysts


# -----------------------------------------------
# Create Analysts
# -----------------------------------------------

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

analyst_instructions = """
You are tasked with creating a set of AI analyst personas. 
Follow these instructions carefully:

1. First, review the research topic:
{topic}

2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts:
{human_analyst_feedback}

3. Determine the most interesting themes based upon documents and / or feedback above.

4. Pick the top {max_analysts} themes.

5. Assign one analyst to each theme.
"""

def create_analysts(state: GenerateAnalystsState):
    """
    Create analysts based on the provided state.
    """
    
    topic = state['topic']
    max_analysts = state['max_analysts']
    human_analyst_feedback = state.get('human_analyst_feedback', '')
    
    # Enforce structured output
    structured_llm = llm.with_structured_output(Perspectives)
    
    # System message
    system_message = analyst_instructions.format(topic=topic, 
                                                 human_analyst_feedback=human_analyst_feedback, 
                                                 max_analysts=max_analysts)
    
    # Generate question 
    analysts = structured_llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content="Generate the set of analysts.")])
    
    # Adding list of analysts to state
    return {"analysts": analysts.analysts}


def human_feedback(state: GenerateAnalystsState):
    """
    No-op node that should be interrupted on.
    """
    pass


def should_continue(state: GenerateAnalystsState):
    """
    Return the next node to execute.
    """
    human_analyst_feedback = state.get('human_analyst_feedback', None)

    if human_analyst_feedback:
        return "create_analysts"
    
    return END

    
# -----------------------------------------------
# Graph
# -----------------------------------------------

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import display, Image


# builder = StateGraph(GenerateAnalystsState)

# builder.add_node("create_analysts", create_analysts)
# builder.add_node("human_feedback", human_feedback)

# builder.add_edge(START, "create_analysts")
# builder.add_edge("create_analysts", "human_feedback")
# builder.add_conditional_edges("human_feedback", should_continue, ["create_analysts", END])

# # Compile using MemorySaver

# memory = MemorySaver()
# graph = builder.compile(interrupt_before=["human_feedback"], checkpointer=memory)

# # Visualize

# display(Image(graph.get_graph().draw_mermaid_png()))


# -----------------------------------------------
# Input and Graph execution
# -----------------------------------------------

# # Input

# topic = "The benefits of LLM agents."
# max_analysts = 3
# thread = {"configurable" : {"thread_id" : "2"}}

# # Graph execution

# for event in graph.stream({"topic" : topic, "max_analysts" : max_analysts}, thread, stream_mode="values"):
#     # Review
#     analysts = event.get('analysts', '')
#     if analysts:
#         for analyst in analysts:
#             print(f"Name: {analyst.name}")
#             print(f"Role: {analyst.role}")
#             print(f"Affiliation: {analyst.affiliation}")
#             print(f"Description: {analyst.description}")
#             print("-" * 50)

# # Get state and check the next node

# state = graph.get_state(thread)
# state.next

# # Human feedback

# human_analyst_feedback = """
# I think we need to focus on the following themes:

# - AI Ethics
# - AI Safety
# - AI Bias
# - AI Accountability
# - AI Transparency
# """

# graph.update_state(thread, {"human_analyst_feedback" : human_analyst_feedback}, as_node="human_feedback")

# # Continue graph execution

# for event in graph.stream(None, thread, stream_mode="values"):
#     # Review
#     analysts = event.get('analysts', '')
#     if analysts:
#         for analyst in analysts:
#             print(f"Name: {analyst.name}")
#             print(f"Role: {analyst.role}")
#             print(f"Affiliation: {analyst.affiliation}")
#             print(f"Description: {analyst.description}")
#             print("-" * 50)

# # Further human feedback

# further_human_feedback = None
# graph.update_state(thread, {"human_analyst_feedback" : further_human_feedback}, as_node="human_feedback")

# # Continue graph execution

# for event in graph.stream(None, thread, stream_mode="updates"):
#     print("---- Node ----")
#     node_name = next(iter(event.keys()))
#     print(node_name)

# final_state = graph.get_state(thread)
# analyst = final_state.values.get('analysts')

# final_state.next

# for analyst in analyst:
#     print(f"Name: {analyst.name}")
#     print(f"Role: {analyst.role}")
#     print(f"Affiliation: {analyst.affiliation}")
#     print(f"Description: {analyst.description}")
#     print("-" * 50)


# ***********************************************
# Conduct Interview - Structure and State
# ***********************************************

from langgraph.graph import MessagesState
from typing_extensions import Annotated
import operator

# Generate Question

class InterviewState(MessagesState):
    max_num_turns: int # Number turns of conversation
    context: Annotated[list, operator.add] # Source docs
    analyst: Analyst # Analyst asking questions
    interview: str # Interview transcript
    sections: list

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")


question_instructions = """
You are an analyst tasked with interviewing an expert to learn about a specific topic. 

Your goal is boil down to interesting and specific insights related to your topic.

1. Interesting: Insights that people will find surprising or non-obvious.
        
2. Specific: Insights that avoid generalities and include specific examples from the expert.

Here is your topic of focus and set of goals: {goals}
        
Begin by introducing yourself using a name that fits your persona, and then ask your question.

Continue to ask questions to drill down and refine your understanding of the topic.
        
When you are satisfied with your understanding, complete the interview with: "Thank you so much for your help!"

Remember to stay in character throughout your response, reflecting the persona and goals provided to you.
"""

def generate_question(state: InterviewState):
    """
    Node to generate a question
    """
    # Get state
    analyst = state["analyst"]
    messages = state["messages"]

    # Generate question 
    system_message = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_message)]+messages)
        
    # Write messages to state
    return {"messages": [question]}


# -----------------------------------------------
# Tools to generate Answer
# -----------------------------------------------

# Using web search tool

from langchain_community.tools.tavily_search import TavilySearchResults
tavily_search = TavilySearchResults(max_results=3)

# Using Wikipedia search tool

from langchain_community.document_loaders import WikipediaLoader
from langchain_core.messages import get_buffer_string

# Search query prompt

search_instructions = """
You will be given a conversation between an analyst and an expert. 

Your goal is to generate a well-structured query for use in retrieval and / or web-search related to the conversation.
        
First, analyze the full conversation.

Pay particular attention to the final question posed by the analyst.

Convert this final question into a well-structured web search query.
"""

def search_web(state: InterviewState):
    """
    Retrieve documents from web search
    """

    # Search Query

    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=search_instructions)] + state["messages"])

    # Search

    search_docs = tavily_search.invoke(search_query.search_query)

    # Format

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}


def search_wikipedia(state: InterviewState):
    """
    Retrieve documents from wikipedia
    """

    # Search Query

    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=search_instructions)] + state["messages"])

    # Search

    search_docs = WikipediaLoader(query=search_query.search_query,
                                  load_max_docs=2).load()

    # Format

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}


# -----------------------------------------------
# Generate Answer
# -----------------------------------------------

answer_instructions = """
You are an expert being interviewed by an analyst.

Here is analyst area of focus: {goals}. 
        
You goal is to answer a question posed by the interviewer.

To answer question, use this context:
        
{context}

When answering questions, follow these guidelines:
        
1. Use only the information provided in the context. 
        
2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.

3. The context contain sources at the topic of each individual document.

4. Include these sources your answer next to any relevant statements. For example, for source # 1 use [1]. 

5. List your sources in order at the bottom of your answer. [1] Source 1, [2] Source 2, etc
        
6. If the source is: <Document source="assistant/docs/llama3_1.pdf" page="7"/>' then just list: 
        
[1] assistant/docs/llama3_1.pdf, page 7 
        
And skip the addition of the brackets as well as the Document source preamble in your citation.
"""

def generate_answer(state: InterviewState):
    """
    Node to answer a question
    """
    # Get state
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]

    # Generate answer 
    system_message = answer_instructions.format(goals=analyst.persona, context=context)
    answer = llm.invoke([SystemMessage(content=system_message)] + messages)

    # Name the message as coming from the expert
    answer.name = "expert"

    # Append it to state
    return {"messages": [answer]}


def save_interview(state: InterviewState):
    """
    Node to save the interview
    """
    # Get Messages
    messages = state["messages"]
    
    # Convert interview to a string
    interview = get_buffer_string(messages)
    
    # Save to interviews key
    return {"interview": interview}
        

def route_messages(state: InterviewState, name: str = "expert"):
    """
    Route between question and answer
    """
    # Get messages
    messages = state["messages"]
    max_num_turns = state.get('max_num_turns', 2)

    # Check the number of expert answers 
    num_responses = len(
        [m for m in messages if isinstance(m, AIMessage) and m.name == name]
    )

    # End if expert has answered more than the max turns
    if num_responses >= max_num_turns:
        return 'save_interview'
    
    # This router is run after each question - answer pair 
    # Get the last question asked to check if it signals the end of discussion
    last_question = messages[-2]
    
    if "Thank you so much for your help" in last_question.content:
        return 'save_interview'
    
    return "ask_question"

    
# -----------------------------------------------
# Writing answer sections
# -----------------------------------------------

section_writer_instructions = """
You are an expert technical writer. 
            
Your task is to create a short, easily digestible section of a report based on a set of source documents.

1. Analyze the content of the source documents: 
- The name of each source document is at the start of the document, with the <Document tag.
        
2. Create a report structure using markdown formatting:
- Use ## for the section title
- Use ### for sub-section headers
        
3. Write the report following this structure:
a. Title (## header)
b. Summary (### header)
c. Sources (### header)

4. Make your title engaging based upon the focus area of the analyst: 
{focus}

5. For the summary section:
- Set up summary with general background / context related to the focus area of the analyst
- Emphasize what is novel, interesting, or surprising about insights gathered from the interview
- Create a numbered list of source documents, as you use them
- Do not mention the names of interviewers or experts
- Aim for approximately 400 words maximum
- Use numbered sources in your report (e.g., [1], [2]) based on information from source documents
        
6. In the Sources section:
- Include all sources used in your report
- Provide full links to relevant websites or specific document paths
- Separate each source by a newline. Use two spaces at the end of each line to create a newline in Markdown.
- It will look like:

### Sources
[1] Link or Document name
[2] Link or Document name

7. Be sure to combine sources. For example this is not correct:

[3] https://ai.meta.com/blog/meta-llama-3-1/
[4] https://ai.meta.com/blog/meta-llama-3-1/

There should be no redundant sources. It should simply be:

[3] https://ai.meta.com/blog/meta-llama-3-1/
        
8. Final review:
- Ensure the report follows the required structure
- Include no preamble before the title of the report
- Check that all guidelines have been followed

"""

def write_section(state: InterviewState):
    """
    Node to answer a question
    """

    # Get state
    interview = state["interview"]
    analyst = state["analyst"]
    context = state["context"]

    # Write section using either the gathered source docs from interview (context) or the interview itself (interview)
    system_message = section_writer_instructions.format(focus=analyst.description)
    section = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Use this source to write your section: {context}")]) 
                
    # Append it to state
    return {"sections": [section.content]}


# -----------------------------------------------
# Graph construction
# -----------------------------------------------

# Grpah
interview_builder = StateGraph(InterviewState)

# Nodes
interview_builder.add_node("ask_question", generate_question)
interview_builder.add_node("search_web", search_web)
interview_builder.add_node("search_wikipedia", search_wikipedia)
interview_builder.add_node("answer_question", generate_answer)
interview_builder.add_node("save_interview", save_interview)
interview_builder.add_node("write_section", write_section)

# Edges
interview_builder.add_edge(START, "ask_question")
interview_builder.add_edge("ask_question", "search_web")
interview_builder.add_edge("ask_question", "search_wikipedia")
interview_builder.add_edge("search_web", "answer_question")
interview_builder.add_edge("search_wikipedia", "answer_question")
interview_builder.add_conditional_edges("answer_question", route_messages, ["ask_question", "save_interview"])
interview_builder.add_edge("save_interview", "write_section")
interview_builder.add_edge("write_section", END)

# Interview
memory = MemorySaver()
interview_graph = interview_builder.compile(checkpointer=memory).with_config(run_name="Conduct Interview")

# Visualize the graph

display(Image(interview_graph.get_graph().draw_mermaid_png()))


# # -----------------------------------------------
# # Let's try to run interview using Analyst 1

# from IPython.display import Markdown

# messages = [HumanMessage(f"So you said you were writing an article on {topic}?")]
# thread = {"configurable": {"thread_id": "1"}}

# interview = interview_graph.invoke({"analyst": analysts[0], "messages": messages, "max_num_turns": 2}, thread)

# Markdown(interview['sections'][0])


# -----------------------------------------------
# Parallel Interviews using Map-Reduce
# -----------------------------------------------

class ResearchGraphState(TypedDict):
    topic: str # Reserch topic
    max_analysts: int # Maximum number of analysts
    human_analyst_feedback: str # Feedback from human
    analysts: List[Analyst] # List of analysts asking questions
    sections: Annotated[list, operator.add] # List of sections
    introduction: str # Introduction for the final report
    content: str # Content for the final report
    conclusion: str # Conclusion for the final report
    final_report: str # Final report


from langgraph.constants import Send

def initiate_all_interviews(state: ResearchGraphState):
    """
    Conditional edge to initiate all interviews via Send() API or return to create_analysts 
    """    

    # Check if human feedback
    human_analyst_feedback = state.get('human_analyst_feedback')

    if human_analyst_feedback:
        # Return to create_analysts
        return "create_analysts"
    else:
        # Otherwise kick off interviews in parallel via Send() API
        topic = state["topic"]
        return [Send("conduct_interview", {"analyst": analyst,
                                           "messages": [HumanMessage(
                                               content=f"So you said you were writing an article on {topic}?"
                                           )
                                                       ]}) for analyst in state["analysts"]]

# Report Writer

report_writer_instructions = """

You are a technical writer creating a report on this overall topic: 

{topic}
    
You have a team of analysts. Each analyst has done two things: 

1. They conducted an interview with an expert on a specific sub-topic.
2. They write up their finding into a memo.

Your task: 

1. You will be given a collection of memos from your analysts.
2. Think carefully about the insights from each memo.
3. Consolidate these into a crisp overall summary that ties together the central ideas from all of the memos. 
4. Summarize the central points in each memo into a cohesive single narrative.

To format your report:
 
1. Use markdown formatting. 
2. Include no pre-amble for the report.
3. Use no sub-heading. 
4. Start your report with a single title header: ## Insights
5. Do not mention any analyst names in your report.
6. Preserve any citations in the memos, which will be annotated in brackets, for example [1] or [2].
7. Create a final, consolidated list of sources and add to a Sources section with the `## Sources` header.
8. List your sources in order and do not repeat.

[1] Source 1
[2] Source 2

Here are the memos from your analysts to build your report from: 

{context}
"""

def write_report(state: ResearchGraphState):
    # Full set of sections
    sections = state["sections"]
    topic = state["topic"]

    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    # Summarize the sections into a final report
    system_message = report_writer_instructions.format(topic=topic, context=formatted_str_sections)    
    report = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Write a report based upon these memos.")]) 
    return {"content": report.content}


# Introduction Writer

intro_conclusion_instructions = """
You are a technical writer finishing a report on {topic}

You will be given all of the sections of the report.

You job is to write a crisp and compelling introduction or conclusion section.

The user will instruct you whether to write the introduction or conclusion.

Include no pre-amble for either section.

Target around 100 words, crisply previewing (for introduction) or recapping (for conclusion) all of the sections of the report.

Use markdown formatting. 

For your introduction, create a compelling title and use the # header for the title.

For your introduction, use ## Introduction as the section header. 

For your conclusion, use ## Conclusion as the section header.

Here are the sections to reflect on for writing: {formatted_str_sections}
"""

def write_introduction(state: ResearchGraphState):

    # Full set of sections
    sections = state["sections"]
    topic = state["topic"]

    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    # Summarize the sections into a final report
    
    instructions = intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)    
    intro = llm.invoke([instructions]+[HumanMessage(content=f"Write the report introduction")]) 

    return {"introduction": intro.content}


def write_conclusion(state: ResearchGraphState):

    # Full set of sections
    sections = state["sections"]
    topic = state["topic"]

    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    # Summarize the sections into a final report
    
    instructions = intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)
    conclusion = llm.invoke([instructions]+[HumanMessage(content=f"Write the report conclusion")]) 

    return {"conclusion": conclusion.content}


def finalize_report(state: ResearchGraphState):
    """"
    This is the "reduce" step where we gather all the sections, combine them, 
    and reflect on them to write the intro/conclusion
    """

    # Save full final report

    content = state["content"]

    if content.startswith("## Insights"):
        content = content.strip("## Insights")

    if "## Sources" in content:
        try:
            content, sources = content.split("\n## Sources\n")
        except:
            sources = None
    else:
        sources = None

    final_report = state["introduction"] + "\n\n---\n\n" + content + "\n\n---\n\n" + state["conclusion"]

    if sources is not None:
        final_report += "\n\n## Sources\n" + sources

    return {"final_report": final_report}
    

# -----------------------------------------------
# Graph construction
# -----------------------------------------------

builder = StateGraph(ResearchGraphState)

# Add nodes

builder.add_node("create_analysts", create_analysts)
builder.add_node("human_feedback", human_feedback)
builder.add_node("conduct_interview", interview_builder.compile())
builder.add_node("write_report", write_report)
builder.add_node("write_introduction", write_introduction)
builder.add_node("write_conclusion", write_conclusion)
builder.add_node("finalize_report", finalize_report)

# Add Edges

builder.add_edge(START, "create_analysts")
builder.add_edge("create_analysts", "human_feedback")
builder.add_conditional_edges("human_feedback", initiate_all_interviews, ["create_analysts", "conduct_interview"])
builder.add_edge("conduct_interview", "write_report")
builder.add_edge("conduct_interview", "write_introduction")
builder.add_edge("conduct_interview", "write_conclusion")
builder.add_edge(["write_conclusion", "write_report", "write_introduction"], "finalize_report")
builder.add_edge("finalize_report", END)

# Compile

memory = MemorySaver()
graph = builder.compile(interrupt_before=['human_feedback'], checkpointer=memory)

# Visualize the graph

display(Image(graph.get_graph(xray=1).draw_mermaid_png()))


# -----------------------------------------------
# Let's run the graph with an open-ended question
# -----------------------------------------------

# Inputs
max_analysts = 3 
topic = "The benefits of adopting LangGraph as an agent framework"
thread = {"configurable": {"thread_id": "1"}}

# Run the graph until the first interruption
for event in graph.stream({"topic":topic,
                           "max_analysts":max_analysts}, 
                          thread, 
                          stream_mode="values"):
    
    analysts = event.get('analysts', '')
    if analysts:
        for analyst in analysts:
            print(f"Name: {analyst.name}")
            print(f"Affiliation: {analyst.affiliation}")
            print(f"Role: {analyst.role}")
            print(f"Description: {analyst.description}")
            print("-" * 50)  


# Human feedback
graph.update_state(thread, {"human_analyst_feedback": None}, as_node="human_feedback")

# Continue the graph execution
for event in graph.stream(None, thread, stream_mode="updates"):
    print("----Node----")
    node_name = next(iter(event.keys()))
    print(node_name)


# **********************************************
# Final report
# **********************************************

from IPython.display import Markdown

final_state = graph.get_state(thread)
report = final_state.values.get('final_report')

Markdown(report)


# -----------------------------------------------