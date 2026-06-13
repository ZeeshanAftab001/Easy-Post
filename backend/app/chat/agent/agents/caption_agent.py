from langchain_openai import ChatOpenAI 
from dotenv import load_dotenv


load_dotenv()



llm=ChatOpenAI()

async def generate_caption(topic, tone, platform):
    prompt = f"""
    Generate a {tone} caption for {platform}
    Topic: {topic}
    Include hashtags.
    """

    response = llm.invoke(prompt)

    return response.content