from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.chat_models import init_chat_model
import base64
from PIL import Image
import io
from dotenv import load_dotenv
load_dotenv()

IMAGE_MODEL = "gemini-3.5-flash-lite"

def image_to_base64(image_path: str) -> str:
    """
    Open an image using Pillow and convert it to Base64.

    Parameters:
        image_path: Path of the image file.

    Returns:
        Base64 encoded image string.
    
    """
    # open image
    image = Image.open(image_path)
    # convert to RGB
    image = image.convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    return image_base64

def ask_about_image(image_path: str, question: str) -> str:
    """
    Send an image and a question to the LangChain agent.

    Parameters:
        image_path: Path to image.
        question: Question about the image.

    Returns:
        Text response from the model.
    """
    print("\nprocessing image...")
    # convert image to base_64
    image_base64 = image_to_base64(image_path=image_path)

    print("defining model...")
    # define model
    model = init_chat_model(
        model=IMAGE_MODEL,
        model_provider="google-genai"
    )

    print("defining agent...")
    # create agent
    agent = create_agent(
        model=model,
        system_prompt=(
            "You are a helpful AI assistant. "
            "Analyse images carefully and answer questions "
            "based only on what you can observe "
        ),
    )

    message = HumanMessage(
        content=[
            {
                "type":"text",
                "text":question,
            },
            {
                "type":"image",
                "base64":image_base64,
                "mime_type": "image/jpeg"
            }
        ]
    )

    print("printing response...")
    response = agent.invoke({
        "messages": [message]
    })

    return response["messages"][-1].content

if __name__ == "__main__":

    output = ask_about_image(image_path="image.jpeg", question="describe the image in few words")
    print("============ AI RESPONSE ===========")
    print(output)