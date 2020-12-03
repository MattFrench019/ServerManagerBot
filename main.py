import discord
from messages import messages as messages
import config
from typing import *


def is_me(m):
    return m.author == client.user


class Bot(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)

        self.server: discord.Guild or None = None

        self.games_msg_id = None
        self.setting_up = False
        self.emoji_to_game = {}


    ###################
    #### Utilities ####
    ###################

    async def log(self, value):
        channel: discord.TextChannel = self.server.get_channel(config.channels.log)
        print(value)
        await channel.send(value)

    async def add_reaction_by_name(self, msg, emoji_name):
        await msg.add_reaction(next((x for x in await self.server.fetch_emojis() if x.name == emoji_name), None))

    async def add_reaction_by_id(self, msg, emoji_id):
        await msg.add_reaction(next((x for x in await self.server.fetch_emojis() if x.id == emoji_id), None))

    async def delete_all_msgs(self, channel):
        async for msg in channel.history():
            await msg.delete()

    async def startup(self):
        self.setting_up = True

        await self.check_admissions_reactions()
        await self.setup_games_msg()

        self.setting_up = False

    async def check_admissions_reactions(self):
        channel: discord.TextChannel = self.server.get_channel(config.channels.admissions)

        msgs = channel.history()

        async for msg in msgs:
            if msg.author == self.user:
                await self.handle_admissions_msg_reaction(msg)

    ##################
    #### Messages ####
    ##################

    async def setup_games_msg(self):
        await self.log("Generating role look-up table...")

        channel: discord.TextChannel = self.server.get_channel(config.channels.game_def)
        msgs = channel.history()

        async for msg in msgs:
            self.emoji_to_game[msg.reactions[0].emoji.id] = int(msg.content)

        await self.log("Generated role look-up table...")

        ### Games Message ###

        channel: discord.TextChannel = self.server.get_channel(config.channels.game_select)

        # Check for message
        valid_msg = True
        msgs = []
        async for msg in channel.history():
            msgs.append(msg)
            if msg.author != self.server.me:
                await msg.delete()

            if len(msgs) > 1:
                await self.log("More than 1 games msg, please remove least important one...")
                exit()

        if valid_msg:
            msg: discord.Message = msgs[0]
            self.games_msg_id = msg.id

            # TODO Potential Source of Error
            # TODO Figure out what I meant

            for emoji_id in self.emoji_to_game.keys():
                print()
                await self.add_reaction_by_id(msg, emoji_id)

        elif not valid_msg:
            await self.log("Creating game message...")

            msg = await channel.send(embed=messages.games)
            self.games_msg_id = msg.id

            for emoji_id in self.emoji_to_game.keys():
                await self.add_reaction_by_id(msg, emoji_id)

            await self.log("Created game message...")

        else:
            await self.log("Somehow `valid_msg` was neither true or false?")
            exit()

        await self.log("Generating role list...")

        correct_roles = {}

        for user in self.server.members:
            if not user.bot:
                correct_roles[user.id] = [self.server.get_role(config.roles.game_label)]

        for reaction in msg.reactions:
            async for user in reaction.users():
                if not user.bot:
                    roles = correct_roles.get(user.id)
                    if roles is None:
                        print(f"Couldnt find {user.display_name} for role list")
                        continue
                    roles.append(self.server.get_role(self.emoji_to_game[reaction.emoji.id]))
                    correct_roles[user.id] = roles

        await self.log("Generated role list...")
        await self.log("Implementing role list...")

        game_roles = [self.server.get_role(x) for x in self.emoji_to_game.values()]

        for user_id, roles in correct_roles.items():
            print(self.server.get_member(user_id).name)
            user: discord.Member = self.server.get_member(user_id)

            await user.remove_roles(*game_roles)
            await user.add_roles(*roles)

        await self.log("Implemented role list...")

    async def send_application_msg(self, role_id, user):
        channel: discord.TextChannel = self.server.get_channel(config.channels.admissions)
        msg = await channel.send(f"<@{user.id}> is wanting to join **{self.server.get_role(role_id).name}**\n{role_id}")

        for emoji_name in ["✅", "❎", "⛔"]:
            await msg.add_reaction(emoji_name)

    async def send_rules_msg(self, user: discord.User or discord.Member):
        await self.log(f"Sending join msg to {user.display_name}")
        msg = await user.send(embed=messages.rules)
        await msg.add_reaction('☑')

    async def send_select_msg(self, user: discord.User or discord.Member):
        await self.log(f"Sending select msg to {user.display_name}")
        await user.send(embed=messages.select_group)

        for role, embed in messages.groups.items():
            msg = await user.send(embed=embed)
            await msg.add_reaction('☑')

    async def send_pending_msg(self, user: discord.User or discord.Member):
        await self.log(f"Sending pending msg to {user.display_name}")
        await user.send(embed=messages.pending, delete_after=30)

    async def send_accepted_msg(self, user: discord.User or discord.Member):
        pass


    ########################
    #### Event Handlers ####
    ########################

    async def on_ready(self, *args):
        print("Ready")

        self.server = client.get_guild(config.server)
        await self.log("Starting...")

        await self.startup()

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        user = self.get_user(payload.user_id)
        channel: discord.TextChannel = self.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        if not user.bot:
            if msg.author == client.user:
                if isinstance(channel, discord.abc.PrivateChannel):
                    member: discord.Member = self.server.get_member(user.id)

                    if msg.embeds[0].title == messages.rules.title:
                        await self.send_select_msg(user)
                        await msg.delete()

                    for role, embed in messages.groups.items():
                        if msg.embeds[0].title == embed.title:
                            await self.delete_all_msgs(channel)
                            await self.send_pending_msg(user)
                            await self.send_application_msg(role, user)


                if msg.id == self.games_msg_id:
                    await self.log(f"Adding role {self.server.get_role(self.emoji_to_game[payload.emoji.id])} to {user.name}")
                    await user.add_roles(self.server.get_role(self.emoji_to_game[payload.emoji.id]))

                # Catch admissions reactions
                elif channel == self.server.get_channel(config.channels.admissions):
                    await self.handle_admissions_msg_reaction(msg)


    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        user = self.server.get_member(payload.user_id)
        channel: discord.TextChannel = self.server.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        if not user.bot:
            if msg.author == client.user:
                if msg.id == self.games_msg_id:
                    await user.remove_roles(self.server.get_role(self.emoji_to_game[payload.emoji.id]))


    async def on_message(self, msg: discord.Message):
        if not self.setting_up:
            if not msg.author.bot:
                if msg.channel.id == config.channels.control:
                    if msg.content == config.reset_cmd:
                        await self.startup()


    async def on_member_join(self, member: discord.Member):
        await self.send_rules_msg(member)

    async def on_disconnect(self):
        pass

    async def handle_admissions_msg_reaction(self, msg):
        try:
            reactions: List[discord.Reaction] = msg.reactions

            reactions = [x for x in reactions]

            if len(await reactions[0].users().flatten()) > 1:
                user_to_move: discord.Member = msg.mentions[0]
                role = int(msg.content.split("\n")[-1])
                await user_to_move.add_roles(self.server.get_role(role))  # Add correct role
                await user_to_move.add_roles(self.server.get_role(config.roles.member))  # Add member role
                await msg.delete()

            elif len(await reactions[1].users().flatten()) > 1:
                user_to_move: discord.Member = msg.mentions[0]
                await user_to_move.kick(reason="You were denied by the admissions team")
                await msg.delete()

            elif len(await reactions[2].users().flatten()) > 1:
                user_to_move: discord.Member = msg.mentions[0]
                await user_to_move.ban(reason="You were denied by the admissions team")
                await msg.delete()

        except Exception as e:
            print(e)


if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.members = True
    intents.messages = True
    intents.reactions = True
    client = Bot(intents=intents)

    client.run("")
