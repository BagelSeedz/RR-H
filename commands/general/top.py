import discord
import sqlite3


async def gTop(ctx, roClient):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    rows = []
    for row in cursor.execute('SELECT * FROM groups ORDER BY points DESC'):
        rows.insert(len(rows), row)

    topEmbed = discord.Embed(
        title=":star2: POINTS LEADERBOARD",
        color=16776960
    )
    for i in range(len(rows)):
        row = rows[i]
        if row[11] == "yes":
            group = await roClient.get_group(group_id=row[0])
            if row[5] == "War Clan":
                topEmbed.add_field(
                    name=f"```{i+1}.``` | {group.name} (https://www.roblox.com/groups/{row[0]})",
                    value=f"{row[7]} points | Group ID: {row[0]}",
                    inline=False
                )
            elif row[5] == "Division":
                topEmbed.add_field(
                    name=f"```{i + 1}.``` | {group.name} (https://www.roblox.com/groups/{row[0]})",
                    value=f"{row[7]} points | Group ID: {row[0]} | [{group.name} - Division](https://www.roblox.com/groups/{row[6]})",
                    inline=False
                )
            else:
                await ctx.send("Error: Please contact Automation.")
                return
    await ctx.send(embed=topEmbed)