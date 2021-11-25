import discord
import sqlite3


async def gMain(ctx, group_id, roClient):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    bigRow = None
    for row in cursor.execute("SELECT * FROM groups ORDER BY groupid"):
        if row[0] == group_id:
            bigRow = row
    if not bigRow:
        await ctx.send("This group is not in the database!")
        return

    userid = None
    for row in cursor.execute("SELECT * FROM users ORDER BY userid"):
        if row[1] == str(ctx.message.author.id):
            userid = row[0]
    if not userid:
        await ctx.send("You are not in the database! Use ```rr!bind```")
        return

    cursor.execute(f"UPDATE users SET mainClan = ? WHERE discord = {str(ctx.message.author.id)}", (group_id,))
    user = await roClient.get_user(user_id=userid)
    group = await roClient.get_group(group_id=int(group_id))
    updateEmbed = discord.Embed(
        title="PRIMARY CHANGED :white_check_mark:",
        description=f"[{user.name}](https://www.roblox.com/users/{userid}/profile) changed their main group to [{group.name}](https://www.roblox.com/groups/{group_id})!",
        color=16776960
    )
    await ctx.send(embed=updateEmbed)
    db.commit()
    db.close()
