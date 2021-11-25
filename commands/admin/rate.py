import sqlite3


async def aRate(ctx, args):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("This command is for admins only.")
        return

    if len(args) == 0:
        await ctx.send("Please include a valid Group ID.")
        return
    elif len(args) == 1:
        await ctx.send("Please include a valid Star Rating")
        return

    gid = args[0]
    rating = args[1]

    bigRow = None
    for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
        if row[0] == gid:
            bigRow = row
    if not bigRow:
        await ctx.send("Group not found in the database!")
        return

    if not 1 <= float(rating) <= 5.0:
        await ctx.send("Please insert a Star Rating between 1 and 5")
        return

    oldReputationCount = bigRow[10]
    newReputationCount = str(int(oldReputationCount) - 1)
    if int(newReputationCount) < 0:
        newReputationCount = "0"
    cursor.execute(f"UPDATE groups SET reputationCount = {newReputationCount} WHERE groupid = {gid}")
    cursor.execute(f"UPDATE groups SET reputationScore = {float(rating)*2.0} WHERE groupid = {gid}")
    db.commit()

    await ctx.send("Success.")

