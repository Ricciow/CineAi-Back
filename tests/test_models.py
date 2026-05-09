import pytest
from src.models.ai import AIModel

def test_ai_model_info():
    model = AIModel.GEMINI_3_FLASH
    info = model.info
    assert info["name"] == "gemini-3-flash"
    assert info["provider"] == "gemini"
    
    model = AIModel.MINIMAX_M2_5
    info = model.info
    assert info["name"] == "minimax-m2.5"
    assert info["provider"] == "minimax"
