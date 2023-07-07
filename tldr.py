import openai

from consts import MODEL


def summarise_chat(chat: str) -> str:
    """Return a summary of the chat given"""

    try:
        completion = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un bot sur un server discord, et tu résumes les points importants de la conversation que l'on te fourni en 3 à 5 puces MAXIMUM",
                    # "Englobe de '**' les parties importants (ex: **bold**)""  <-- doesn't work
                },
                {"role": "user", "content": chat},
            ],
            max_tokens=400,
        )

        return completion.choices[0].message.content

    except Exception as exc:
        return str(exc)
