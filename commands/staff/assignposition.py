import discord
import sqlite3

actionLogChannel = 910022427046731817


async def sAssignPosition(ctx, gid, user, rank, roClient, discordClient):
    isHighRank = False
    roles = ctx.message.author.roles
    for i in range(len(roles)):
        if roles[i].id == 909593464155553862 or ctx.message.author.guild_permissions.administrator:
            isHighRank = True
    if not isHighRank:
        await ctx.send("You cannot use this command.")
        return

    if not 0 < int(rank) < 5:
        await ctx.send("Please insert a valid rank")
        return

    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    bigRow = None
    for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
        if row[0] == gid:
            bigRow = row
    if not bigRow:
        await ctx.send("Group not found in the database!")
        return

    discordID = None
    try:
        discordID = str(ctx.message.mentions[0].id)
    except:
        discordID = user

    group = await roClient.get_group(int(gid))

    oldRank = 0
    for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
        if row[0] == gid:
            if row[1].find(discordID) != -1:
                oldRank = 1
            elif row[2].find(discordID) != -1:
                oldRank = 2
            elif row[3].find(discordID) != -1:
                oldRank = 3
            elif row[4].find(discordID) != -1:
                oldRank = 4

    def rankCheck(integer):
        if integer == 1:
            return "leaders"
        elif integer == 2:
            return "hicom"
        elif integer == 3:
            return "officials"
        elif integer == 4:
            return "members"

    def executeFunction(orank):
        oldCell = None
        for cell in cursor.execute('SELECT * FROM groups ORDER BY points'):
            if cell[0] == gid:
                oldCell = cell[orank]
        oldCell = str(oldCell).replace(f" <@{discordID}>", "")
        oldCell = str(oldCell).lstrip("None")
        check = rankCheck(orank)
        cursor.execute(f"UPDATE groups SET {check} = ? WHERE groupid = {gid}", (oldCell,))

        oldInput = None
        for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
            if row[0] == gid:
                oldInput = row[int(rank)]
        newInput = f"{str(oldInput)} <@{discordID}>"

        if int(rank) == 1:
            cursor.execute(f"UPDATE groups SET leaders = ? WHERE groupid = {gid}", (newInput,))
        elif int(rank) == 2:
            cursor.execute(f"UPDATE groups SET hicom = ? WHERE groupid = {gid}", (newInput,))
        elif int(rank) == 3:
            cursor.execute(f"UPDATE groups SET officials = ? WHERE groupid = {gid}", (newInput,))
        elif int(rank) == 4:
            cursor.execute(f"UPDATE groups SET members = ? WHERE groupid = {gid}", (newInput,))

    def insertLog(num):
        discUser = discordClient.get_user(int(discordID))
        role = None
        if num == 1:
            role = "leader"
        elif num == 2:
            role = "HICOM"
        elif num == 3:
            role = "officer"
        elif num == 4:
            role = "member"
        logEmbed = discord.Embed(
            title=":white_check_mark: __Group Audit Action Log:__",
            description=f"**{group.name}** added a new **{role}** ``[{num}]`` to their group!\n\n**User Added:** ``{discUser.name}`` ({discUser.mention})\n**Added By:** ``{ctx.message.author.name}`` ({ctx.message.author.mention})",
            color=65280
        )
        logEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        return logEmbed

    if oldRank == 0:
        oldInput = None
        for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
            if row[0] == gid:
                oldInput = row[int(rank)]
        newInput = f"{str(oldInput)} <@{discordID}>"
        if int(rank) == 1:
            cursor.execute(f"UPDATE groups SET leaders = ? WHERE groupid = {gid}", (newInput,))
        elif int(rank) == 2:
            cursor.execute(f"UPDATE groups SET hicom = ? WHERE groupid = {gid}", (newInput,))
        elif int(rank) == 3:
            cursor.execute(f"UPDATE groups SET officials = ? WHERE groupid = {gid}", (newInput,))
        elif int(rank) == 4:
            cursor.execute(f"UPDATE groups SET members = ? WHERE groupid = {gid}", (newInput,))

        channel = discordClient.get_channel(actionLogChannel)
        logEmbed = insertLog(int(rank))
        await channel.send(embed=logEmbed)
        await ctx.send(f"Successfully reassigned user to rank {rankCheck(int(rank))}.")
        db.commit()
    elif oldRank == 1:
        for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
            if row[0] == gid:
                if row[1].find(" ") != -1:
                    executeFunction(oldRank)
                    channel = discordClient.get_channel(actionLogChannel)
                    logEmbed = insertLog(int(rank))
                    await channel.send(embed=logEmbed)
                    await ctx.send(f"Successfully reassigned user to rank {rankCheck(int(rank))}.")
                    db.commit()
                else:
                    await ctx.send("Please promote a new leader to rank 1 before using this command.")
    elif 1 < oldRank < 5:
        executeFunction(oldRank)
        channel = discordClient.get_channel(actionLogChannel)
        logEmbed = insertLog(int(rank))
        await channel.send(embed=logEmbed)
        await ctx.send(f"Successfully reassigned user to rank {rankCheck(int(rank))}.")
        db.commit()
