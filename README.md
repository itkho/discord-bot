# itkho-discord-bot
Discord bot for the itkho guild

Install deps with: 
```py
pipx install uv
uv sync --frozen
uv run ntlk_download.py
```
(python 3.11.3 was used)

Run it with:
```py
uvicorn api:app --reload
```

For development purpose, you can just run the discord bot with:
```py
python bot.py  # or, even better, in debugging mode through your IDE
```

For now, the bot run here, on a server with free option: https://dashboard.render.com/web/srv-chd6t33hp8u0163j5phg

The API is accessible from here: https://itkho-bot.onrender.com

And this cron keeps the server awake: https://console.cron-job.org


## Command line used on the server 
```sh
pip install uv && uv sync --frozen && uv run ntlk_download.py
```