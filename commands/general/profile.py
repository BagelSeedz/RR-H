import math
import discord
import sqlite3
from ro_py import thumbnails
import requests
import json
from discord.utils import get

db = sqlite3.connect("main.sqlite")
cursor = db.cursor()


async def gProfile(ctx, roClient):
    type = None

    originalContent = ctx.message.content
    remainingContent = str(originalContent).removeprefix("rr!profile")

    if remainingContent.find("<@") != -1:
        type = "mention"
    else:
        try:
            integerCheck = int(remainingContent)
            type = "group"
        except:
            type = "self"

    async def userProfile(userid):
        userRow = None
        for row in cursor.execute("SELECT * FROM users"):
            if row[1] == str(userid):
                userRow = row
        if not userRow:
            await ctx.send("Please bind your account before using this command ``rr!bind``.")
            return

        highPositions = []
        officalPositions = []
        memberPositions = []
        for row in cursor.execute("SELECT * FROM groups"):
            if str(row[2]).find(str(userid)) != -1:
                highPositions.insert(len(highPositions), row[0])
            if str(row[3]).find(str(userid)) != -1:
                officalPositions.insert(len(officalPositions), row[0])
            if str(row[4]).find(str(userid)) != -1:
                memberPositions.insert(len(memberPositions), row[0])
        if len(highPositions) == 0:
            highPositions = "None."
        else:
            for i in range(len(highPositions)):
                group = await roClient.get_group(int(highPositions[i]))
                highPositions[i] = f"[{group.name}](https://www.roblox.com/groups/{highPositions[i]})"
        if len(officalPositions) == 0:
            officalPositions = "None."
        else:
            for i in range(len(officalPositions)):
                group = await roClient.get_group(int(officalPositions[i]))
                officalPositions[i] = f"[{group.name}](https://www.roblox.com/groups/{officalPositions[i]})"
        if len(memberPositions) == 0:
            memberPositions = "None."
        else:
            for i in range(len(memberPositions)):
                group = await roClient.get_group(int(memberPositions[i]))
                memberPositions[i] = f"[{group.name}](https://www.roblox.com/groups/{memberPositions[i]})"

        user = await roClient.get_user(int(userRow[0]))
        playerPic = await user.thumbnails.get_avatar_image(shot_type=thumbnails.ThumbnailType.avatar_full_body)

        mainClanId = userRow[2]
        mainClanObject = None
        mainClan = "None"
        if mainClanId != "None":
            mainClanObject = await roClient.get_group(int(mainClanId))
            mainClan = mainClanObject.name

        clanRank = "None."
        if mainClan != "None":
            for row in cursor.execute("SELECT * FROM groups"):
                if row[0] == str(mainClanId):
                    if str(row[1]).find(str(userid)) != -1:
                        clanRank = "Leader"
                    elif str(row[2]).find(str(userid)) != -1:
                        clanRank = "HICOM"
                    elif str(row[3]).find(str(userid)) != -1:
                        clanRank = "Officer"
                    elif str(row[4]).find(str(userid)) != -1:
                        clanRank = "Member"
            profileEmbed = discord.Embed(
                title=user.name,
                description=f"**Main Clan:** [{mainClan}](https://www.roblox.com/groups/{mainClanId})\n**Clan Rank:** ``{clanRank}``",
                color=65280
            )
            profileEmbed.set_thumbnail(url=str(playerPic))

            if highPositions != "None.":
                profileEmbed.add_field(name="HIGH POSITIONS", value=", ".join(highPositions), inline=False)
            else:
                profileEmbed.add_field(name="HIGH POSITIONS", value="‎", inline=False)

            if officalPositions != "None.":
                profileEmbed.add_field(name="OFFICER POSITIONS", value=", ".join(officalPositions), inline=False)
            else:
                profileEmbed.add_field(name="OFFICER POSITIONS", value="‎", inline=False)

            if memberPositions != "None.":
                profileEmbed.add_field(name="MEMBER POSITIONS", value=", ".join(memberPositions), inline=False)
            else:
                profileEmbed.add_field(name="MEMBER POSITIONS", value="‎", inline=False)

            await ctx.send(embed=profileEmbed)
        elif mainClan == "None":
            profileEmbed = discord.Embed(
                title=user.name,
                color=65280
            )
            profileEmbed.set_thumbnail(url=str(playerPic))

            if highPositions != "None.":
                profileEmbed.add_field(name="HIGH POSITIONS", value=", ".join(highPositions), inline=False)
            else:
                profileEmbed.add_field(name="HIGH POSITIONS", value="‎", inline=False)

            if officalPositions != "None.":
                profileEmbed.add_field(name="OFFICER POSITIONS", value=", ".join(officalPositions), inline=False)
            else:
                profileEmbed.add_field(name="OFFICER POSITIONS", value="‎", inline=False)

            if memberPositions != "None.":
                profileEmbed.add_field(name="MEMBER POSITIONS", value=", ".join(memberPositions), inline=False)
            else:
                profileEmbed.add_field(name="MEMBER POSITIONS", value="‎", inline=False)

            await ctx.send(embed=profileEmbed)

    async def groupProfile(gid):
        groupRow = None
        for row in cursor.execute("SELECT * FROM groups ORDER BY groupid"):
            if row[0] == gid:
                groupRow = row
        if not groupRow:
            await ctx.send("The group which you just inputted is not in our database! Groups are added when they are "
                           "affiliated or when they are reviewed.")
            return

        forts = []
        fairzones = []
        for row in cursor.execute("SELECT * FROM places"):
            if row[1] == gid:
                if row[2] == "fort":
                    forts.insert(len(forts), row)
                elif row[2] == "fairzone":
                    fairzones.insert(len(fairzones), row)

        rep = round(float(groupRow[9])/2, 1)
        fullStars = math.trunc(rep)
        rep2 = round((float(groupRow[9])/2) + 0.0001)
        addHalfStar = False
        if rep < rep2:
            addHalfStar = True
        repPercent = round(float(groupRow[9]) * 10)

        stars = ""
        for i in range(fullStars):
            fullStarEmoji = get(ctx.message.guild.emojis, name="full_star")
            stars = f"{stars}{fullStarEmoji}"
        if addHalfStar:
            halfStarEmoji = get(ctx.message.guild.emojis, name="half_star")
            stars = f"{stars}{halfStarEmoji}"
            fullStars += 1
        for i in range((5 - fullStars)):
            emptyStarEmoji = get(ctx.message.guild.emojis, name="empty_star")
            stars = f"{stars}{emptyStarEmoji}"

        group = await roClient.get_group(int(gid))

        desc = f"[{group.name}](https://www.roblox.com/groups/{gid}) - Verified Group of **RR:H.** :white_check_mark:\n \n**Review Rating:** {stars} **({int(repPercent)/20})**\n\n```python\nGroup Points: {groupRow[7]}```"
        if groupRow[11] == "no":
            desc = f":x: [{group.name}](https://www.roblox.com/groups/{gid}) - Unverified Group of **RR:H** :no_entry:\n \n**Review Rating:** {stars} **({int(repPercent)/20})**\n\n```python\nGroup Points: {groupRow[7]}```"

        title = f"{str.upper(group.name)} ({str.upper(groupRow[5])})"
        if groupRow[5] == "[None]":
            title = f"{str.upper(group.name)} (UNASSIGNED)"

        guildEmbed = discord.Embed(
            title=title,
            description=desc,
            color=65280
        )
        guildEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        # guildEmbed.add_field(name="GROUP REPUTATION:", value=f"{stars} {repPercent}%\n\n```python\nGroup Points: {groupRow[7]}```", inline=False)
        value = "‎"
        for i in range(len(forts)):
            fort = forts[i]
            place = fort[0]
            placeLink = requests.get(f"https://api.roblox.com/Marketplace/ProductInfo?assetId={place}")
            placeParse = json.loads(placeLink.text)
            name = placeParse["Name"]

            pTimes = fort[4]
            if pTimes == "N/A":
                pTimes = "Schedule Only"

            addedValue = f"[{name}](https://www.roblox.com/games/{place})\nDefault Numbers: ``{fort[3]}``\nPreflood Times: ``{pTimes}``\nNotes: ``{fort[5]}``"
            value = f"{value}\n{addedValue}"
        guildEmbed.add_field(name="LISTED FORTS:", value=f"{value}", inline=False)
        value = "‎"
        for i in range(len(fairzones)):
            fairzone = fairzones[i]

            place = fairzone[0]
            placeLink = requests.get(f"https://api.roblox.com/Marketplace/ProductInfo?assetId={place}")
            placeParse = json.loads(placeLink.text)
            name = placeParse["Name"]

            pTimes = fairzone[4]
            if pTimes == "N/A":
                pTimes = "Schedule Only"

            addedValue = f"[{name}](https://www.roblox.com/games/{place})\nDefault Numbers: ``{fairzone[3]}``\nPreflood Times: ``{pTimes}``\nNotes: ``{fairzone[5]}``"
            value = f"{value}\n{addedValue}"
        guildEmbed.add_field(name="LISTED FAIRZONES:", value=f"{value}", inline=False)

        await ctx.send(embed=guildEmbed)

    if type == "mention":
        userid = ctx.message.mentions[0].id
        await userProfile(userid)
    elif type == "group":
        gid = str(ctx.message.content).removeprefix("rr!profile ")
        await groupProfile(gid=gid)
    elif type == "self":
        userid = ctx.message.author.id
        await userProfile(userid)
