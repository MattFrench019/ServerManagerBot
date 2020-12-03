import discord

class Messages:
    @property
    def rules(self):
        embed = discord.Embed(
            title="Welcome to our Server", colour=discord.Colour(0x5e7a29),
            description="Our server is fairly relaxed, but we do have some basic rules.\nBefore you can proceed, please click on the reaction to agree to follow them.\nOnce you have clicked on the reaction, head to <#769233721281871873> to continue.",
            inline=False
        )
        embed.add_field(
            name="Rule 1",
            value="Racist/Homophobic/Transphobic language etc that goes beyond a joke will **not** be tolerated and **will** result with a temporary or permanent ban.",
            inline=False
        )
        embed.add_field(
            name="Rule 2",
            value="Any bullying or toxicity that goes beyond a joke is **not** acceptable, and will result in an instant ban.",
            inline=False
        )
        embed.add_field(
            name="Rule 3",
            value="NSFW content **must** be limited to NSFW channels, or it will be removed. This is to bring us inline with Discord's policy for large servers.",
            inline=False
        )
        embed.add_field(name="Cameron W.", value="Founder\n<@670988528594976801>", inline=True)
        embed.add_field(name="Matt F.", value="Co-Founder & Head Admin\n<@528575736270028800>", inline=True)
        return embed

    @property
    def select_group(self):
        embed = discord.Embed(title="Select Group", colour=discord.Colour(0xab38c7), description="In our server, we have serveral independent groups.\nClick on the reaction underneath the group you want to join to apply.\nYou should have a rough idea which one to join, but I'll go over them here.")



        """
        embed.add_field(name="Sidcot Y13", value="A collection of students from Y13, along with a few of our friends.")
        embed.add_field(name="Sidcot Y10", value="A group of students from Y10 at Sidcot along with some others.")
        embed.add_field(name="Sidcot Wing House", value="Discord group for students in Wing House.")
        """
        return embed

    @property
    def groups(self):
        return {
            719903094640738346: discord.Embed(title="Sidcot Y13", colour=discord.Colour(0xab38c7), description="A collection of students from Y13, along with a few of our friends."),
            719901525807333397: discord.Embed(title="Sidcot Y10", colour=discord.Colour(0xab38c7), description="A group of students from Y10 at Sidcot along with some others."),
            769281855455232030: discord.Embed(title="Sidcot Wing House", colour=discord.Colour(0xab38c7), description="Discord group for students in Wing House."),
        }







    @property
    def pending(self):
        embed = discord.Embed(title="Thank you for Applying", colour=discord.Colour(0xa02948), description="Our admissions team will now review your application before you are accepted into the server.\nThey may direct message you to ask for more information.")
        embed.add_field(name="Please be Patient", value="Sometimes, applications can take a while, but we have not forgotten them, so please cut our admissions team a bit of slack.", inline=False)
        embed.add_field(name="Cameron W.", value="Founder\n<@670988528594976801>", inline=True)
        embed.add_field(name="Matt F.", value="Co-Founder & Head Admin\n<@528575736270028800>", inline=True)
        return embed

    @property
    def games(self):
        embed = discord.Embed(title="Select Games", colour=discord.Colour(0xa02948), description="Here you can select game roles to be added to your profile.\nThis allows you to be pinged when someone @s that role.")
        return embed


messages = Messages()
