# LangGraph-Basics

### 1. The Simplest Graph 

Let's build a simple graph with 3 nodes and one conditional edge. 

![image](https://github.com/user-attachments/assets/8c8db214-7d12-4578-8cce-4d13aa5f3a73)


### 2. A Simple chain in Graph 

Let's build up to a simple chain that combines 4 concepts:

1. Using chat messages as our graph state
2. Using chat models in graph nodes
3. Binding tools to our chat model
4. Executing tool calls in graph nodes

![image](https://github.com/user-attachments/assets/57f5291e-708e-4dd7-8f7b-3e5e41cf81f2)


### 3. Route in Graph

Let's build a router, where the chat model routes between a direct response or a tool call based upon the user input.
This is an simple example of an agent, where the LLM is directing the control flow either by calling a tool or just responding directly.

![Screenshot 2025-02-03 230343](https://github.com/user-attachments/assets/363a8997-53d9-41f6-847e-e09586cd0246)
