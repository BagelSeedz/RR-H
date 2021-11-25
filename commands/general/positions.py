import discord
import sqlite3


async def gPositions(ctx, group_id, client):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    groupFound = False
    row1 = None
    for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
        if row[0] == str(group_id):
            groupFound = True
            row1 = row
            break
    if not groupFound:
        await ctx.send("This group needs to be affiliated first! Use ```rr!affiliate```")
        return

    group = await client.get_group(group_id=int(group_id))

    # hicomSTR = row1[2]
    # hicomPRE = hicomSTR.rstrip("[")
    # hicomSUF = hicomPRE.removesuffix("]")
    # hicom = hicomSTR.rsplit(", ")
    # print(hicom)
    # hicom.remove("None")
    # for i in range(len(hicom)):
    #     hicom[i] = f"<@{hicom[i]}>"

    positionsEmbed = discord.Embed(
        title=f"{str.upper(group.name)} - Roles",
        color=65280
    )
    positionsEmbed.add_field(name="Leaders", value=row1[1], inline=False)
    positionsEmbed.add_field(name="HICOM", value=row1[2], inline=False)
    positionsEmbed.add_field(name="Officials", value=row1[3], inline=False)
    positionsEmbed.add_field(name="Members", value=row1[4], inline=False)

    await ctx.send(embed=positionsEmbed)
