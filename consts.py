import os

from dotenv import load_dotenv

load_dotenv()

if not (DISCORD_TOKEN := os.getenv("DISCORD_TOKEN", "")):
    raise ValueError("No 'DISCORD_TOKEN' variable environment found")

if not (GUILD_NAME := os.getenv("GUILD_NAME", "")):
    raise ValueError("No 'GUILD_NAME' variable environment found")

if not (MARHABAN_MESSAGE := os.getenv("MARHABAN_MESSAGE", "")):
    raise ValueError("No 'MARHABAN_MESSAGE' variable environment found")

if not (GRANTED_MESSAGE := os.getenv("GRANTED_MESSAGE", "")):
    raise ValueError("No 'GRANTED_MESSAGE' variable environment found")


PRESENTATION_CHANNEL_NAME = "presentation"
RULES_CHANNEL_NAME = "rules"
MEMBER_ROLE_NAME = "member"
ROLES_CHANNEL_NAME = "roles"
