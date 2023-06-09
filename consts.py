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

if not (SAVED_MESSAGE_TEMPLATE := os.getenv("SAVED_MESSAGE_TEMPLATE", "")):
    raise ValueError("No 'SAVED_MESSAGE_TEMPLATE' variable environment found")

if not (UNANSWERED_MESSAGE_TEMPLATE := os.getenv("UNANSWERED_MESSAGE_TEMPLATE", "")):
    raise ValueError("No 'UNANSWERED_MESSAGE_TEMPLATE' variable environment found")

if not (MODERATOR_USERNAME := os.getenv("MODERATOR_USERNAME", "")):
    raise ValueError("No 'MODERATOR_USERNAME' variable environment found")


# Channels
PRESENTATION_CHANNEL_NAME = "presentation"
RULES_CHANNEL_NAME = "rules"
MEMBER_ROLE_NAME = "member"
ROLES_CHANNEL_NAME = "roles"

# OpenIA
MODEL = "gpt-3.5-turbo-16k"

# Others
COMMAND_PREFIX = "$"
