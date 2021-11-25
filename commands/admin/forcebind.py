import sqlite3
import discord
from ro_py import thumbnails


async def aForcebind(ctx, client, userid):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("This command is for admins only.")
        return

    discordID = None
    try:
        discordID = ctx.message.mentions[0].id
    except:
        await ctx.send("Please mention a valid user!")
        return

    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    userFound = False
    for row in cursor.execute('SELECT * FROM users ORDER BY userid'):
        if row[1] == str(discordID):
            userFound = True
            break
    if userFound:
        await ctx.send("User is already in the database!")
        return

    if not userid.isnumeric():
        await ctx.send("Please type the UserID of the individual.")
        return

    user = await client.get_user(int(userid))
    playerPic = await user.thumbnails.get_avatar_image(shot_type=thumbnails.ThumbnailType.avatar_full_body)

    cursor.execute("INSERT INTO users (userid, discord) VALUES(?, ?)", (user.id, discordID))
    db.commit()
    db.close()

    bindEmbed = discord.Embed(
        title=":white_check_mark: **SUCCESS**",
        description="The user have been successfully added to the database.",
        color=65280
    )
    bindEmbed.add_field(name="__**Roblox Username**__", value=str(user.name), inline=False)
    bindEmbed.add_field(name="__**Roblox Id**__", value=str(user.id), inline=False)
    bindEmbed.set_thumbnail(url=str(playerPic))

    await ctx.send(embed=bindEmbed)
