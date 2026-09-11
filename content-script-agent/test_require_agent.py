from langchain.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.types import Command
from requirement_agent_sys_prompt import RequirementAgentPrompt
from dotenv import load_dotenv
requires = RequirementAgentPrompt()
load_dotenv()
@tool("ask_user", description="Asking questions to user to gather missing requirements.")

def ask_user(questions: list[str], reason: str) -> str:
    """
    Ask the user for multiple pieces of information
    required to continue requirements analysis.

    questions:
        List of specific questions.

    reason:
        Why this information is necessary.
    """
    return f"Asked user: {questions}. Reason: {reason}"

def extract_model_response(result) -> str:
    """
    Extracts and returns only the model's text response from the agent result,
    excluding metadata, dictionaries, or list structures.
    """
    if isinstance(result, dict) and "messages" in result and result["messages"]:
        last_msg = result["messages"][-1]
        content = getattr(last_msg, "content", last_msg)
    elif hasattr(result, "content"):
        content = result.content
    else:
        content = result

    # Handle list of content blocks (e.g. [{'type': 'text', 'text': '...'}])
    if isinstance(content, list):
        extracted_texts = []
        for block in content:
            if isinstance(block, str):
                extracted_texts.append(block)
            elif isinstance(block, dict):
                if "text" in block:
                    extracted_texts.append(str(block["text"]))
                elif "content" in block:
                    extracted_texts.append(str(block["content"]))
            elif hasattr(block, "text"):
                extracted_texts.append(str(block.text))
        return "\n".join(extracted_texts).strip()

    # Handle dictionary content
    if isinstance(content, dict):
        if "text" in content:
            return str(content["text"]).strip()
        if "content" in content:
            return str(content["content"]).strip()

    # Handle string content
    return str(content).strip()


print("defining model...")
model = init_chat_model(
    model = "gemini-3.6-flash",
    model_provider="google-genai"
)
print("defining agent...")
agent = create_agent(
    model=model,
    system_prompt=requires.requirementAgentSysPrompt(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "ask_user": {
                "allowed_decisions": ["respond"]
                }
            },
            description_prefix="Requirements Agent needs your input",
        )
    ],
    checkpointer=InMemorySaver(),
    tools=[ask_user]
)
user_input = "I want to create a content to explain types of cars on YouTube"
thread_id = "project-001"
config = {
    "configurable": {
    "thread_id": thread_id
    }
}
    
print(f"\n[User Initial Prompt]: {user_input}\n")
print("Executing Requirements Agent...")
    
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": user_input
            }
        ]
    },
    config=config,
)

while True:
    state = agent.get_state(config)
    # Check if agent has hit an interrupt
    if state.tasks and state.tasks[0].interrupts:
        interrupt = state.tasks[0].interrupts[0]
        interrupt_val = interrupt.value
            
        # Extract questions and reason from action_requests
        action_requests = interrupt_val.get("action_requests", [])
        print("\n" + "="*60)
        print("HUMAN-IN-THE-LOOP INTERRUPT TRIGGERED")
        print("="*60)
            
        for req in action_requests:
            args = req.get("args", {})
            reason = args.get("reason", "More information needed.")
            questions = args.get("questions", [])
                
            print(f"\nReason for Questions: {reason}")
            print("\nQuestions from Requirements Agent:")
            for i, q in enumerate(questions, 1):
                print(f"  {i}. {q}")
            
        print("\n" + "-"*60)
        try:
            user_response = input("\nPlease provide your answer / clarification: ").strip()
        except EOFError:
            print("\n[Non-interactive execution detected] Providing automated sample feedback...")
            user_response = "pefered language is Hindi. Time limit is 3 to 4 minutes. Focusing of Sports cars with examples such as Ferrari, Porsche.Prefer informative tone."
            print(f"Sample response: {user_response}")

        if not user_response:
            user_response = "No additional details provided."

        print("\nResuming Requirements Agent with your feedback...")
        resume_command = Command(resume={
            "decisions": [
                {
                    "type": "respond",
                    "message": user_response
                }
            ]
        })
        result = agent.invoke(resume_command, config=config)
    else:
        # Agent completed execution
        print("\n" + "="*60)
        print("FINAL REQUIREMENTS SPECIFICATION")
        print("="*60 + "\n")
        response_text = extract_model_response(result)
        print(response_text)
        break