from enum import Enum

class AIModel(Enum):
    # Google AI Studio
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    # OpenRouter Free Models
    STEP_3_5_FLASH = "stepfun/step-3.5-flash:free"
    MINIMAX_M2_5 = "minimax/minimax-m2.5:free"

    @property
    def provider(self):
        return self.info["provider"]

    @property
    def info(self):
        models = {
            "GEMINI_2_5_FLASH": {
                "name": "gemini-2.5-flash",
                "model": "gemini-2.5-flash",
                "provider": "gemini"
            },
            "STEP_3_5_FLASH": {
                "name": "step-3.5-flash",
                "model": "stepfun/step-3.5-flash:free",
                "provider": "openrouter"
            },
            "MINIMAX_M2_5": {
                "name": "minimax-m2.5",
                "model": "minimax/minimax-m2.5:free",
                "provider": "openrouter"
            }
        }
        return models.get(self.name, {
            "name": self.name,
            "model": self.value,
            "provider": "openrouter" # Default fallback
        })

class AIPersona(Enum):
    ROTEIRISTA = "Você é um roteirista, ajude o usuário a redigir roteiros quando pedido"
