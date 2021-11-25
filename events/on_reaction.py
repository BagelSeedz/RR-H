import discord
import sqlite3

ticketsCategoryChannel = 899070308529631233
winsChannel = 899067189968113674


async def eReaction(payload, discordClient):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    channel = await discordClient.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await discordClient.fetch_user(payload.user_id)
    emoji = payload.emoji

    if str(emoji) != "⚠":
        return

    if message.channel.id == winsChannel:
        if user.id == 896183083685015562: # Bot
            return

        desc = message.embeds[0].description
        gid1Start = desc.find("groups/") + 7
        gid1Finish = desc.find(")")
        gid1 = desc[gid1Start:gid1Finish]
        desc2 = desc[gid1Finish+1:]
        gid2Start = desc2.find("groups/") + 7
        gid2Finish = desc2.find(")")
        gid2 = desc2[gid2Start:gid2Finish]

        userFound = False
        for row in cursor.execute('SELECT * FROM users ORDER BY userid'):
            if row[1] == str(user.id):
                userFound = True
                break
        if not userFound:
            dm = await user.create_dm()
            await dm.send("You must be a HR+ of a participating group in this battle to submit a ticket.")
            return

        hrFound = False
        for row in cursor.execute('SELECT * FROM groups'):
            if row[0] == gid1 and (row[1].find(str(user.id)) != -1 or row[2].find(str(user.id)) != -1 or row[3].find(str(user.id)) != -1):
                hrFound = True
                break
            if row[0] == gid2 and (row[1].find(str(user.id)) != -1 or row[2].find(str(user.id)) != -1 or row[3].find(str(user.id)) != -1):
                hrFound = True
                break
        if not hrFound:
            dm = await user.create_dm()
            await dm.send("You must be a HR+ of a participating group in this battle to submit a ticket.")
            return


        category = discordClient.get_channel(ticketsCategoryChannel)
        guild = message.guild

        ticketChannel = await guild.create_text_channel(
            name=f"ticket-{gid1}_vs_{gid2}",
            category=category
        )
        await ticketChannel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)

        ticketEmbed = discord.Embed(
            title="Welcome to your ticket!",
            description="Support Team will be with you shortly.",
            color=6559841
        )
        ticketEmbed.add_field(name="Click the link to see the Reported Message:", value=f"[Message]({message.jump_url})", inline=False)

        await ticketChannel.send(f"<@!{user.id}>", embed=ticketEmbed)
