import re
from time import sleep
from typing import Any, Optional

import arrow
import discord
from discord.ext import tasks

from consts import (
    COMMAND_PREFIX,
    DEBUG_MESSAGE_TEMPLATE,
    DISCORD_TOKEN,
    EMOJI_REMOVED_MESSAGE_TEMPLATE,
    GRANTED_MESSAGE,
    GUILD_NAME,
    MARHABAN_MESSAGE,
    MEMBER_ROLE_NAME,
    MODERATOR_USERNAME,
    PRESENTATION_CHANNEL_NAME,
    REMINDER_1_MESSAGE,
    REMINDER_2_MESSAGE,
    ROLES_CHANNEL_NAME,
    RULES_CHANNEL_NAME,
    SAVED_MESSAGE_TEMPLATE,
    UNANSWERED_MESSAGE_TEMPLATE,
)
from helpers import get_message_id_from_link
from tldr import summarise_chat


class ItkhoClient(discord.Client):
    def __init__(self, **options: Any) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents, **options)

    @property
    def guild(self) -> discord.Guild:
        if not hasattr(self, "_guild"):
            if not GUILD_NAME:
                raise ValueError("No guild name found")
            guilds = [g for g in self.guilds if g.name.lower() == GUILD_NAME.lower()]
            if len(guilds) != 1:
                raise ValueError(f"There must be one and only one {GUILD_NAME} guild.")
            self._guild = guilds[0]
        return self._guild

    @property
    def member_role(self) -> discord.Role:
        if not hasattr(self, "_member_role"):
            member_roles = [
                r
                for r in self.guild.roles
                if r.name.lower() == MEMBER_ROLE_NAME.lower()
            ]
            if len(member_roles) != 1:
                raise ValueError(
                    f"There must be one and only one '{MEMBER_ROLE_NAME}' role."
                )
            self._member_role = member_roles[0]
        return self._member_role

    @property
    def presentation_channel(self) -> discord.TextChannel:
        if not hasattr(self, "_presentation_channel"):
            presentation_channels = [
                c
                for c in self.guild.channels
                if c.name.lower() == PRESENTATION_CHANNEL_NAME.lower()
            ]
            if len(presentation_channels) != 1:
                raise ValueError(
                    f"There must be one and only one '{PRESENTATION_CHANNEL_NAME}' channel."
                )
            if not isinstance(presentation_channels[0], discord.TextChannel):
                raise ValueError("Presentation channel should be of type 'TextChannel'")
            self._presentation_channel = presentation_channels[0]
        return self._presentation_channel

    @property
    def roles_channel(self) -> discord.TextChannel:
        if not hasattr(self, "_roles_channel"):
            roles_channels = [
                c
                for c in self.guild.channels
                if c.name.lower() == ROLES_CHANNEL_NAME.lower()
            ]
            if len(roles_channels) != 1:
                raise ValueError(
                    f"There must be one and only one '{ROLES_CHANNEL_NAME}' channel."
                )
            if not isinstance(roles_channels[0], discord.TextChannel):
                raise ValueError("Roles channel should be of type 'TextChannel'")
            self._roles_channel = roles_channels[0]
        return self._roles_channel

    @property
    def rules_channel(self) -> discord.TextChannel:
        if not hasattr(self, "_rules_channel"):
            rules_channels = [
                c
                for c in self.guild.channels
                if c.name.lower() == RULES_CHANNEL_NAME.lower()
            ]
            if len(rules_channels) != 1:
                raise ValueError(
                    f"There must be one and only one '{RULES_CHANNEL_NAME}' channel."
                )
            if not isinstance(rules_channels[0], discord.TextChannel):
                raise ValueError("Rules channel should be of type 'TextChannel'")
            self._rules_channel = rules_channels[0]
        return self._rules_channel

    @property
    def moderator(self) -> discord.Member:
        if not hasattr(self, "_moderator"):
            moderators = [m for m in self.guild.members if m.name == MODERATOR_USERNAME]
            if len(moderators) != 1:
                raise ValueError(
                    f"There must be one and only one '{MODERATOR_USERNAME}' member."
                )
            self._moderator = moderators[0]
        return self._moderator

    @tasks.loop(hours=24)
    async def check_unanswered_messages(self):
        for channel in self.guild.channels:
            if not isinstance(channel, discord.TextChannel):
                continue
            async for message in channel.history(limit=1):
                if not re.search("\?(?!\w)", message.content):
                    continue
                if message.reactions:
                    continue
                if message.created_at > arrow.now().shift(days=-1).datetime:
                    continue
                await message.reply(
                    content=UNANSWERED_MESSAGE_TEMPLATE.format(
                        user_name=message.author.name,
                    )
                )

    @tasks.loop(hours=24 * 7)
    async def check_not_introduced_user(self):
        for user in self.guild.members:
            if self.member_role not in user.roles:
                if user.bot:
                    continue

                message_to_send = None
                # if user.joined_at < arrow.now().shift(weeks=-3).datetime:
                #     message_to_send = GOODBYE_MESSAGE
                #     # TODO: remove the user from the server
                #     # await user.kick()
                # el
                if user.joined_at < arrow.now().shift(weeks=-2).datetime:
                    message_to_send = REMINDER_2_MESSAGE.format(
                        presentation_channel_mention=self.presentation_channel.mention,
                    )
                elif user.joined_at < arrow.now().shift(weeks=-1).datetime:
                    message_to_send = REMINDER_1_MESSAGE.format(
                        presentation_channel_mention=self.presentation_channel.mention,
                    )

                if message_to_send:
                    try:
                        await user.send(content=message_to_send)
                        # TODO: abstract this part of sending DM from bot
                        dm_message = await self.moderator.send(
                            content=DEBUG_MESSAGE_TEMPLATE.format(
                                user_name=user.name,
                                user_mention=user.mention,
                                message_content=message_to_send.replace("\n", "\n> "),
                            )
                        )
                        await dm_message.add_reaction("❌")
                        sleep(10)
                    except:
                        continue

    async def on_ready(self):
        self.check_unanswered_messages.start()
        self.check_not_introduced_user.start()

    # HACK: because on_message overwrite the command
    # but I saw afterwards that it was possible: https://stackoverflow.com/a/67465330
    # see here for commmand inside a Bot class: https://stackoverflow.com/a/67913136
    async def run_command(self, message: discord.Message):
        content_without_prefix = "".join(message.content.split(COMMAND_PREFIX)[1:])
        content_without_prefix_split = content_without_prefix.split(" ")
        command, content = content_without_prefix_split[0], "".join(
            content_without_prefix_split[1:]
        )

        match command.lower():
            case "tldr":
                start_message_id = get_message_id_from_link(link=content)
                counter = 0
                messages = []
                async for message in message.channel.history():
                    counter += 1
                    if counter == 1:
                        # Skip the first one because it's the command itself
                        continue
                    messages.append(f"{message.author.name}: {message.content}\n")
                    if message.id == start_message_id or counter > 200:
                        break

                # Reverse the list to have oldest messages first
                messages.reverse()
                summary = summarise_chat(chat="\n".join(messages))
                await message.channel.send(content=summary)

    async def get_role(
        self,
        payload: discord.RawReactionActionEvent,
    ) -> Optional[discord.Role]:
        if payload.channel_id != self.roles_channel.id:
            return

        message = await self.roles_channel.fetch_message(payload.message_id)

        if not message.role_mentions:
            return

        role = message.role_mentions[0]

        if not role.name.lower().startswith("dev-"):
            return

        return role

    async def get_message(
        self,
        payload: discord.RawReactionActionEvent,
    ) -> Optional[discord.Message]:
        channel = await self.guild.fetch_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        return await channel.fetch_message(payload.message_id)

    async def get_dm_message(
        self,
        payload: discord.RawReactionActionEvent,
    ) -> discord.Message | None:
        dm_channel = await self.fetch_channel(payload.channel_id)
        if not isinstance(dm_channel, discord.channel.DMChannel):
            return
        return await dm_channel.fetch_message(payload.message_id)

    async def get_user(self, user_id: int) -> Optional[discord.Member]:
        return await self.guild.fetch_member(user_id)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        match payload.emoji.name:
            case "✅":
                role = await self.get_role(payload=payload)

                if not role:
                    return

                if not payload.member:
                    return

                await payload.member.add_roles(role)

            case "💾":
                message = await self.get_message(payload=payload)

                if not message or not payload.member:
                    return

                dm_message = await payload.member.send(
                    content=SAVED_MESSAGE_TEMPLATE.format(
                        message_content=message.content.replace("\n", "\n> "),
                        message_link=message.jump_url,
                    )
                )
                await dm_message.add_reaction("❌")

            case "❌":
                dm_message = await self.get_dm_message(payload=payload)

                if not dm_message:
                    return

                if dm_message.author.id == payload.user_id:
                    return

                await dm_message.delete()

            case "👋" | "🙏" | "🤞" | "🖕":
                message = await self.get_message(payload=payload)

                if not message or not payload.member:
                    return

                await message.clear_reaction(emoji=payload.emoji)

                dm_message = await payload.member.send(
                    content=EMOJI_REMOVED_MESSAGE_TEMPLATE.format(
                        emoji=payload.emoji.name,
                    )
                )
                await dm_message.add_reaction("❌")

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        match payload.emoji.name:
            case "✅":
                role = await self.get_role(payload=payload)

                if not role:
                    return

                # There is not member in the payload on the reaction removal
                member = await self.get_user(user_id=payload.user_id)
                if not member:
                    return

                await member.remove_roles(role)

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.content.startswith(COMMAND_PREFIX):
            await self.run_command(message=message)
            return

        if message.channel != self.presentation_channel:
            return

        # I should have been use "on_member_join" but it doesn't work.
        # The event doesn't fire (maybe because of wrong roles/permissions)
        if message.type == discord.MessageType.new_member:
            await message.author.send(
                content=MARHABAN_MESSAGE.format(
                    user_mention=message.author.mention,
                    presentation_channel_mention=self.presentation_channel.mention,
                )
            )
            await message.add_reaction("✅")
            return

        if (
            isinstance(message.author, discord.Member)
            and self.member_role not in message.author.roles
        ):
            await message.author.add_roles(self.member_role)
            await message.author.send(
                content=GRANTED_MESSAGE.format(
                    rules_channel_mention=self.rules_channel.mention,
                    roles_channel_mention=self.roles_channel.mention,
                )
            )
            await message.add_reaction("🤝")
            return


def run_discord_client():
    client = ItkhoClient()
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run_discord_client()
