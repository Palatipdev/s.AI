from dotenv import load_dotenv
load_dotenv()
import anthropic
client = anthropic.Anthropic()

element = '{"handle":"35F45","layer":"2","type":"TEXT","text":"A7  ประตูหน้าต่าง"}'
prompt = f"What construction element is this? {element}"

msg = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=200,
    messages=[{"role": "user", "content": prompt}],
)
print(msg.content[0].text)
