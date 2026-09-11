# **Content Creation Agent**

### Overview: 
- This AI agent system will be able to create a script for the social media influencer on the basis of given topic. 


---

### The content creations includes:

1. Deciding the topic of content
2. Conducting Research on the topic
3. Creating a script based on virality and impact
4. Setting up environment and gathering requirements
5. Video recording (raw)
6. Video editing 
7. Evaluating overall video
8. Making update or change
9. Finalizing date, day and time to post
10. Post on social media.

### Types of Agent, roles and tools 

1. Requirement gather Agent
    - Role: to gather necessary required inputs from the user.
    - Tool: ask question tool
    - Middleware: Human-In-The-Loop to ask questions to users 
    - Input: None
    - Output: user requirements

2. Research Agent
    - Role: to perform a research on the given topic and gather context / information
    - Tool: web search, wikipedia, etc
    -Input: user requirements
    - Output: researched text 

3. Script Agent
    - Role: to generate a viral and quality script according to requirements 
    - Tool: RAG tool (to fetch research)
    - Input: user requirements and researched info
    - Output : script 

4. Evaluation Agent
    - Role: to evaluate and review generated script based on the user requirements, and virality
    - Tool: suggest changes to script agent 
    - Input: previous script 
    - Output: suggestions to update, change or modification or no change.

---

### AI Model to use for every agent
1. Requirement Agent: ollama qwen3:8b 
2. Research agent:  gemini-3.5-flash
3. Script agent : openai/gpt-oss-20b
4. Evaluation agent: qwen3:8b 
`Note: default model is qwen3:8b`

---

### Characteristics of AI Models

1. Function calling 
2. Multilingual 
3. Short term memory
4. Human-In-The-Loop
5. Structured Output
6. Thinking