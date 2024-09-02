# DOCUMENTATION
# https://pypi.org/project/ro-py/
# https://ro.py.jmksite.dev/index.html
# https://devforum.roblox.com/t/use-python-to-interact-with-the-roblox-api-with-ropy/1006465
# https://discordpy.readthedocs.io/en/latest/api.html

import discord
from ro_py import Client
from discord.ext import commands
from discord_components import *
import tracemalloc
import time

from commands.admin.addpoints import aAddPoints
from commands.admin.forcebind import aForcebind
from commands.admin.close import aClose
from commands.admin.add import aAdd
from commands.admin.rate import aRate
from commands.general.ping import gPing
from commands.general.bind import gBind
from commands.general.affiliate import gAffiliate
from commands.general.positions import gPositions
from commands.general.mainCOM import gMain
from commands.general.rep import gRep
from commands.general.top import gTop
from commands.general.count import gCount
from commands.general.open import gOpen
from commands.general.profile import gProfile
from commands.staff.assignposition import sAssignPosition
from commands.staff.fairzone import sFairzone
from commands.staff.fort import sFort
from commands.staff.scrimmage import sScrimmage
from commands.staff.submit import sSubmit
from commands.staff.review import sReview

from events.on_reaction import eReaction

tracemalloc.start()

roToken = "TOKEN HERE"
roClient = Client(roToken)

status = "rr!help"
prefix = "rr!"
intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
discordClient = commands.Bot(command_prefix=prefix, intents=intents)
discordClient.remove_command("help")


@discordClient.command()
async def help(ctx):
    def buttonCheck(b):
        return b.channel == ctx.message.channel

    buttonEmbed = discord.Embed(
        title="RequestBOT Help",
        description="What commands would you like to see?",
        color=0,
    )
    components = [
        Button(style=ButtonStyle.blue, label="General", custom_id="general"),
        Button(style=ButtonStyle.red, label="High Ranks", custom_id="hicom"),
        Button(style=ButtonStyle.green, label="Admin", custom_id="admin")
    ]

    msg = await ctx.send(embed=buttonEmbed, components=[components])

    helpEmbed = discord.Embed(
        title="RequestBOT Help",
        color=0
    )

    buttonClicked = False
    res = await discordClient.wait_for("button_click", check=buttonCheck)
    if res.component.custom_id == "admin":
        if buttonClicked:
            return
        buttonClicked = True

        await msg.delete()

        helpEmbed.add_field(name="**Admin Category**", value="These commands can only be used by Admins.", inline=False)
        helpEmbed.add_field(name=":100: **| addpoints**  - ``rr!addpoints <group id> <amount>``",
                            value="Add points to a group.", inline=False)
        helpEmbed.add_field(name=":closed_lock_with_key: **| close** - ``rr!close``", value="Close a ticket.",
                            inline=False)
        helpEmbed.add_field(name=":zap: **| forcebind** - ``rr!forcebind <@user> <user roblox id>``",
                            value="Force bind a user.", inline=False)

        await ctx.send(embed=helpEmbed)
    elif res.component.custom_id == "general":
        if buttonClicked:
            return
        buttonClicked = True

        await msg.delete()

        helpEmbed.add_field(name="**General Category**", value="These commands are always available for use.",
                            inline=False)
        helpEmbed.add_field(name=":handshake: **| affiliate** - ``rr!affiliate <group id>``",
                            value="Submit an affiliation request for a group you own.", inline=False)
        helpEmbed.add_field(name=":lock_with_ink_pen: **| bind** - ``rr!bind``",
                            value="Adds the user to the database if already doesn't exist.", inline=False)
        helpEmbed.add_field(name=":1234: **| count** - ``rr!count <group id>``",
                            value="Showcases the amount of people who represent and the amount of people who main a group.",
                            inline=False)
        helpEmbed.add_field(name=":bookmark_tabs: **| help** - ``rr!help``", value="Returns the bot's commands.",
                            inline=False)
        helpEmbed.add_field(name=":lock: **| main** - ``rr!main <group id>``", value="Main an affiliated group.",
                            inline=False)
        helpEmbed.add_field(name=":information_source: **| open** - ``rr!open [forts or fairzones]``",
                            value="Showcases 20 forts and fairzones of available groups.", inline=False)
        helpEmbed.add_field(name=":ping_pong: **| ping** - ``rr!ping``",
                            value="Returns the bot's latency to the discord api.", inline=False)
        helpEmbed.add_field(name=":bar_chart: **| positions** - ``rr!positions <group id>``",
                            value="Show's the positions of the members in the group specified.", inline=False)
        helpEmbed.add_field(name=":briefcase: **| profile** - ``rr!profile <@user> or <group id>``",
                            value="View the profile of an affiliated group / user.", inline=False)
        helpEmbed.add_field(name=":pencil: **| rep** - ``rr!rep <group id>``", value="Represent an affiliated group.",
                            inline=False)
        helpEmbed.add_field(name=":chart_with_upwards_trend: **| top** - ``rr!top``",
                            value="Showcases the top groups in the server with the most points.", inline=False)

        await ctx.send(embed=helpEmbed)
    elif res.component.custom_id == "hicom":
        if buttonClicked:
            return
        buttonClicked = True

        await msg.delete()

        helpEmbed.add_field(name="**Group Higher Ranks Category**",
                            value="These commands can only be used by High Ranks.", inline=False)
        helpEmbed.add_field(
            name=":bookmark: **| assignposition** - ``rr!assignposition <group id> <@user or userid> <rank number>``",
            value="Assign a user a position in the specified group.", inline=False)
        helpEmbed.add_field(name=":flag_white: **| fairzone** - ``rr!fairzone <game link> <notes>``",
                            value="Explicitly for use within the #battle-request channel. Pings users with the ``@Fairzone Request`` role.", inline=False)
        helpEmbed.add_field(name=":flag_black: **| fort** - ``rr!fort <game link> <notes>``", value="Explicitly for use within the #battle-request channel. Pings users with the ``@Raid Request`` role.",
                            inline=False)
        helpEmbed.add_field(name=":book: **| review** - ``rr!review <your clan group id> <reviewing clan group id>``",
                            value="Review an event which has happened between your group and another.", inline=False)
        helpEmbed.add_field(name=":crossed_swords: **| scrimmage** - ``rr!scrimmage <game link> <notes>``",
                            value="Explicitly for use within the #battle-request channel. Pings users with the ``@Scrimmage Request`` role.", inline=False)
        helpEmbed.add_field(name=":writing_hand: **| upload** - ``rr!upload <group id>``",
                            value="Submit a base which your division / war clan group owns or update one you have already submitted.",
                            inline=False)

        await ctx.send(embed=helpEmbed)


@discordClient.event
async def on_ready():
    await discordClient.change_presence(status=discord.Status.online, activity=discord.Game(status))
    DiscordComponents(discordClient)
    print("Bot is ready")


@discordClient.event
async def on_raw_reaction_add(payload):
    await eReaction(payload=payload, discordClient=discordClient)


@discordClient.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg2 = await ctx.send("There is still a delay in place. Please try again in a few minutes after the 10 minute delay.")
        time.sleep(5)
        await ctx.message.delete()
        await msg2.delete()


@discordClient.command()
async def ping(ctx):
    await gPing(ctx=ctx, latency=discordClient.latency)


@discordClient.command()
async def bind(ctx):
    await gBind(ctx=ctx, client=roClient)


@discordClient.command()
async def addpoints(ctx, *args):
    if len(args) < 3:
        await ctx.send("Please use the following format: ``rr!addpoints (group_id) (amount) (reason)``")
        return
    gid = args[0]
    amt = args[1]
    await aAddPoints(ctx=ctx, group_id=gid, amount=amt, discordClient=discordClient, roClient=roClient)


affiliateRunners = []
@discordClient.command()
async def affiliate(ctx, *args):
    if len(args) == 0:
        await ctx.send("Please include a valid Group ID to affiliate ``rr!affiliate <Group Id>``")
        return
    gid = args[0]
    for runner in affiliateRunners:
        if runner == ctx.message.author.id:
            await ctx.send("You are already running this command.")
            return
    affiliateRunners.insert(len(affiliateRunners), ctx.message.author.id)
    oldRunner = await gAffiliate(ctx=ctx, group_id=gid, discordClient=discordClient, roClient=roClient)
    affiliateRunners.remove(oldRunner)


@discordClient.command()
async def forcebind(ctx, mention, robloxID):
    await aForcebind(ctx=ctx, client=roClient, userid=robloxID)


@discordClient.command()
async def positions(ctx, gid):
    await gPositions(ctx=ctx, group_id=gid, client=roClient)  # CHECK ERRORS START HERE 10/19/2021


@discordClient.command()
async def assignposition(ctx, gid, user, rank):
    await sAssignPosition(ctx=ctx, gid=gid, user=user, rank=rank, roClient=roClient, discordClient=discordClient)


@discordClient.command()
async def main(ctx, gid):
    await gMain(ctx=ctx, group_id=gid, roClient=roClient)


@discordClient.command()
async def rep(ctx, gid):
    await gRep(ctx=ctx, group_id=gid, roClient=roClient)


@discordClient.command()
async def top(ctx):
    await gTop(ctx=ctx, roClient=roClient)


@discordClient.command()
async def count(ctx, gid):
    await gCount(ctx=ctx, group_id=gid, roClient=roClient)


@discordClient.command()
@commands.cooldown(1, 600, commands.BucketType.user)
async def fairzone(ctx, *args):
    link = None
    msg = None
    try:
        link = args[0]
    except:
        msg = await ctx.send("Please provide a game link.")
    if not link:
        fairzone.reset_cooldown(ctx)
        time.sleep(5)
        await msg.delete()
        await ctx.message.delete()
        return
    await sFairzone(ctx=ctx, link=link, discordClient=discordClient, command=fairzone)


@discordClient.command()
@commands.cooldown(1, 600, commands.BucketType.user)
async def fort(ctx, *args):
    link = None
    msg = None
    try:
        link = args[0]
    except:
        msg = await ctx.send("Please provide a game link.")
    if not link:
        fairzone.reset_cooldown(ctx)
        time.sleep(5)
        await msg.delete()
        await ctx.message.delete()
        return
    await sFort(ctx=ctx, link=link, discordClient=discordClient, command=fort)


@discordClient.command()
@commands.cooldown(1, 600, commands.BucketType.user)
async def scrimmage(ctx, *args):
    link = None
    msg = None
    try:
        link = args[0]
    except:
        msg = await ctx.send("Please provide a game link.")
    if not link:
        fairzone.reset_cooldown(ctx)
        time.sleep(5)
        await msg.delete()
        await ctx.message.delete()
        return
    await sScrimmage(ctx=ctx, link=link, discordClient=discordClient, command=scrimmage)


@discordClient.command()
async def upload(ctx, gid):
    await sSubmit(ctx=ctx, gid=gid, discordClient=discordClient, roClient=roClient)


@discordClient.group(invoke_without_command=True)
async def open(ctx):
    await gOpen(ctx=ctx, type="void", roClient=roClient)


@open.command()
async def forts(ctx):
    await gOpen(ctx=ctx, type="forts", roClient=roClient)


@open.command()
async def fairzones(ctx):
    await gOpen(ctx=ctx, type="fairzones", roClient=roClient)


@discordClient.command()
async def profile(ctx):
    await gProfile(ctx=ctx, roClient=roClient)


reviewRunners = []
@discordClient.command()
async def review(ctx, *args):
    if len(args) < 2:
        await ctx.send(f"{ctx.message.author.mention} Please  state the group you're representing and the group you wish to review ``rr!review <Group Id> <Group Id>``.")
        return
    gid1 = args[0]
    gid2 = args[1]
    for runner in reviewRunners:
        if runner == ctx.message.author.id:
            await ctx.send("You are already running this command.")
            return
    reviewRunners.insert(len(reviewRunners), ctx.message.author.id)
    oldRunner = await sReview(ctx=ctx, gid1=gid1, gid2=gid2, roClient=roClient, discordClient=discordClient)
    reviewRunners.remove(oldRunner)


@discordClient.command()
async def close(ctx):
    await aClose(ctx=ctx, discordClient=discordClient)


@discordClient.command()
async def add(ctx):
    await aAdd(ctx=ctx)


@discordClient.command()
async def rate(ctx, *args):
    await aRate(ctx, args)

discordClient.run("TOKEN GOES HERE")
