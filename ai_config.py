import os
from agents import OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()

api_key = os.environ.get("API_KEY")

if not api_key:
    raise ValueError("API_KEY não definida no ambiente de variáveis")


external_client = AsyncOpenAI(
    api_key = api_key, 
    base_url="https://openrouter.ai/api/v1"
)

model = OpenAIChatCompletionsModel(
    model = "tngtech/deepseek-r1t2-chimera:free",
    openai_client = external_client
)

config = RunConfig(
    model = model,
    model_provider = external_client,
    tracing_disabled = True
)