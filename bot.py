import discord
from dotenv import load_dotenv

from consts import (
    DISCORD_TOKEN,
    GRANTED_MESSAGE,
    GUILD_NAME,
    MARHABAN_MESSAGE,
    MEMBER_ROLE_NAME,
    PRESENTATION_CHANNEL_NAME,
)

load_dotenv()


class CustomClient(discord.Client):
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

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.channel != self.presentation_channel:
            return

        # I should have been use "on_member_join" but it doesn't work.
        # The event doesn't fire (maybe because of wrong roles/permissions)
        if message.type == discord.MessageType.new_member:
            await message.author.send(
                MARHABAN_MESSAGE.format(
                    user_mention=message.author.mention,
                    channel_mention=self.presentation_channel.mention,
                )
            )
            return

        if (
            isinstance(message.author, discord.Member)
            and self.member_role not in message.author.roles
        ):
            await message.author.add_roles(self.member_role)
            await message.author.send(GRANTED_MESSAGE)
            return


def run_disord_client():
    intents = discord.Intents.default()
    intents.message_content = True
    client = CustomClient(intents=intents)
    client.run(DISCORD_TOKEN)
