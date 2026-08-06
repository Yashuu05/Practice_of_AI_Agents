from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

@tool
def calculator(operation: str, num1: float, num2: float) -> float:
    """Performs basic mathematical operations.
    
    Args:
        operation: The operation to perform ('add', 'subtract', 'multiply', 'divide').
        num1: The first number.
        num2: The second number.
    """
    if operation == 'add':
        return num1 + num2
    elif operation == 'subtract':
        return num1 - num2
    elif operation == 'multiply':
        return num1 * num2
    elif operation == 'divide':
        if num2 == 0:
            raise ValueError("Cannot divide by zero")
        return num1 / num2
    else:
        raise ValueError(f"Unsupported operation: {operation}")

class CalculatorAgent:

    def __init__(self):
        # LangGraph requires a config with a thread_id when using memory checkpointers
        self.config = {"configurable": {"thread_id": "calculator_thread_1"}}

    def init_memory(self):
        check_pointer = InMemorySaver()
        return check_pointer

    def create_model(self):
        model = init_chat_model(
            model="gemini-3.1-flash-lite",
            model_provider="google-genai",
            temperature = 0.5
        )
        return model 
    
    def calculator_agent(self, model):
        # Using langgraph's create_react_agent which supports memory checkpointers natively
        agent = create_agent(
            model=model,
            tools=[calculator],
            checkpointer=self.init_memory(),
            system_prompt="You are an expert mathematician responsible to calculate results based on given inputs. Explain results step by step."
        )

        return agent 

    def run_agent(self, input_prompt, agent):
        # Added config to the invoke call, necessary for checkpointer
        result = agent.invoke(
            {"messages": [{"role": "user", "content": f"{input_prompt}"}]},
            config=self.config
        )
        output = result["messages"][-1].content[0]['text']
        if output:
            print(output)

if __name__ == "__main__":
    print("=========== AGENT INITIATED ==========")
    user_prompt = str(input("enter prompt= "))

    if user_prompt:
        try:
            cal_obj = CalculatorAgent()
            print("creating model...")
            gemini_model = cal_obj.create_model()
            print("creating agent...")
            calculator_agent = cal_obj.calculator_agent(model=gemini_model)
            print("AI Response:\n")
            cal_obj.run_agent(input_prompt=user_prompt, agent=calculator_agent)

        except Exception as e:
            print(f"error: {e}")
    
    else:
        print("Warining: Prompt should not be empty.")