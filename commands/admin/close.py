import discord
import asyncio
import io

archivesChannel = 899123529407152159


async def aClose(ctx, discordClient):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("You cannot use this command!")
        return

    if str(ctx.message.channel.name).find("ticket") == -1:
        await ctx.send("This is not a ticket channel.")
        return

    deleteEmbed = discord.Embed(
        title="This channel will be deleted in 20 seconds.",
        description="A ``txt`` file of the conversation will be created and sent in the archives channel.",
        color=16711680
    )

    await ctx.send(embed=deleteEmbed)

    messages = await ctx.message.channel.history(limit=None, oldest_first=True).flatten()
    stringFile = ""
    for message in messages:
        stringFile = f"{stringFile}\n{message.author.name}: {message.content}"

    byteFile = io.BytesIO(stringFile.encode('utf-8'))

    await asyncio.sleep(20)

    file = discord.File(
        filename=f"{ctx.message.channel.name}.txt",
        fp=byteFile
    )
    archives = discordClient.get_channel(archivesChannel)
    await archives.send(file=file)

    await ctx.message.channel.delete()

