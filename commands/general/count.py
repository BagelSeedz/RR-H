import sqlite3
import discord


async def gCount(ctx, group_id, roClient):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    bigRow = None
    for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
        if row[0] == group_id:
            bigRow = row
    if not bigRow:
        await ctx.send("Group not found in the database!")
        return

    repCount = bigRow[8]
    mainCount = 0

    for row in cursor.execute('SELECT * FROM users'):
        if row[2] == group_id:
            mainCount += 1

    group = await roClient.get_group(group_id=int(group_id))

    countEmbed = discord.Embed(
        title=f"TOTAL MEMBERS IN {str.upper(group.name)}",
        color=16776960
    )
    countEmbed.add_field(name="__Representatives__", value=repCount, inline=True)
    countEmbed.add_field(name="__Members__", value=str(mainCount), inline=True)

    await ctx.send(embed=countEmbed)