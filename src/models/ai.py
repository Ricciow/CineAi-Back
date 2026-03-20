from enum import Enum

class AIModel(Enum):
    DEEPSEEK = "tngtech/deepseek-r1t2-chimera:free"
    GEMINI_2_5_FLASH = "google/gemini-2.5-flash"

    @property
    def info(self):
        models = {
            "DEEPSEEK": {
                "name": "deepseek-r1t2-chimera",
                "model": "tngtech/deepseek-r1t2-chimera:free",
                "provider": "deepseek"
            },
            "GEMINI_2_5_FLASH": {
                "name": "gemini-2.5-flash",
                "model": "google/gemini-2.5-flash",
                "provider": "gemini"
            }
        }
        return models[self.name]

class AIPersona(Enum):
    ROTEIRISTA = "Você é um roteirista, ajude o usuário a redigir roteiros quando pedido"
