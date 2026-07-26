from dotenv import load_dotenv
load_dotenv()
import anthropic
client = anthropic.Anthropic()
import json
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pydantic import BaseModel
from typing import Literal
from pydantic import Field


class Classification(BaseModel):
    type: str 
    confidence: Literal["low", "medium", "high"]
    reason: str = Field(description="one short phrase, max 30 words")

element = '{"handle":"35F45","layer":"2","type":"TEXT","text":"A7  ประตูหน้าต่าง"}'
prompt = f"""Classify this CAD element into one of item type. What construction element is it?

for type: Use a short lowercase noun like: door, window, column, footing, annotation, pile, other." That nudges toward a stable vocabulary without locking it.


Element: {element}"""

msg = client.messages.parse(
    model="claude-haiku-4-5-20251001",
    max_tokens=200,
    messages=[{"role": "user", "content": prompt}],
    output_format=Classification,
)

result = msg.parsed_output
print(f"Type: {result.type}, confidence: {result.confidence}, reason: {result.reason}")
