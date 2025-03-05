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
