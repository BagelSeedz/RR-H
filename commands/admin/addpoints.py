import sqlite3

import discord

actionLogChannel = 910022427046731817


async def aAddPoints(ctx, group_id, amount, discordClient, roClient):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("This command is for admins only.")
        return

    if not group_id or not amount:
        await ctx.send("Please input all that is required for the command to work: ``rr!addpoints {group_id} {amount}``")

    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    bigRow = None
    for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
        if row[0] == group_id:
            bigRow = row
    if not bigRow:
        await ctx.send("Group not found in the database!")
        return

    results = bigRow[7]
    addition = str(int(results) + int(amount))
    if int(addition) < 0:
        addition = "0"
    cursor.execute("""UPDATE groups SET points =? WHERE groupid =? """, (addition, group_id))
    db.commit()
    db.close()

    await ctx.send(f"Successfully added {amount} points to group {group_id}.")

    logChannel = discordClient.get_channel(actionLogChannel)
    group = await roClient.get_group(int(group_id))

    index = len(group_id) + len(amount) + 15
    reason = ctx.message.content[index:]

    if int(amount) >= 0:
        logEmbed = discord.Embed(
            title=":white_check_mark: __Admin Audit Action Log:__",
            description=f"**{group.name}** has received **{amount} points** by Raid Request: Hub! ```{reason}```\n**Added By:** ``{ctx.message.author.name}`` ({ctx.message.author.mention})",
            color=65280
        )
        logEmbed.add_field(name="Previous Amount:", value=f"``{results} Points``", inline=True)
        logEmbed.add_field(name="Current Amount:", value=f"``{addition} Points``", inline=True)
        logEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
    else:
        logEmbed = discord.Embed(
            title=":white_check_mark: __Admin Audit Action Log:__",
            description=f"**{group.name}** has lost **{amount[1:]} points** by Raid Request: Hub! ```{reason}```\n**Removed By:** ``{ctx.message.author.name}`` ({ctx.message.author.mention})",
            color=16711680
        )
        logEmbed.add_field(name="Previous Amount:", value=f"``{results} Points``", inline=True)
        logEmbed.add_field(name="Current Amount:", value=f"``{addition} Points``", inline=True)
        logEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

    await logChannel.send(embed=logEmbed)
