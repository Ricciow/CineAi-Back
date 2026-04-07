from enum import Enum

class AIModel(Enum):
    GEMINI_3_FLASH = "google/gemini-3-flash-preview"
    STEP_3_5_FLASH = "stepfun/step-3.5-flash:free"
    MINIMAX_M2_5 = "minimax/minimax-m2.5:free"
    GEMMA_4_31B = "google/gemma-4-31b-it"

    @property
    def info(self):
        models = {
            "GEMINI_3_FLASH": {
                "name": "gemini-3-flash-preview",
                "model": "google/gemini-3-flash-preview",
                "provider": "gemini"
            },
            "STEP_3_5_FLASH": {
                "name": "step-3.5-flash",
                "model": "stepfun/step-3.5-flash:free",
                "provider": "stepfun"
            },
            "MINIMAX_M2_5": {
                "name": "minimax-m2.5",
                "model": "minimax/minimax-m2.5:free",
                "provider": "minimax"
            },
            "GEMMA_4_31B": {
                "name": "gemma-4-31b-it",
                "model": "google/gemma-4-31b-it",
                "provider": "gemini"
            }
        }
        return models[self.name]

class AIPersona(Enum):
    ROTEIRISTA = "Você é um roteirista, ajude o usuário a redigir roteiros quando pedido"
