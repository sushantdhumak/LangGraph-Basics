# LangGraph-Basics

### 1. The Simplest Graph 

Let's build a simple graph with 3 nodes and one conditional edge. 

![image](https://github.com/user-attachments/assets/8c8db214-7d12-4578-8cce-4d13aa5f3a73)

---

### 2. A Simple chain in Graph 

Let's build up to a simple chain that combines 4 concepts:

1. Using chat messages as our graph state
2. Using chat models in graph nodes
3. Binding tools to our chat model
4. Executing tool calls in graph nodes

![image](https://github.com/user-attachments/assets/57f5291e-708e-4dd7-8f7b-3e5e41cf81f2)

---

### 3. Route in Graph

Let's build a router, where the chat model routes between a direct response or a tool call based upon the user input.
This is an simple example of an agent, where the LLM is directing the control flow either by calling a tool or just responding directly.

![Screenshot 2025-02-03 230343](https://github.com/user-attachments/assets/363a8997-53d9-41f6-847e-e09586cd0246)

---

### 4. Agent in Graph

Let's build an agent using a general ReAct architecture

1. Act - let the model call specific tools
2. Observe - pass the tool output back to the model
3. Reason - let the model reason about the tool output to decide what to do next (e.g., call another tool or just respond directly)

![Screenshot 2025-02-06 223826](https://github.com/user-attachments/assets/2a1f08b8-f01c-4fb2-bb9d-65dcbcbad6c7)

---

### 5. Agent in Graph with Memory

Let's build an agent using a general ReAct architecture with Memory

1. Act - let the model call specific tools
2. Observe - pass the tool output back to the model
3. Reason - let the model reason about the tool output to decide what to do next (e.g., call another tool or just respond directly)

We will extend our agent by introducing memory.

![image](https://github.com/user-attachments/assets/1562c544-11ee-4d61-8a0d-2614ec18ceaf)

---

### 6. State Schema in LangGraph

The state schema represents the structure and types of data that our graph will use. All nodes are expected to communicate with that schema.

We will use

1. `TypeDict` class from python's `typing` module.
2. `DataClasses` from python
3. `Pydantic` - data validation and settings management library using Python type annotations.

---

### 7. State Reducers in LangGraph

The reducers, which specify how state updates are performed on specific keys / channels in the state schema.

We will use

1. `Annotated` type with reducer function like `operator.add`.
2. `Annotated` type with custom reducer function like `reduce_list`.
3. `MessagesState`
4. `Re-writing` and `Removal` of messages.

---

### 8. Multiple Schemas in LangGraph

The multiple schemas are needed when,

1. Internal nodes may pass information that is *not required* in the graph's input / output.
2. We may also want to use different input / output schemas for the graph.

---

### 9. Filtering and Trimming messages in LangGraph

Filtering and Trimming messages using,

1. Remove Message with MessageState
2. Filtering Messages
3. Trimming Messages

---

### 10. Chatbot with Message Summarization & Checkpoint Memory

Let's create a simple Chatbot with conversation summary. We'll equip that Chatbot with memory, supporting long-running conversations.

---

### 11. Chatbot with Message Summarization & External DB Memory

Let's upgrade our Chatbot with conversation summary and external memory (SqliteSaver checkpointer), supporting long-running conversations and chat presistence.

---

### 12. Streaming the Output of the Graph (Graph State and Tokens)

1. `.stream` and `.astream` are sync and async methods for streaming back results
2. Streaming graph state using streaming modes - 'updates' and 'values'
3. `.astream` events and each event is a dict with a few keys:   
* `event`: This is the type of event that is being emitted. 
* `name`: This is the name of event.
* `data`: This is the data associated with the event.
* `metadata`: Contains`langgraph_node`, the node emitting the event.

---

### 13. Human-in-the-loop | Breakpoints

For breakpoint, we need to simply compile the graph with `interrupt_before=["tools"]` where `tools` is our tools node.
This means that the execution will be interrupted before the node `tools`, which executes the tool call.

![image](https://github.com/user-attachments/assets/8db36385-11f5-4419-abcb-794bcca180da)

---

### 14. Human-in-the-loop | Editing State

Using breakpoints to modify the graph state.

---

### 15. Human-in-the-loop | Dynamic Breakpoints

This is an internal breakpoint to allow the graph **dynamically interrupt** itself!

This has a few specific benefits: 
1. Can do it conditionally (from inside a node based on developer-defined logic).
2. Can communicate to the user why its interrupted (by passing whatever you want to the `NodeInterrupt`).

---

### 16. Human-in-the-loop | Time Travel

Time travel in LangGraph supports debugging by viewing, re-playing, and even forking from past states. 

We can do this by: 
1. Browsing History - get_state and get_state_history.
   ![image](https://github.com/user-attachments/assets/4295dbc1-3092-4c9e-96f9-8c3403c9edcb)

   
2. Replaying - Re-run our agent from any of the prior steps.
   ![image](https://github.com/user-attachments/assets/1a4dc7b9-9b0a-486b-833a-50d2570a0f83)


3. Forking - Run from that same step, but with a different input.
   ![image](https://github.com/user-attachments/assets/5f8a6102-6019-4476-a6de-d9b36f67d281)

---

### 17. Parallelization

We can excecute the nodes in parallel (as required by the situation) using,

1. Fan-in and Fan-out
2. Waiting for other parallel node to finish
3. Setting the order of the state updates

![image](https://github.com/user-attachments/assets/43527675-fd50-4f07-bfc5-9582e94cdad4)


---

### 18. Sub-graphs

Sub-graphs allow you to create and manage different states in different parts of your graph. 
This is particularly useful for multi-agent systems, with teams of agents that each have their own state.

Let's consider an example:

1. I have a system that accepts logs
2. It performs two separate sub-tasks by different agents (summarize logs, find failure modes)
3. I want to perform these two operations in two different sub-graphs.

The most critical thing to understand is how the graphs communicate!

![image](https://github.com/user-attachments/assets/742c9f21-2e59-41c9-827f-fc6449c1c25c)


---

### 19. Map-Reduce

Map-reduce operations are essential for efficient task decomposition and parallel processing. 

It has two phases:

1. `Map` - Break a task into smaller sub-tasks, processing each sub-task in parallel.
2. `Reduce` - Aggregate the results across all of the completed, parallelized sub-tasks.

---

### 20. Research Assistant

Research is often laborious work offloaded to analysts. AI has considerable potential to assist with this.

However, research demands customization: raw LLM outputs are often poorly suited for real-world decision-making workflows. 

Customized, AI-based [research and report generation] workflows are a promising way to address this.

![image](https://github.com/user-attachments/assets/1993dc5b-ea8d-4b24-b5bd-1c3a24b22d75)

![output](https://github.com/user-attachments/assets/9a2e0603-a3b6-4a81-b0b3-e27dd3ce795a)

---

### 21. Chatbot with Memory

Let's build a chatbot that uses both `short-term (within-thread)` and `long-term (across-thread)` memory.

We'll focus on long-term, which will be facts about the user. These long-term memories will be used to create a personalized chatbot that can remember facts about the user.

It will save memory, as the user is chatting with it.

![image](https://github.com/user-attachments/assets/2c90b418-28b5-482a-88aa-3ed91d56b463)

---

### 22. Chatbot with Profile Schema

Our chatbot saved memories as a string. In practice, we often want memories to have a structure. 
 
In our case, we want this to be a single user profile. We'll extend our chatbot to save semantic memories to a single user profile

We'll also use a library, `Trustcall`, to update this schema with new information. 

---

### 23. Chatbot with Collection Schema

Sometimes we want to save memories to a `collection` rather than single profile. 

Let's update our chatbot to save memories to a collection.

We'll also show how to use `Trustcall` to update this collection. 

---

### 24. Memory Agent

Let's pull together the pieces learned to build an agent with long-term memory.

![image](https://github.com/user-attachments/assets/6ec1c208-fc57-4f72-aa18-f11e79fcd0ec)

---

### 25. Deployment - Creation and Connecting

The following information should be provided to create a LangGraph Platform deployment:

A LangGraph API Configuration file - `langgraph.json`
The graphs that implement the logic of the application - e.g., `task_maistro.py`
A file that specifies dependencies required to run the application - `requirements.txt`
Supply environment variables needed for the application to run - `.env` or `docker-compose.yml`

We can access the deployment through:
      
API: http://localhost:8123

Docs: http://localhost:8123/docs

LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123


LangGraph Server exposes many API endpoints for interacting with the deployed agent. These endpoints are group into a few common agent needs: 

**Runs**: Atomic agent executions

**Threads**: Multi-turn interactions or human in the loop

**Store**: Long-term memory

![image](https://github.com/user-attachments/assets/d503c62a-c36c-4c13-b084-86fa2b090bf1)

---

### 26. Double Texting

Seamless handling of double texting is important for handling real-world usage scenarios, especially in chat applications.

Users can send multiple messages in a row before the prior run(s) complete, and we want to ensure that we handle this gracefully.

We can follow below approaches to handle the different scenarios

**Reject**: A simple approach is to reject any new runs until the current run completes.

**Enqueue**: Enqueue any new runs until the current run completes.

**Interrupt**: Interrupt to interrupt the current run, but save all the work that has been done so far up to that point.

**Rollback**: Rollback to interrupt the prior run of the graph, delete it, and start a new run with the double-texted input.

![image](https://github.com/user-attachments/assets/e43fce95-6dda-432e-a215-30fe8dd7dfa2)

---
