import os
from dotenv import load_dotenv
from openai import OpenAI
from AI.Modelos import Modelos
from AI.Personas import Personas

load_dotenv()

api_key = os.environ.get("API_KEY")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

def gerarRespostaStream(historico : list, modelo : Modelos = Modelos.DeepSeek, persona : Personas = Personas.Roteirista):
    historico.insert(0, {
        "role": "system", 
        "content": persona.value
    })

    completion = client.chat.completions.create(
        model = modelo.value,
        messages = historico,
        stream=True
    )

    for chunk in completion:
        try:
            delta = chunk.choices[0].delta
            base = {
                "role": "assistant",
                "content": "",
                "reasoning": "",
            }
            updated = False
            if(delta.content and delta.content != ""):
                base["content"] = delta.content
                updated = True
            if(delta.reasoning and delta.reasoning != ""):
                base["reasoning"] = delta.reasoning
                updated = True

            if(updated):
                yield base
        except Exception as e:
            continue
