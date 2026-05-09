import httpx
from typing import List, Dict
from src.config import config


async def call_yandexgpt(
        messages: List[Dict],
        temperature: float = 0.3,
        max_tokens: int = 300
) -> Dict:
    """Асинхронный запрос к YandexGPT API"""

    yandex_messages = []
    for msg in messages:
        yandex_messages.append({
            "role": msg["role"],
            "text": msg["content"]
        })

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    headers = {
        "Authorization": f"Api-Key {config.YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "modelUri": f"gpt://{config.YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": str(max_tokens)
        },
        "messages": yandex_messages
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, headers=headers, json=body)

            if response.status_code == 200:
                data = response.json()
                reply_text = data['result']['alternatives'][0]['message']['text']
                tokens_used = data['result']['usage']['totalTokens']

                return {
                    "success": True,
                    "content": reply_text,
                    "tokens_used": tokens_used
                }
            else:
                return {
                    "success": False,
                    "error": f"YandexGPT API error {response.status_code}: {response.text}"
                }

        except httpx.TimeoutException:
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
