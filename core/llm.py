import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


def ask_llm(prompt: str, system: str = None, temperature: float = 0.3) -> str:
    """
    Send a prompt to the LLM and return the text response.
    
    Args:
        prompt: The user message to send
        system: Optional system prompt to set the model's behavior
        temperature: 0.0 = deterministic, 1.0 = creative. Keep low for analysis tasks.
    
    Returns:
        The model's response as a plain string
    """
    messages = []
    
    if system:
        messages.append({"role": "system", "content": system})
    
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
    )
    
    return response.choices[0].message.content


