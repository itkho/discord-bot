import os
from typing import Optional

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_NAME = os.getenv("GUILD_NAME")

PRESENTATION_CHANNEL_NAME = "presentation"
MEMBER_ROLE_NAME = "member"


class CustomClient(discord.Client):
    @property
    def guild(self) -> Optional[discord.Guild]:
        if not hasattr(self, "_guild"):
            guilds = [g for g in client.guilds if g.name.lower() == GUILD_NAME.lower()]
            if len(guilds) != 1:
                raise ValueError(f"There must be one and only one {GUILD_NAME} guild.")
            self._guild = guilds[0]
        return self._guild

    @property
    def member_role(self) -> Optional[discord.Role]:
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

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")
        print(f"Guilds: {self.guild}")
        print(f"Member Role: {self.member_role}")

    async def send_marhaban_message(
        self, channel: discord.TextChannel, to: discord.User
    ):
        await channel.send(f"Marhaban {to.mention} 👋")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.channel.name != PRESENTATION_CHANNEL_NAME:
            return

        if message.type == discord.MessageType.new_member:
            await self.send_marhaban_message(channel=message.channel, to=message.author)
            return

        if self.member_role not in message.author.roles:
            await message.author.add_roles(self.member_role)
            await message.channel.send("ACCESS GRANTED! 🎉")
            return


intents = discord.Intents.default()
intents.message_content = True
client = CustomClient(intents=intents)
client.run(TOKEN)
