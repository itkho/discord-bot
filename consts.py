import os

from dotenv import load_dotenv

load_dotenv()

if not (DISCORD_TOKEN := os.getenv("DISCORD_TOKEN", "")):
    raise ValueError("No 'DISCORD_TOKEN' variable environment found")

if not (GUILD_NAME := os.getenv("GUILD_NAME", "")):
    raise ValueError("No 'GUILD_NAME' variable environment found")

if not (MARHABAN_MESSAGE := os.getenv("MARHABAN_MESSAGE", "")):
    raise ValueError("No 'MARHABAN_MESSAGE' variable environment found")

if not (REMINDER_1_MESSAGE := os.getenv("REMINDER_1_MESSAGE", "")):
    raise ValueError("No 'REMINDER_1_MESSAGE' variable environment found")

if not (REMINDER_2_MESSAGE := os.getenv("REMINDER_2_MESSAGE", "")):
    raise ValueError("No 'REMINDER_2_MESSAGE' variable environment found")

if not (GOODBYE_MESSAGE := os.getenv("GOODBYE_MESSAGE", "")):
    raise ValueError("No 'GOODBYE_MESSAGE' variable environment found")

if not (GRANTED_MESSAGE := os.getenv("GRANTED_MESSAGE", "")):
    raise ValueError("No 'GRANTED_MESSAGE' variable environment found")

if not (SAVED_MESSAGE_TEMPLATE := os.getenv("SAVED_MESSAGE_TEMPLATE", "")):
    raise ValueError("No 'SAVED_MESSAGE_TEMPLATE' variable environment found")

if not (UNANSWERED_MESSAGE_TEMPLATE := os.getenv("UNANSWERED_MESSAGE_TEMPLATE", "")):
    raise ValueError("No 'UNANSWERED_MESSAGE_TEMPLATE' variable environment found")

if not (
    TEMPLATE_WITH_USER_QUESTIONED := os.getenv("TEMPLATE_WITH_USER_QUESTIONED", "")
):
    raise ValueError("No 'TEMPLATE_WITH_USER_QUESTIONED' variable environment found")

if not (
    TEMPLATE_WITH_CHANNEL_MODERATOR := os.getenv("TEMPLATE_WITH_CHANNEL_MODERATOR", "")
):
    raise ValueError("No 'TEMPLATE_WITH_CHANNEL_MODERATOR' variable environment found")

if not (DEBUG_MESSAGE_TEMPLATE := os.getenv("DEBUG_MESSAGE_TEMPLATE", "")):
    raise ValueError("No 'DEBUG_MESSAGE_TEMPLATE' variable environment found")

if not (
    EMOJI_REMOVED_MESSAGE_TEMPLATE := os.getenv("EMOJI_REMOVED_MESSAGE_TEMPLATE", "")
):
    raise ValueError("No 'EMOJI_REMOVED_MESSAGE_TEMPLATE' variable environment found")

if not (MODERATOR_USERNAME := os.getenv("MODERATOR_USERNAME", "")):
    raise ValueError("No 'MODERATOR_USERNAME' variable environment found")


# Channels
PRESENTATION_CHANNEL_NAME = "présentation-🎙"
RULES_CHANNEL_NAME = "règlement-📜"
ROLES_CHANNEL_NAME = "roles-🏷"
FAQ_CHANNEL_NAME = "faq-❔"

# Roles
PRESENTATION_DONE_ROLE_NAME = "presentation-done-🎙"
RULES_ACCEPTED_ROLE_NAME = "rules-accepted-📜"

# OpenIA
MODEL = "gpt-3.5-turbo-16k"

# Others
COMMAND_PREFIX = "$"

JOIN_THREAD_MENTIONS_PREFIX = "Frères ajoutés au thread via le 👀 :"
JOIN_THREAD_MENTIONS_SEPARATOR = " "
