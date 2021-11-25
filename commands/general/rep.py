import discord
import sqlite3


async def gRep(ctx, group_id, roClient):
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
    oldRep = None
    for row in cursor.execute("SELECT * FROM users ORDER BY userid"):
        if row[1] == str(ctx.message.author.id):
            userid = row[0]
            oldRep = row[3]
    if not userid:
        await ctx.send("You are not in the database! Use ```rr!bind```")
        return

    cursor.execute(f"UPDATE users SET repGroup = ? WHERE discord = {str(ctx.message.author.id)}", (group_id,))
    if oldRep and oldRep.isnumeric():
        for row in cursor.execute("SELECT * FROM groups ORDER BY repCount"):
            if row[0] == oldRep:
                repCount = None
                try:
                    repCount = int(row[8])
                except ValueError as err:
                    await ctx.send(f"ERROR: {err}")
                    return
                repCount -= 1
                cursor.execute(f"UPDATE groups SET repCount = ? WHERE groupid = {oldRep}", (repCount,))
    repCount = None
    try:
        repCount = int(bigRow[8])
    except ValueError as err:
        await ctx.send(f"ERROR: {err}")
        return
    repCount += 1
    cursor.execute(f"UPDATE groups SET repCount = ? WHERE groupid = {group_id}", (repCount,))

    user = await roClient.get_user(user_id=userid)
    group = await roClient.get_group(group_id=int(group_id))

    repEmbed = discord.Embed(
        title="REPRESENTATIVE ADDED :white_check_mark:",
        description=f"[{user.name}](https://www.roblox.com/users/{userid}/profile) now represents [{group.name}](https://www.roblox.com/groups/{group_id})!",
        color=16776960
    )
    await ctx.send(embed=repEmbed)
    db.commit()
    db.close()
