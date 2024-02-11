import re
from time import sleep
from typing import Any

import arrow
import discord
from discord.ext import tasks

from consts import (
    AUTO_THREAD_ENABLED_DEFAULT,
    AUTO_THREAD_ENABLED_KEYWORD,
    CHANNEL_MODERATOR_KEYWORD,
    COMMAND_PREFIX,
    DEBUG_MESSAGE_TEMPLATE,
    DISCORD_TOKEN,
    EMOJI_REMOVED_MESSAGE_TEMPLATE,
    FAQ_CHANNEL_NAME,
    GOODBYE_MESSAGE,
    GRANTED_MESSAGE,
    GUILD_NAME,
    JOIN_THREAD_MENTIONS_PREFIX,
    JOIN_THREAD_MENTIONS_SEPARATOR,
    MARHABAN_MESSAGE,
    MODERATOR_USERNAME,
    PRESENTATION_CHANNEL_NAME,
    PRESENTATION_DONE_ROLE_NAME,
    REMINDER_1_MESSAGE,
    REMINDER_2_MESSAGE,
    ROLES_CHANNEL_NAME,
    RULES_ACCEPTED_ROLE_NAME,
    RULES_CHANNEL_NAME,
    SAVED_MESSAGE_TEMPLATE,
    SKIP_REMINDER_MESSAGE,
    TEMPLATE_WITH_CHANNEL_MODERATOR,
    TEMPLATE_WITH_USER_QUESTIONED,
    UNANSWERED_MESSAGE_TEMPLATE,
)
from generate_title import generate_title
from helpers import get_message_id_from_link
from tldr import summarise_chat


class EditThreadModal(discord.ui.Modal, title="Modifier le titre du thread"):
    new_title = discord.ui.TextInput(label="Nouveau titre")

    async def on_submit(self, interaction: discord.Interaction):
        if not isinstance(interaction.channel, discord.Thread):
            return
        await interaction.channel.edit(name=self.new_title.value)
        await interaction.response.defer()


class EditThreadButtonView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(self.EditThreadButton())

    class EditThreadButton(discord.ui.Button):
        def __init__(self):
            super().__init__(
                label="Modifier le titre du thread",
                emoji="✏️",
                style=discord.ButtonStyle.primary,
            )

        async def callback(self, interaction: discord.Interaction):
            if not isinstance(interaction.channel, discord.Thread):
                return

            await interaction.response.send_modal(EditThreadModal())


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
    def presentation_done_role(self) -> discord.Role:
        if not hasattr(self, "_presentation_done_role"):
            presentation_done_roles = [
                r
                for r in self.guild.roles
                if r.name.lower() == PRESENTATION_DONE_ROLE_NAME.lower()
            ]
            if len(presentation_done_roles) != 1:
                raise ValueError(
                    f"There must be one and only one '{PRESENTATION_DONE_ROLE_NAME}' role."
                )
            self._presentation_done_role = presentation_done_roles[0]
        return self._presentation_done_role

    @property
    def rules_accepted_role(self) -> discord.Role:
        if not hasattr(self, "_rules_accepted_role"):
            rules_accepted_roles = [
                r
                for r in self.guild.roles
                if r.name.lower() == RULES_ACCEPTED_ROLE_NAME.lower()
            ]
            if len(rules_accepted_roles) != 1:
                raise ValueError(
                    f"There must be one and only one '{RULES_ACCEPTED_ROLE_NAME}' role."
                )
            self._rules_accepted_role = rules_accepted_roles[0]
        return self._rules_accepted_role

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
    def faq_channel(self) -> discord.TextChannel:
        if not hasattr(self, "_faq_channel"):
            faq_channels = [
                c
                for c in self.guild.channels
                if c.name.lower() == FAQ_CHANNEL_NAME.lower()
            ]
            if len(faq_channels) != 1:
                raise ValueError(
                    f"There must be one and only one '{FAQ_CHANNEL_NAME}' channel."
                )
            if not isinstance(faq_channels[0], discord.TextChannel):
                raise ValueError("Faq channel should be of type 'TextChannel'")
            self._faq_channel = faq_channels[0]
        return self._faq_channel

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

    async def on_ready(self):
        self.check_unanswered_messages.start()
        self.check_not_introduced_user.start()

    @tasks.loop(hours=24)
    async def check_unanswered_messages(self):
        def is_old_question(message: discord.Message) -> bool:
            if message.created_at > arrow.now().shift(days=-1).datetime:
                return False
            if [r for r in message.reactions if r.emoji != "👀"]:
                return False
            if not re.search(r"\?(?!\w)", message.content):
                return False
            return True

        async def send_reminder_for_unanswered_message(
            unanswered_message: discord.Message,
            channel_moderator: discord.Member | None,
        ):
            content = UNANSWERED_MESSAGE_TEMPLATE.format(
                user_mention=unanswered_message.author.mention,
            )
            if (
                unanswered_message.reference
                and isinstance(unanswered_message.reference.resolved, discord.Message)
                and unanswered_message.reference.resolved.author
            ):
                content += TEMPLATE_WITH_USER_QUESTIONED.format(
                    user_questioned_mention=unanswered_message.reference.resolved.author.mention,
                )

            if channel_moderator:
                content += TEMPLATE_WITH_CHANNEL_MODERATOR.format(
                    channel_moderator_mention=channel_moderator.mention,
                )

            await unanswered_message.reply(content=content)

        for channel in self.guild.channels:
            if not isinstance(channel, discord.TextChannel):
                continue

            for thread in channel.threads:
                if (
                    not thread.created_at
                    or not thread.last_message_id
                    or thread.created_at < arrow.now().shift(weeks=-1).datetime
                ):
                    continue

                channel_moderator = None
                if isinstance(channel, discord.TextChannel):
                    channel_moderator = await self.get_channel_moderator(
                        channel=channel
                    )

                # Unanswered message in thread
                try:
                    last_message = await thread.fetch_message(thread.last_message_id)
                except discord.NotFound:
                    # Probably because it's a system message
                    pass
                else:
                    if is_old_question(message=last_message):
                        await send_reminder_for_unanswered_message(
                            unanswered_message=last_message,
                            channel_moderator=channel_moderator,
                        )
                        continue

                # Unanswered message in channel
                try:
                    started_message = await channel.fetch_message(thread.id)
                except discord.NotFound:
                    # Can happen when the started message is deleted
                    pass
                else:
                    if is_old_question(message=started_message):
                        if not [
                            r for r in started_message.reactions if r.emoji == "🔂"
                        ] and last_message.author in [
                            self.user,
                            started_message.author,
                        ]:
                            someone_relied = any(
                                [
                                    m
                                    async for m in thread.history(
                                        limit=10, oldest_first=False
                                    )
                                    if m.author
                                    not in [self.user, started_message.author]
                                ]
                            )
                            if not someone_relied:
                                await started_message.add_reaction("🔂")
                                await send_reminder_for_unanswered_message(
                                    unanswered_message=started_message,
                                    channel_moderator=channel_moderator,
                                )
                                continue

    @tasks.loop(hours=24 * 7)
    async def check_not_introduced_user(self):
        for user in self.guild.members:
            if self.presentation_done_role in user.roles:
                continue
            if user.bot or not user.joined_at:
                continue

            message_to_send = None
            if user.joined_at < arrow.now().shift(weeks=-3).datetime:
                message_to_send = GOODBYE_MESSAGE
                await user.kick()
            elif user.joined_at < arrow.now().shift(weeks=-2).datetime:
                message_to_send = REMINDER_2_MESSAGE.format(
                    presentation_channel_mention=self.presentation_channel.mention,
                )
            elif user.joined_at < arrow.now().shift(weeks=-1).datetime:
                message_to_send = REMINDER_1_MESSAGE.format(
                    presentation_channel_mention=self.presentation_channel.mention,
                )

            if message_to_send and not SKIP_REMINDER_MESSAGE:
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
                except Exception:
                    continue

    # HACK: because on_message overwrite the command
    # but I saw afterwards that it was possible: https://stackoverflow.com/a/67465330
    # see here for commmand inside a Bot class: https://stackoverflow.com/a/67913136
    async def run_command(self, message: discord.Message):
        content_without_prefix = "".join(message.content.split(COMMAND_PREFIX)[1:])
        content_without_prefix_split = content_without_prefix.split(" ")
        command, content = (
            content_without_prefix_split[0],
            "".join(content_without_prefix_split[1:]),
        )

        match command.lower():
            case "tldr":
                start_message_id = get_message_id_from_link(link=content)
                counter = 0
                messages: list[str] = []
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
            case _:
                pass

    async def get_wanted_role_from_reaction(
        self,
        payload: discord.RawReactionActionEvent,
    ) -> discord.Role | None:
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
    ) -> discord.Message | None:
        channel = await self.guild.fetch_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        return await channel.fetch_message(payload.message_id)

    async def get_dm_message_from_reaction(
        self,
        payload: discord.RawReactionActionEvent,
    ) -> discord.Message | None:
        dm_channel = await self.fetch_channel(payload.channel_id)
        if not isinstance(dm_channel, discord.channel.DMChannel):
            return
        return await dm_channel.fetch_message(payload.message_id)

    async def get_member(self, user_id: int) -> discord.Member | None:
        try:
            return await self.guild.fetch_member(user_id)
        except discord.NotFound:
            return None

    def is_auto_thread_enabled(self, channel: discord.TextChannel) -> bool:
        if not channel.topic:
            return AUTO_THREAD_ENABLED_DEFAULT

        match = re.search(rf"{AUTO_THREAD_ENABLED_KEYWORD}:(\w+)", channel.topic)
        if match:
            auto_thread_enabled_str = match.group(1).lower()
            if auto_thread_enabled_str == "true":
                return True
            elif auto_thread_enabled_str == "false":
                return False

        return AUTO_THREAD_ENABLED_DEFAULT

    async def get_channel_moderator(
        self, channel: discord.TextChannel
    ) -> discord.Member | None:
        if not channel.topic:
            return None

        match = re.search(rf"{CHANNEL_MODERATOR_KEYWORD}:@(.+?)( |\n|$)", channel.topic)
        if match:
            moderator_username = match.group(1)
            channel_moderator = discord.utils.get(
                self.guild.members, name=moderator_username
            )
            return channel_moderator
        else:
            return None

    async def on_thread_create(self, thread: discord.Thread):
        if not isinstance(thread.parent, discord.TextChannel):
            return

        message = await thread.parent.fetch_message(thread.id)
        await message.add_reaction("👀")
        await thread.send(
            JOIN_THREAD_MENTIONS_PREFIX, silent=True, view=EditThreadButtonView()
        )

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member == self.user:
            return

        match payload.emoji.name:
            case "👀":
                if not payload.member:
                    return

                message = await self.get_message(payload=payload)

                if not message:
                    return

                if not isinstance(message.channel, discord.TextChannel):
                    return

                if message.author.bot:
                    return

                if not message.flags.has_thread:
                    return

                thread = message.channel.get_thread(message.id)
                if not thread:
                    return

                messages = [m async for m in thread.history(limit=3, oldest_first=True)]

                for message in messages:
                    if (
                        message.author == self.user
                        and JOIN_THREAD_MENTIONS_PREFIX in message.content
                    ):
                        if payload.member.mention in message.content:
                            break
                        mentions = message.content.replace(
                            JOIN_THREAD_MENTIONS_PREFIX, ""
                        ).split(JOIN_THREAD_MENTIONS_SEPARATOR)
                        mentions.append(payload.member.mention)
                        await message.edit(
                            content=JOIN_THREAD_MENTIONS_PREFIX
                            + JOIN_THREAD_MENTIONS_SEPARATOR.join(mentions)
                        )

            case "✅":
                if not payload.member:
                    return

                if payload.channel_id == self.roles_channel.id:
                    if role := await self.get_wanted_role_from_reaction(
                        payload=payload
                    ):
                        await payload.member.add_roles(role)

                elif payload.channel_id == self.rules_channel.id:
                    await payload.member.add_roles(self.rules_accepted_role)

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
                dm_message = await self.get_dm_message_from_reaction(payload=payload)

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

            case _:
                pass

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.member == self.user:
            return

        match payload.emoji.name:
            # NOTE: this remove the user's mention, but the user is still in the thread
            #       if the user is actually removed from the thread, a system message whould be sent
            case "👀":
                member = await self.get_member(user_id=payload.user_id)
                if not member:
                    return

                message = await self.get_message(payload=payload)

                if not message:
                    return

                if not isinstance(message.channel, discord.TextChannel):
                    return

                if message.author.bot:
                    return

                if not message.flags.has_thread:
                    return

                thread = message.channel.get_thread(message.id)
                if not thread:
                    return

                messages = [m async for m in thread.history(limit=3, oldest_first=True)]

                for message in messages:
                    if (
                        message.author == self.user
                        and JOIN_THREAD_MENTIONS_PREFIX in message.content
                    ):
                        if member.mention not in message.content:
                            break
                        mentions = message.content.replace(
                            JOIN_THREAD_MENTIONS_PREFIX, ""
                        ).split(JOIN_THREAD_MENTIONS_SEPARATOR)
                        mentions.remove(member.mention)
                        await message.edit(
                            content=JOIN_THREAD_MENTIONS_PREFIX
                            + JOIN_THREAD_MENTIONS_SEPARATOR.join(mentions)
                        )

            case "✅":
                if payload.channel_id == self.roles_channel.id:
                    role = await self.get_wanted_role_from_reaction(payload=payload)

                    if not role:
                        return

                    # There is not member in the payload on the reaction removal
                    member = await self.get_member(user_id=payload.user_id)
                    if not member:
                        return

                    await member.remove_roles(role)

            case _:
                pass

    async def on_message(self, message: discord.Message):
        async def try_create_thread(message: discord.Message):
            if message.author == self.user:
                return
            if message.type == discord.MessageType.reply:
                return
            if not isinstance(message.channel, discord.TextChannel):
                return
            if not self.is_auto_thread_enabled(channel=message.channel):
                return
            title = generate_title(text=message.content)
            await message.create_thread(
                name=f"{message.author.name}: {title}",
                auto_archive_duration=1440,  # 1440 min / 60 = 1 j
            )

        await try_create_thread(message=message)

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
                    rules_channel_mention=self.rules_channel.mention,
                )
            )
            await message.add_reaction("✅")
            return

        if (
            isinstance(message.author, discord.Member)
            and self.presentation_done_role not in message.author.roles
        ):
            await message.author.add_roles(self.presentation_done_role)
            await message.author.send(
                content=GRANTED_MESSAGE.format(
                    rules_channel_mention=self.rules_channel.mention,
                    roles_channel_mention=self.roles_channel.mention,
                    faq_channel_mention=self.faq_channel.mention,
                )
            )
            await message.add_reaction("🤝")
            return


def run_discord_client():
    client = ItkhoClient()
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run_discord_client()
