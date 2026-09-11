# testing script agent without any external research
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage
from script_agent_sys_pompt import ScriptAgentPrompt
from dotenv import load_dotenv
script = ScriptAgentPrompt()
load_dotenv()

print("defining model...")
script_model = init_chat_model(
    model="openai/gpt-oss-20b",
    model_provider="groq",
    temperature=0.7
)

print("defining script agent...")
script_agent = create_agent(
    model=script_model,
    tools=[],
    checkpointer=InMemorySaver(),
    system_prompt=script.scriptAgentSysPrompt()
)
user_requirement = "audience: car enthusiasts or general public\nvideo duration:60 seconds\nlanguage:english\nlanguage tone:informative and casual\title: types of cars based on body styls (sedan, SUV, hatchbacks)\nplatform: Youtube and Instagram"
human_msg = HumanMessage(f"generate the script considering user's requirement. User requirements:\n{user_requirement}")
config = {"configurable": {"thread_id": "script_thread_1"}}

print("=================== AI AGENT RESPONSE ========================")
response = script_agent.invoke(
            {'messages':[human_msg]},
            config=config,
        )
print(response)