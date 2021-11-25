import discord
import sqlite3
import requests
import json
import datetime
from pytz import timezone

db = sqlite3.connect("main.sqlite")
cursor = db.cursor()


async def gOpen(ctx, type, roClient):
    if type != "void":
        rows = []
        if type == "forts":
            for row in cursor.execute('SELECT * FROM places'):
                if row[2] == "fort" and row[4] != "N/A":
                    estStart = row[4][:5]
                    estEnd = row[4][6:11]
                    tz = timezone('EST')
                    currentTime = str(datetime.datetime.now(tz))[11:16]
                    intEstStart = int(estStart.replace(":", ""))
                    intEstEnd = int(estEnd.replace(":", ""))
                    intCurrentTime = int(currentTime.replace(":", ""))
                    if intEstStart <= intCurrentTime <= intEstEnd:
                        rows.insert(len(rows), row)
        elif type == "fairzones":
            for row in cursor.execute('SELECT * FROM places'):
                if row[2] == "fairzone" and row[4] != "N/A":
                    estStart = row[4][:5]
                    estEnd = row[4][6:11]
                    tz = timezone('EST')
                    currentTime = str(datetime.datetime.now(tz))[11:16]
                    intEstStart = int(estStart.replace(":", ""))
                    intEstEnd = int(estEnd.replace(":", ""))
                    intCurrentTime = int(currentTime.replace(":", ""))
                    if intEstStart <= intCurrentTime <= intEstEnd:
                        rows.insert(len(rows), row)

        openEmbed = discord.Embed(
            title=f"AVAILABLE {str.upper(type)}",
            description="Use ``rr!profile {GroupId}`` for details on a specific group.",
            color=65280
        )
        openEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        for i in range(len(rows)):
            row = rows[i]
            group = await roClient.get_group(row[1])
            groupName = group.name
            placeLink = requests.get(f"https://api.roblox.com/Marketplace/ProductInfo?assetId={row[0]}")
            placeParse = json.loads(placeLink.text)
            name = placeParse["Name"]

            openEmbed.add_field(
                name=f"{group.name} ``{row[1]}``",
                value=f"[{name}](https://www.roblox.com/games/{row[0]}) ``{row[4]}``",
                inline=False
            )

        await ctx.send(embed=openEmbed)
    elif type == "void":
        fortRows = []
        fairzoneRows = []

        for row in cursor.execute('SELECT * FROM places'):
            if row[2] == "fort" and row[4] != "N/A":
                estStart = row[4][:5]
                estEnd = row[4][6:11]
                tz = timezone('EST')
                currentTime = str(datetime.datetime.now(tz))[11:16]
                intEstStart = int(estStart.replace(":", ""))
                intEstEnd = int(estEnd.replace(":", ""))
                intCurrentTime = int(currentTime.replace(":", ""))
                print(f"{intEstStart}, {intCurrentTime}, {intEstEnd}")
                if intEstStart <= intCurrentTime <= intEstEnd:
                    fortRows.insert(len(fortRows), row)
            elif row[2] == "fairzone" and row[4] != "N/A":
                estStart = row[4][:5]
                estEnd = row[4][6:11]
                tz = timezone('EST')
                currentTime = str(datetime.datetime.now(tz))[11:16]
                intEstStart = int(estStart.replace(":", ""))
                intEstEnd = int(estEnd.replace(":", ""))
                intCurrentTime = int(currentTime.replace(":", ""))
                if intEstStart <= intCurrentTime <= intEstEnd:
                    fairzoneRows.insert(len(fairzoneRows), row)

        openEmbed = discord.Embed(
            title=f"AVAILABLE GROUPS",
            description="Use ``rr!profile {GroupId}`` for details on a specific group.",
            color=65280
        )
        openEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

        openEmbed.add_field(name="\u200b", value="**AVAILABLE FORTS**", inline=False)
        for i in range(len(fortRows)):
            row = fortRows[i]
            group = await roClient.get_group(row[1])
            groupName = group.name
            placeLink = requests.get(f"https://api.roblox.com/Marketplace/ProductInfo?assetId={row[0]}")
            placeParse = json.loads(placeLink.text)
            name = placeParse["Name"]

            openEmbed.add_field(
                name=f"{group.name} ``{row[1]}``",
                value=f"[{name}](https://www.roblox.com/games/{row[0]}) ``{row[4]}``",
                inline=False
            )

        openEmbed.add_field(name="\u200b", value="**AVAILABLE FAIRZONES**", inline=False)
        for i in range(len(fairzoneRows)):
            row = fairzoneRows[i]
            group = await roClient.get_group(row[1])
            groupName = group.name
            placeLink = requests.get(f"https://api.roblox.com/Marketplace/ProductInfo?assetId={row[0]}")
            placeParse = json.loads(placeLink.text)
            name = placeParse["Name"]

            openEmbed.add_field(
                name=f"{group.name} ``{row[1]}``",
                value=f"[{name}](https://www.roblox.com/games/{row[0]}) ``{row[4]}``",
                inline=False
            )

        await ctx.send(embed=openEmbed)