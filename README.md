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
