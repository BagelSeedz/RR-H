import discord
from discord_components import *
import sqlite3

modChannelId = 896968970161258588
automationRole = 906749972999966741
actionLogChannel = 910022427046731817


async def gAffiliate(ctx, group_id, discordClient, roClient):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    oldPoints = 0
    oldRepCount = 0
    oldScore = 10.0
    oldReputationCount = 0

    userFound = False
    for row in cursor.execute('SELECT * FROM users ORDER BY userid'):
        if row[1] == str(ctx.message.author.id):
            userFound = True
            break
    if not userFound:
        errorEmbed = discord.Embed(
            title=":x: **ERROR**",
            description="You do not have a profile yet. Please set one up to use this command! ```rr!bind```",
            color=16711680
        )
        await ctx.send(embed=errorEmbed)
        return ctx.message.author.id
    elif userFound:
        rowGroup = None
        for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
            if row[0] == group_id:
                rowGroup = row
                break
        if rowGroup:
            if rowGroup[11] == "no":
                oldPoints = rowGroup[7]
                oldRepCount = rowGroup[8]
                oldScore = rowGroup[9]
                oldReputationCount = rowGroup[10]
                cursor.execute(f"DELETE FROM groups WHERE groupid = {group_id}")
                db.commit()
            else:
                await ctx.send("This group is already affiliated!")
                return ctx.message.author.id

    def addToDatabase(group, leaders, hicom, officials, members, type, mainGroup):
        cursor.execute("INSERT INTO groups VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (str(group), str(leaders), str(hicom), str(officials), str(members), str(type), str(mainGroup), oldPoints, oldRepCount, oldScore, oldReputationCount, "yes"))
        db.commit()


    await ctx.send("Check your dms! (If you did not get one, please enable \"Allow direct messages from server members\" in your Privacy and Safety settings)")
    channel = await ctx.message.author.create_dm()

    def buttonCheck(b):
        return b.channel == channel

    clanID = group_id
    clanType = None
    rank = None
    leader = None
    reason = None
    hicom = [None]
    officials = [None]
    members = [None]

    affiliationPrompt = discord.Embed(
        title="**RR:H - AFFILIATION PROMPT**",
        description="Affiliating with Raid Request: HUB allows raiding squads to find events in a quick and much more "
                    "safe manner.\n\nBy affiliating, you get your own profile, and are allowed to send and receive "
                    "reviews which will make clans who host with integrity to receive recognition for doing so.\n\nIf "
                    "you own a clan, division or raiding squad with a roblox group, and wish to affiliate, "
                    "follow the steps below. **RR:H is currently limited to sword-fighting clans only.** ",
        color=16776960
    )
    affiliationPrompt.set_footer(text="Once read and agreed to the above, click Continue.")
    affiliationPrompt.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
    msg = await channel.send(embed=affiliationPrompt, components=[
        Button(style=ButtonStyle.gray, label="Continue")
    ])

    res = await discordClient.wait_for("button_click", check=buttonCheck)
    if res.channel == channel and res.component.style == ButtonStyle.gray:
        await msg.edit(embed=affiliationPrompt, components=[])

        categoryEmbed = discord.Embed(
            title="**RR:H - AFFILIATION PROMPT**",
            description="What is the primary category of your team? (Please type 'War Clan' or 'Division)",
            color=16776960
        )
        categoryEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        components = [
            Button(style=ButtonStyle.red, label="War Clan", custom_id="war"),
            Button(style=ButtonStyle.blue, label="Division", custom_id="division")
        ]
        msg = await channel.send(embed=categoryEmbed, components=[components])

        res69 = await discordClient.wait_for("button_click", check=buttonCheck)
        if res69.channel == channel and res69.component.custom_id == "war":
            await msg.edit(embed=categoryEmbed, components=[])

            clanType = "War Clan"

            positionEmbed = discord.Embed(
                title="**RR:H - AFFILIATION PROMPT**",
                description="What is your position in this group?",
                color=16776960
            )
            components = [
                Button(style=ButtonStyle.gray, label="Low Rank", custom_id="low rank"),
                Button(style=ButtonStyle.blue, label="High Rank", custom_id="high rank"),
                Button(style=ButtonStyle.red, label="High Command", custom_id="high command"),
                Button(style=ButtonStyle.green, label="Leader", custom_id="leader")
            ]
            positionEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

            msg = await channel.send(embed=positionEmbed, components=[components])

            async def why(leaders):
                whyEmbed = discord.Embed(
                    title="**RR:H - AFFILIATION PROMPT**",
                    description="Why do you want to affiliate with RR:H?",
                    color=16776960
                )
                whyEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

                await channel.send(embed=whyEmbed)

                def check(m):
                    return m.channel == channel and m.author == ctx.message.author
                msg = await discordClient.wait_for('message', check=check)
                for i in range(len(leaders)):
                    leaders[i] = f"<@{leaders[i]}>"

                def listToString(s):
                    str1 = " "
                    for ele in s:
                        str1 += ele
                    return str1

                newLeaders = listToString(leaders)
                group = await roClient.get_group(group_id=int(clanID))

                applicationEmbed = discord.Embed(
                    title="**RR:H - AFFILIATION APPLICATION**",
                    description=msg.content,
                    color=16776960
                )
                applicationEmbed.add_field(name="Category", value=clanType, inline=False)
                applicationEmbed.add_field(name="Group Name", value=group.name, inline=False)
                applicationEmbed.add_field(name="Member Position", value=rank, inline=False)
                applicationEmbed.add_field(name="Leader(s)", value=newLeaders, inline=False)
                applicationEmbed.set_footer(text=f"User ID: {ctx.message.author.id}")
                applicationEmbed.set_author(name=str(ctx.message.author), icon_url=ctx.message.author.avatar_url)
                applicationEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                components = [
                    Button(style=ButtonStyle.blue, label="Submit"),
                    Button(style=ButtonStyle.red, label="Cancel")
                ]
                role = ctx.message.guild.get_role(automationRole)
                msg = await channel.send(embed=applicationEmbed, components=[components])

                res6 = await discordClient.wait_for("button_click", check=buttonCheck)
                if res6.channel == channel and res6.component.style == ButtonStyle.blue:
                    await msg.edit(embed=applicationEmbed, components=[])

                    modChannel = discordClient.get_channel(modChannelId)
                    newComponents = [
                        Button(style=ButtonStyle.red, label="Decline"),
                        Button(style=ButtonStyle.blue, label="Accept")
                    ]
                    msg = await modChannel.send(content=f"{role.mention} | A new clan is requesting to affiliate to RR:H.", embed=applicationEmbed, components=[newComponents])
                    await res6.respond(content=":white_check_mark: | Application sent.")

                    def modChannelCheck(b):
                        return b.channel == modChannel
                    res8 = await discordClient.wait_for("button_click", check=modChannelCheck)
                    if res8.channel == modChannel and res8.component.style == ButtonStyle.blue:

                        await msg.edit(content=f"{role.mention} | {res8.user.mention} has accepted the following affiliation request.", embed=applicationEmbed, components=[])

                        addToDatabase(group=str(group_id), leaders=str(leaders), hicom=str(hicom), officials=str(officials),
                                      members=str(members), type=str(clanType), mainGroup=str(clanID))

                        await channel.send("Your application was accepted.")

                        logEmbed = discord.Embed(
                            title=":white_check_mark: __Affiliation Action Log:__",
                            description=f"**{group.name}** has been affiliated to Raid Request: Hub!\n\n**Category:** ``{clanType}``\n**Leader(s):** {newLeaders}",
                            color=65280
                        )
                        logEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                        logChannel = discordClient.get_channel(actionLogChannel)
                        await logChannel.send(embed=logEmbed)

                        return ctx.message.author.id

                    if res8.channel == modChannel and res8.component.style == ButtonStyle.red:
                        await msg.edit(
                            content=f"{role.mention} | {res8.user.mention} has declined the following affiliation request.",
                            embed=applicationEmbed, components=[])

                        await channel.send("Your application was declined.")
                        return ctx.message.author.id

                if res6.channel == channel and res6.component.style == ButtonStyle.red:
                    await msg.edit(embed=applicationEmbed, components=[])
                    await channel.send(":x: | Application not sent.")
                    return ctx.message.author.id

            async def whosLeader():
                whosLeaderEmbed = discord.Embed(
                    title="**RR:H - AFFILIATION PROMPT**",
                    description="What is the Discord Id of your leader? [If multiple you can seperate them by a "
                                "space:\nExample: ```578765234437881856 508227155444891658```",
                    color=16776960
                )
                whosLeaderEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

                await channel.send(embed=whosLeaderEmbed)

                def check(m):
                    return m.channel == channel and m.author == ctx.message.author
                msg = await discordClient.wait_for('message', check=check)
                leader = msg.content.rsplit(" ")
                await why(leaders=leader)

            resRank = await discordClient.wait_for("button_click", check=buttonCheck)
            if resRank.channel == channel and resRank.component.custom_id == "low rank":
                await msg.edit(embed=positionEmbed, components=[])
                rank = "Low Rank"
                members.insert(0, ctx.message.author.id)
                await whosLeader()
                return ctx.message.author.id
            elif resRank.channel == channel and resRank.component.custom_id == "high rank":
                await msg.edit(embed=positionEmbed, components=[])
                rank = "High Rank"
                officials.insert(0, ctx.message.author.id)
                await whosLeader()
                return ctx.message.author.id
            elif resRank.channel == channel and resRank.component.custom_id == "high command":
                await msg.edit(embed=positionEmbed, components=[])
                rank = "High Command"
                officials.insert(0, ctx.message.author.id)
                await whosLeader()
                return ctx.message.author.id
            elif resRank.channel == channel and resRank.component.custom_id == "leader":
                await msg.edit(embed=positionEmbed, components=[])
                rank = "Leader"
                leader = ctx.message.author.id
                await why(leaders=[leader])
                return ctx.message.author.id
        elif res69.channel == channel and res69.component.custom_id == "division":
            await msg.edit(embed=categoryEmbed, components=[])

            clanType = "Division"

            gidEmbed = discord.Embed(
                title="**RR:H - AFFILIATION PROMPT**",
                description="What is the division's ** main war clan** group id?",
                color=16776960
            )
            gidEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

            await channel.send(embed=gidEmbed)

            def check(m):
                return m.channel == channel and m.author == ctx.message.author
            msg = await discordClient.wait_for('message', check=check)
            clanID = msg.content

            positionEmbed = discord.Embed(
                title="**RR:H - AFFILIATION PROMPT**",
                description="What is your position in this group?",
                color=16776960
            )
            components = [
                Button(style=ButtonStyle.gray, label="Low Rank", custom_id="low rank"),
                Button(style=ButtonStyle.blue, label="High Rank", custom_id="high rank"),
                Button(style=ButtonStyle.red, label="High Command", custom_id="high command"),
                Button(style=ButtonStyle.green, label="Leader", custom_id="leader")
            ]
            positionEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

            msg = await channel.send(embed=positionEmbed, components=[components])

            async def why(leaders):
                whyEmbed = discord.Embed(
                    title="**RR:H - AFFILIATION PROMPT**",
                    description="Why do you want to affiliate with RR:H?",
                    color=16776960
                )
                whyEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

                await channel.send(embed=whyEmbed)

                def check(m):
                    return m.channel == channel and m.author == ctx.message.author

                msg = await discordClient.wait_for('message', check=check)
                for i in range(len(leaders)):
                    leaders[i] = f"<@{leaders[i]}>"

                group = await roClient.get_group(group_id=int(clanID))
                divGroup = await roClient.get_group(group_id=int(group_id))

                applicationEmbed = discord.Embed(
                    title="**RR:H - AFFILIATION APPLICATION**",
                    description=msg.content,
                    color=16776960
                )
                applicationEmbed.add_field(name="Category", value=clanType, inline=False)
                applicationEmbed.add_field(name="Group Name", value=f"{divGroup.name} ({group.name})", inline=False)
                applicationEmbed.add_field(name="Member Position", value=rank, inline=False)
                applicationEmbed.add_field(name="Leader(s)", value=leaders, inline=False)
                applicationEmbed.set_footer(text=f"User ID: {ctx.message.author.id}")
                applicationEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                components = [
                    Button(style=ButtonStyle.red, label="Cancel"),
                    Button(style=ButtonStyle.blue, label="Submit")
                ]
                role = ctx.message.guild.get_role(automationRole)
                msg = await channel.send(embed=applicationEmbed, components=[components])

                res6 = await discordClient.wait_for("button_click", check=buttonCheck)
                if res6.channel == channel and res6.component.style == ButtonStyle.blue:
                    await msg.edit(embed=applicationEmbed, components=[])

                    modChannel = discordClient.get_channel(modChannelId)
                    newComponents = [
                        Button(style=ButtonStyle.blue, label="Accept"),
                        Button(style=ButtonStyle.red, label="Decline")
                    ]
                    msg = await modChannel.send(content=f"{role.mention} | A new division is requesting to affiliate to RR:H.", embed=applicationEmbed, components=[newComponents])
                    await res6.respond(content=":white_check_mark: | Application sent.")
                    # await channel.send(":white_check_mark: | Application sent.")

                    def modChannelCheck(b):
                        return b.channel == modChannel

                    res8 = await discordClient.wait_for("button_click", check=modChannelCheck)
                    if res8.channel == modChannel and res8.component.style == ButtonStyle.blue:
                        await msg.edit(
                            content=f"{role.mention} | {res8.user.mention} has accepted the following affiliation request.",
                            embed=applicationEmbed, components=[])

                        addToDatabase(group=str(group_id), leaders=str(leaders), hicom=str(hicom), officials=str(officials),
                                      members=str(members), type=str(clanType), mainGroup=str(clanID))

                        await channel.send("Your application was accepted.")
                        return ctx.message.author.id

                    if res8.channel == modChannel and res8.component.style == ButtonStyle.red:
                        await msg.edit(
                            content=f"{role.mention} | {res8.user.mention} has declined the following affiliation request.",
                            embed=applicationEmbed, components=[])

                        await channel.send("Your application was declined.")
                        return ctx.message.author.id

                if res6.channel == channel and res6.component.style == ButtonStyle.red:
                    await msg.edit(embed=applicationEmbed, components=[])
                    await channel.send(":x: | Application not sent.")
                    return ctx.message.author.id

            async def whosLeader():
                whosLeaderEmbed = discord.Embed(
                    title="**RR:H - AFFILIATION PROMPT**",
                    description="What is the Discord Id of your leader? [If multiple you can seperate them by a "
                                "space:\nExample: ```578765234437881856 508227155444891658```",
                    color=16776960
                )
                whosLeaderEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

                await channel.send(embed=whosLeaderEmbed)

                def check(m):
                    return m.channel == channel and m.author == ctx.message.author

                msg = await discordClient.wait_for('message', check=check)
                leader = msg.content.rsplit(" ")
                await why(leaders=leader)

            resRank = await discordClient.wait_for("button_click", check=buttonCheck)
            if resRank.channel == channel and resRank.component.custom_id == "low rank":
                await msg.edit(embed=positionEmbed, components=[])
                rank = "Low Rank"
                members.insert(0, ctx.message.author.id)
                await whosLeader()
                return ctx.message.author.id
            elif resRank.channel == channel and resRank.component.custom_id == "high rank":
                await msg.edit(embed=positionEmbed, components=[])
                rank = "High Rank"
                officials.insert(0, ctx.message.author.id)
                await whosLeader()
                return ctx.message.author.id
            elif resRank.channel == channel and resRank.component.custom_id == "high command":
                await msg.edit(embed=positionEmbed, components=[])
                rank = "High Command"
                officials.insert(0, ctx.message.author.id)
                await whosLeader()
                return ctx.message.author.id
            elif resRank.channel == channel and resRank.component.custom_id == "leader":
                await msg.edit(embed=positionEmbed, components=[])
                rank = "Leader"
                leader = ctx.message.author.id
                await why(leaders=[leader])
                return ctx.message.author.id
            else:
                await msg.edit(embed=positionEmbed, components=[])
                await channel.send("SYNTAX ERROR. PLEASE RE-INPUT THE COMMAND AND USE A VALID OPTION. (Prompt finished.)")
                return ctx.message.author.id
