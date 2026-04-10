from enum import Enum

class AIModel(Enum):
    GEMINI_3_FLASH = "google/gemini-3-flash-preview"
    GEMMA_4 = "google/gemma-4-31b-it:free"
    MINIMAX_M2_5 = "minimax/minimax-m2.5:free"

    @property
    def info(self):
        models = {
            "GEMINI_3_FLASH": {
                "name": "gemini-3-flash",
                "model": "google/gemini-3-flash-preview",
                "provider": "gemini"
            },
            "GEMMA_4": {
                "name": "gemma-4",
                "model": "google/gemma-4-31b-it:free",
                "provider": "gemini"
            },
            "MINIMAX_M2_5": {
                "name": "minimax-m2.5",
                "model": "minimax/minimax-m2.5:free",
                "provider": "minimax"
            }
        }
        return models[self.name]

class AIPersona(Enum):
    ROTEIRISTA = "Você é um roteirista, ajude o usuário a redigir roteiros quando pedido"
