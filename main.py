import discord
import config
from typing import *


def is_me(m):
    return m.author == client.user


class Bot(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)

        self.server: discord.Guild = None

        self.rules_msg_id = None
        self.select_msg_id = None
        self.pending_msg_id = None
        self.games_msg_id = None

        self.setting_up = False

        self.emoji_to_game = {}

    async def log(self, value):
        channel: discord.TextChannel = self.server.get_channel(config.channels.log)
        print(value)
        await channel.send(value)

    async def add_reaction_by_name(self, msg, emoji_name):
        await msg.add_reaction(next((x for x in await self.server.fetch_emojis() if x.name == emoji_name), None))

    async def add_reaction_by_id(self, msg, emoji_id):
        await msg.add_reaction(next((x for x in await self.server.fetch_emojis() if x.id == emoji_id), None))

    async def check_for_msg(self, channel, reactions_len):
        # Check for message
        valid_msg = True
        msgs = []
        async for msg in channel.history():
            msgs.append(msg)
            if msg.author != self.server.me:
                await msg.delete()
                continue

            elif len(msgs) > 1 or len(msg.reactions) != reactions_len:
                valid_msg = False
                break

        return valid_msg, msgs

    async def delete_all_msgs(self, channel):
        async for msg in channel.history():
            await msg.delete()

    async def setup_rules_msg(self):
        await self.log("Setting up the rules message...")

        channel: discord.TextChannel = self.server.get_channel(config.channels.rules)

        valid_msg, msgs = await self.check_for_msg(channel, 1)

        if valid_msg:
            await self.log("Resetting the rules message...")

            msg: discord.Message = msgs[0]
            self.rules_msg_id = msg.id

            async for user in msg.reactions[0].users():
                if user != self.user:
                    try:
                        if len(user.roles) == 1:
                            await self.move_user_to_select(user)
                    except AttributeError:
                        pass

            await msg.clear_reactions()
            await self.add_reaction_by_name(msg, config.emojis.rules_tick)

            await self.log("Reset the rules message...")

        elif not valid_msg:
            await self.log("Could not find rules message, creating message...")

            await self.delete_all_msgs(channel)

            embed = discord.Embed(title="Welcome to our Server", colour=discord.Colour(0x5e7a29), description="Our server is fairly relaxed, but we do have some basic rules.\nBefore you can proceed, please click on the reaction to agree to follow them.\nOnce you have clicked on the reaction, head to <#769233721281871873> to continue.", inline=False)
            embed.add_field(name="Rule 1", value="Racist/Homophobic/Transphobic language etc that goes beyond a joke will **not** be tolerated and **will** result with a temporary or permanent ban.", inline=False)
            embed.add_field(name="Rule 2", value="Any bullying or toxicity that goes beyond a joke is **not** acceptable, and will result in an instant ban.", inline=False)
            embed.add_field(name="Rule 3", value="NSFW content **must** be limited to NSFW channels, or it will be removed. This is to bring us inline with Discord's policy for large servers.", inline=False)
            embed.add_field(name="Cameron W.", value="Founder\n<@670988528594976801>", inline=True)
            embed.add_field(name="Matt F.", value="Co-Founder & Head Admin\n<@528575736270028800>", inline=True)

            msg = await channel.send(embed=embed)
            await self.add_reaction_by_name(msg, config.emojis.rules_tick)

            self.rules_msg_id = msg.id

            await self.log("Created new rules message...")

        await self.log("Finished setting up rules message...")

    async def setup_select_msg(self):
        await self.log("Setting up the selection message...")

        channel: discord.TextChannel = self.server.get_channel(config.channels.select)

        valid_msg, msgs = await self.check_for_msg(channel, config.groups_len)

        if valid_msg:
            await self.log("Resetting the selection message...")

            msg: discord.Message = msgs[0]
            self.select_msg_id = msg.id

            for reaction in msg.reactions:
                users = await reaction.users().flatten()
                if len(users) > 1:
                    for user in users:
                        if user != self.user:
                            await self.move_user_to_pending(reaction.emoji, user)

            await msg.clear_reactions()

            for emoji in [config.emojis.y13, config.emojis.y10, config.emojis.wing]:
                await self.add_reaction_by_name(msg, emoji)

            await self.log("Reset the selection message...")

        elif not valid_msg:
            await self.log("Could not find selection message, creating message...")

            await self.delete_all_msgs(channel)

            embed = discord.Embed(title="Select Group", colour=discord.Colour(0xab38c7), description="In our server, we have serveral independent groups.\nClick on the reactions underneath to apply to a group.\nYou should have a rough idea which one to join, but I'll go over them here.\nOnce you have clicked on the reaction, head to <#769236016669392957> to continue.")
            embed.add_field(name="Sidcot Y13", value="A collection of students from Y13, along with a few of our friends.")
            embed.add_field(name="Sidcot Y10", value="A group of students from Y10 at Sidcot along with some others.")
            embed.add_field(name="Sidcot Wing House", value="Discord group for students in Wing House.")

            msg = await channel.send(embed=embed)

            for emoji in [config.emojis.y13, config.emojis.y10, config.emojis.wing]:
                await self.add_reaction_by_name(msg, emoji)

            self.select_msg_id = msg.id

            await self.log("Created new selection message...")

        await self.log("Finished setting up selection message...")

    async def setup_pending_msg(self):
        await self.log("Setting up the pending message...")

        channel: discord.TextChannel = self.server.get_channel(config.channels.pending)

        valid_msg, msgs = await self.check_for_msg(channel, 0)

        if valid_msg:
            await self.log("Resetting pending message...")

            msg: discord.Message = msgs[0]
            self.pending_msg_id = msg.id

            await self.log("Reset pending message...")

        elif not valid_msg:
            await self.log("Could not find pending message, creating message...")

            await self.delete_all_msgs(channel)

            embed = discord.Embed(title="Thank you for Applying", colour=discord.Colour(0xa02948), description="Our admissions team will now review your application before you are accepted into the server.\nThey may direct message you to ask for more information.")
            embed.add_field(name="Please be Patient", value="Sometimes, applications can take a while, but we have not forgotten them, so please cut our admissions team a bit of slack.", inline=False)
            embed.add_field(name="Cameron W.", value="Founder\n<@670988528594976801>", inline=True)
            embed.add_field(name="Matt F.", value="Co-Founder & Head Admin\n<@528575736270028800>", inline=True)

            msg = await channel.send(embed=embed)

            self.pending_msg_id = msg.id

            await self.log("Created new pending message...")

        await self.log("Finished setting up pending message...")

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

            for emoji_id in self.emoji_to_game.keys():
                print()
                await self.add_reaction_by_id(msg, emoji_id)

        elif not valid_msg:
            await self.log("Creating game message...")

            embed = discord.Embed(title="Select Games", colour=discord.Colour(0xa02948), description="Here you can select game roles to be added to your profile.\nThis allows you to be pinged when someone @s that role.")
            msg = await channel.send(embed=embed)
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
                    roles.append(self.server.get_role(self.emoji_to_game[reaction.emoji.id]))
                    correct_roles[user.id] = roles

        await self.log("Generated role list...")
        await self.log("Implementing role list...")

        for user_id, roles in correct_roles.items():
            print(self.server.get_member(user_id).name)
            user: discord.Member = self.server.get_member(user_id)
            for emoji_id, role_id in self.emoji_to_game.items():
                await user.remove_roles(self.server.get_role(role_id))

            for role in roles:
                await user.add_roles(self.server.get_role(role.id))

        await self.log("Implemented role list...")

    async def check_admissions_message(self, msg):
        try:
            reactions: List[discord.Reaction] = msg.reactions

            reactions = [x for x in reactions]

            if len(await reactions[0].users().flatten()) > 1:
                user_to_move: discord.Member = msg.mentions[0]
                role = int(msg.content.split("\n")[-1])
                await user_to_move.add_roles(self.server.get_role(role))  # Add correct role
                await user_to_move.add_roles(self.server.get_role(config.roles.member))  # Add member role
                await user_to_move.remove_roles(self.server.get_role(config.roles.on_select_click_add))  # Remove pending role
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

    async def check_admissions(self):
        channel: discord.TextChannel = self.server.get_channel(config.channels.admissions)

        msgs = channel.history()

        async for msg in msgs:
            if msg.author == self.user:
                await self.check_admissions_message(msg)

    async def move_user_to_select(self, user):
        try:
            await user.add_roles(self.server.get_role(config.roles.on_rules_click_add))
        except AttributeError:
            print("User has left")

    async def move_user_to_pending(self, emoji, user):
        try:
            await user.add_roles(self.server.get_role(config.roles.on_select_click_add))
            await user.remove_roles(self.server.get_role(config.roles.on_select_click_rem))

            await self.send_application_msg(emoji, user)

        except AttributeError:
            print("User has left")

    async def on_ready(self, *args):
        print("Ready")

        self.server = client.get_guild(config.server)
        await self.log("Starting...")

        await self.startup()

    async def startup(self):
        self.setting_up = True
        await self.setup_rules_msg()

        await self.check_admissions()

        await self.setup_select_msg()
        await self.setup_pending_msg()
        await self.setup_games_msg()

        self.setting_up = False

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        print("reaction")

        user = self.server.get_member(payload.user_id)
        channel: discord.TextChannel = self.server.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        if not user.bot:
            if msg.author == client.user:
                if msg.id == self.rules_msg_id:
                    await self.move_user_to_select(user)

                elif msg.id == self.select_msg_id:
                    if next((x for x in user.roles if x.id == config.roles.on_rules_click_add), None):
                        await self.move_user_to_pending(payload.emoji, user)

                elif msg.id == self.games_msg_id:
                    print(f"Adding role {self.server.get_role(self.emoji_to_game[payload.emoji.id])} to {user.name}")
                    await user.add_roles(self.server.get_role(self.emoji_to_game[payload.emoji.id]))

                # Catch admissions reactions
                elif channel == self.server.get_channel(config.channels.admissions):
                    print("admissions")
                    await self.check_admissions_message(msg)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        print("reaction remove")

        user = self.server.get_member(payload.user_id)
        channel: discord.TextChannel = self.server.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        if not user.bot:
            if msg.author == client.user:
                if msg.id == self.games_msg_id:
                    await user.remove_roles(self.server.get_role(self.emoji_to_game[payload.emoji.id]))

    async def on_message(self, msg: discord.Message):
        if not self.setting_up:
            print("msg sent")

            if not msg.author.bot:
                if msg.channel.id == config.channels.control:
                    if msg.content == config.reset_cmd:
                        await self.startup()

    async def send_application_msg(self, emoji, user):
        channel: discord.TextChannel = self.server.get_channel(config.channels.admissions)
        msg = await channel.send(f"<@{user.id}> is wanting to join {config.emojis_to_group[emoji.name]}\n{config.emojis_to_roles[emoji.name]}")

        for emoji in [config.emojis.user_tick, config.emojis.user_cross, config.emojis.user_ban]:
            await self.add_reaction_by_name(msg, emoji.name)


if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.members = True
    intents.messages = True
    intents.reactions = True
    client = Bot(intents=intents)

    client.run("")