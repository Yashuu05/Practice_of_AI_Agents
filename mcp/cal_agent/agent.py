import asyncio
from dotenv import load_dotenv

# Load environment variables (.env file)
load_dotenv()

# Import LangChain's MCP client adapter.
from langchain_mcp_adapters.client import MultiServerMCPClient

# Import LangChain's agent constructor and model initializer.
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model


async def main():
    # Configure connection to the HTTP MCP server.
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    # Discover tools from the MCP server.
    tools = await client.get_tools()
    print(tools)

    # Create the LLM instance
    model = init_chat_model("gemini-3.5-flash", model_provider="google-genai")

    # Create the AI agent.
    # The MCP tools are now available to the agent.
    agent = create_agent(
        model=model,
        tools=tools,

        # Give the agent instructions about its behavior.
        system_prompt=(
            "You are a helpful mathematical assistant. "
            "Use the available tools whenever calculations are required."
            "show calulcation step by step along with the result."
        ),
    )

    # Ask the agent a question.
    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Calculate 20 multiply by 10 "
                        "then subract 100"
                    ),
                }
            ]
        }
    )

    # Extract and print the final answer.
    final_message = result["messages"][-1]
    
    if isinstance(final_message.content, list):
        for block in final_message.content:
            if isinstance(block, dict) and "text" in block:
                print(block["text"])
            elif hasattr(block, "text"):
                print(block.text)
            else:
                print(block)
    else:
        print(final_message.content)

# Start the program.
if __name__ == "__main__":
    asyncio.run(main())
     