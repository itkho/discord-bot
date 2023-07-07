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
                    # Best result in english
                    "content": "You are connected to a bot on a Discord server, and you summarize the important points of the conversation provided to you in a maximum of 3 bullet points, explicitly mentioning each person's opinions and what they say. Anwser in French",
                    # "content": "Tu es connecté à un bot sur un server discord, et tu résumes les points importants de la conversation que l'on te fourni en 3 puces MAXIMUM en citant EXPLICITEMENT par leurs noms les avis de chacun et qui dit quoi",
                    # "Englobe de '**' les parties importants (ex: **bold**)""  <-- doesn't work
                },
                {"role": "user", "content": chat},
            ],
            max_tokens=400,
        )

        return completion.choices[0].message.content

    except Exception as exc:
        return str(exc)
