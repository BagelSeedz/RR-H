import discord
import asyncio

scrimChannel = 897958725762056262
scrimRole = 897960424069275659


async def sScrimmage(ctx, link, discordClient, command):
    isHighRank = False
    roles = ctx.message.author.roles
    for i in range(len(roles)):
        if roles[i].id == 909593464155553862 or ctx.message.author.guild_permissions.administrator:
            isHighRank = True
    if not isHighRank:
        msg = await ctx.send("You cannot use this command.")
        command.reset_cooldown(ctx)
        await asyncio.sleep(5)
        await msg.delete()
        await ctx.message.delete()
        return

    if ctx.message.channel.id != scrimChannel:
        msg = await ctx.send("This command can only be used in #scrim-request.")
        command.reset_cooldown(ctx)
        await asyncio.sleep(5)
        await msg.delete()
        await ctx.message.delete()
        return

    if str(link).find("https://www.roblox.com/games/") == -1:
        msg = await ctx.send(
            "Please post a valid link: ``rr!scrimmage {LINK} {NOTES}``\nLink must start with: ``https://www.roblox.com/games/``")
        command.reset_cooldown(ctx)
        await asyncio.sleep(5)
        await msg.delete()
        await ctx.message.delete()
        return

    notes = str(ctx.message.content).removeprefix(f"rr!scrimmage {link} ")
    if len(notes) == 0:
        msg = await ctx.send("Please provide notes.")
        command.reset_cooldown(ctx)
        await asyncio.sleep(5)
        await msg.delete()
        await ctx.message.delete()
        return

    fairzoneEmbed = discord.Embed(
        title="SCRIMMAGE REQUEST",
        url=link,
        description=f"<@{ctx.message.author.id}> is requesting for a group to scrimmage against.\n```{notes}```",
        color=16711680
    )
    fairzoneEmbed.set_footer(text="This command can only be used once per 10 minutes.")

    channel = discordClient.get_channel(scrimChannel)
    await channel.send(f"<@&{scrimRole}> {link}", embed=fairzoneEmbed)
    msg = await ctx.send("Request sent!")
    await asyncio.sleep(5)
    await msg.delete()
    await ctx.message.delete()
    return
