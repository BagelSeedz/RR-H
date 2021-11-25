import sqlite3
import discord
import requests
import json
import asyncio
from ro_py import thumbnails


async def gBind(ctx, client):
    print(-5)
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    print(-4)
    userFound = False
    for row in cursor.execute('SELECT * FROM users ORDER BY userid'):
        if row[1] == str(ctx.message.author.id):
            userFound = True
            break
    print(userFound)
    if userFound:
        await ctx.send("You are already in the database!")
        return
    print(-3)
    discordID = ctx.message.author.id

    print(1)
    bloxlinkR = requests.get(f"https://api.blox.link/v1/user/{discordID}")
    print(2)
    if bloxlinkR.text == "You are being ratelimited.":
        print(3)
        await ctx.send("Please wait a minute...")
        await asyncio.sleep(60)
    print(4)
    print(bloxlinkR.text)
    bloxlinkParse = json.loads(bloxlinkR.text)
    print(5)
    if bloxlinkParse["status"] == "error":
        await ctx.send("You are currently not verified to **Bloxlink**. Please verify to their database or show proof "
                       "to an Admin what your roblox account is.")
        return
    bloxlinkUserId = bloxlinkParse["primaryAccount"]
    print(6)

    user = None
    try:
        user = await client.get_user(int(bloxlinkUserId))
        print(user)
    except:
        print(7)
        await ctx.send("You are currently not verified to **Bloxlink**. Please verify to their database or show proof "
                       "to an Admin what your roblox account is.")
        return
    print(8)
    playerPic = await user.thumbnails.get_avatar_image(shot_type=thumbnails.ThumbnailType.avatar_full_body)

    cursor.execute("INSERT INTO users (userid, discord) VALUES(?, ?)", (user.id, ctx.message.author.id))
    db.commit()
    db.close()

    bindEmbed = discord.Embed(
        title=":white_check_mark: **SUCCESS**",
        description="You have been successfully added to the database.",
        color=65280
    )
    bindEmbed.add_field(name="__**Roblox Username**__", value=str(user.name), inline=False)
    bindEmbed.add_field(name="__**Roblox Id**__", value=str(user.id), inline=False)
    bindEmbed.set_thumbnail(url=str(playerPic))

    await ctx.send(embed=bindEmbed)
