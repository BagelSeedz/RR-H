async def aAdd(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("This command is for admins only.")
        return
    if ctx.message.channel.name.find("ticket") == -1:
        await ctx.send("This command can only be used in a ticket channel.")
        return

    member = ctx.message.mentions[0]

    await ctx.message.channel.set_permissions(member, read_messages=True, send_messages=True, view_channel=True)
    await ctx.send(f"{member.mention} has been added to the channel")
