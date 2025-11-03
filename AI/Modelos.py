from enum import Enum
class Modelos(Enum):
    DeepSeek = "tngtech/deepseek-r1t2-chimera:free"
    GEMINI_25_FLASH = "google/gemini-2.5-flash"

    @property
    def valor(self):
        modelos = {
            "DeepSeek": {
                "name": "deepseek-r1t2-chimera",
                "model": "tngtech/deepseek-r1t2-chimera:free",
                "provider": "deepseek"
            },
            "GEMINI_25_FLASH": {
                "name": "gemini-2.5-flash",
                "model": "google/gemini-2.5-flash",
                "provider": "gemini"
            }
        }
        return modelos[self.name]
