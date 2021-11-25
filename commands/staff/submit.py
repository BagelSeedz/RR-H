import discord
from discord_components import *
import sqlite3
import requests
import json
from datetime import datetime, time
from pytz import timezone as tz
import math

submissionsChannel = 898695908454182912
automationRole = 906749972999966741
actionLogChannel = 910022427046731817


async def sSubmit(ctx, gid, discordClient, roClient):
    isHighRank = False
    roles = ctx.message.author.roles
    for i in range(len(roles)):
        if roles[i].id == 909593464155553862 or ctx.message.author.guild_permissions.administrator:
            isHighRank = True
    if not isHighRank:
        await ctx.send("You cannot use this command.")
        return

    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()

    groupFound = False
    for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
        if row[0] == gid:
            groupFound = True
            break
    if not groupFound:
        await ctx.send("This group is not in the database.")
        return

    await ctx.send("Check your dms! (If you did not get one, please enable \"Allow direct messages from server members\" in your Privacy and Safety settings)")
    dm = await ctx.message.author.create_dm()

    place = None
    type = None
    defaultNumbers = "N/A"
    name = None


    submitPrompt = discord.Embed(
        title="RR:H - SUBMIT PROMPT",
        description="Please select one of the 3 buttons below which best describes what you're trying to do.",
        color=16711680
    )
    submitPrompt.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
    components = [
        Button(style=ButtonStyle.gray, label="New Submission", custom_id="newSub"),
        Button(style=ButtonStyle.gray, label="Edit Submission", custom_id="editSub"),
        Button(style=ButtonStyle.gray, label="Delete Submission", custom_id="deleteSub")
    ]
    msg = await dm.send(embed=submitPrompt, components=[components])

    def check(m):
        return m.channel == dm and m.author == ctx.message.author

    def buttonCheck(b):
        return b.channel == dm

    standardTimezone = "UTC"
    displayTimezones = ["EST", "GMT"]

    def addSecondsToTime(values, seconds):
        o_mins = seconds / 60
        o_hours = math.floor(o_mins / 60)
        o_mins -= o_hours * 60
        hours, mins = values[0], values[1]
        mins += o_mins
        if mins >= 60:
            mins -= 60
            o_hours += 1
        hours += o_hours
        if hours >= 24:
            hours -= 24
        return [int(hours), int(mins)]

    def toDisplayTimes(values):  # takes [hours,mins]
        standard = tz(standardTimezone)
        dt = datetime.now()
        displayText = None
        for timezone in displayTimezones:
            offset = (tz(timezone).utcoffset(dt) - standard.utcoffset(dt)).seconds
            new = addSecondsToTime(values, offset)
            localisedTime = time(new[0], new[1]).strftime("%H:%M")
            if not displayText:
                displayText = f'{localisedTime} {timezone}'
            else:
                displayText = displayText + f", {localisedTime} {timezone}"
        return displayText

    def processTime(str):  # returns in [hours,mins] format
        raw = str.split(":")
        values = [23, 59]
        for i in range(2):
            new = raw[i]
            if not new.isdigit() or len(new) < 2:
                return None
            new = int(new)
            if new >= 0 and new <= values[i]:
                values[i] = new
            else:
                return None
        return values

    async def onMisinput(attempt):
        if attempt < 3:
            attemptEmbed = discord.Embed(
                title=":x: ERROR",
                description=f"{attempt}/3 | Invalid format was received!\nTry again following the valid format",
                color=16711680
            )
            await dm.send(embed=attemptEmbed)
            newMsg = await discordClient.wait_for("message", check=check)

            return newMsg
        else:
            attemptEmbed = discord.Embed(
                title=":x: ERROR",
                description=f"{attempt}/3 | You are out of tries!\nRun the command ``{ctx.message.content}`` again to continue.",
                color=16711680
            )
            await dm.send(embed=attemptEmbed)

            return False

    async def newSub():
        global prefloodTimes, notes
        placePrompt = discord.Embed(
            title="RR:H - SUBMIT PROMPT",
            description="Please enter the ID of the place you wish to add to your profile.",
            color=16711680
        )
        placePrompt.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        await dm.send(embed=placePrompt)

        msg = await discordClient.wait_for('message', check=check)
        name = None
        place = None
        for i in range(1, 4):
            place = msg.content
            placeLink = requests.get(f"https://api.roblox.com/Marketplace/ProductInfo?assetId={place}")
            placeParse = json.loads(placeLink.text)
            name = placeParse["Name"]
            if name:
                break
            msg = await onMisinput(i)
            if not msg:
                return

        typeEmbed = discord.Embed(
            title="RR:H - SUBMIT PROMPT",
            description="Please select the type of thing you wish to submit.",
            color=16711680
        )
        typeEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        components = [
            Button(style=ButtonStyle.gray, label="Fort", custom_id="fort"),
            Button(style=ButtonStyle.gray, label="Fairzone", custom_id="fairzone")
        ]
        msg = await dm.send(embed=typeEmbed, components=[components])

        prefloodTimes = "N/A"

        res0 = await discordClient.wait_for("button_click", check=buttonCheck)
        if res0.channel == dm:
            await msg.edit(embed=typeEmbed, components=[])

            type = res0.component.custom_id

            defaultNumbersEmbed = discord.Embed(
                title="RR:H - SUBMIT PROMPT",
                description="Please enter the following information about your base **IN THE GIVEN FORMAT.**",
                color=16711680
            )
            defaultNumbersEmbed.add_field(name="FORMAT:", value="```Default Numbers - Static/Non-Static```", inline=False)
            defaultNumbersEmbed.add_field(name="EXAMPLE:", value="10v10 - Static", inline=False)
            defaultNumbersEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
            await dm.send(embed=defaultNumbersEmbed)

            msg = await discordClient.wait_for('message', check=check)
            for i in range(1, 4):
                if (msg.content[0].isnumeric() or msg.content[1].isnumeric()) and (
                        msg.content[2].isnumeric() or msg.content[4].isnumeric()):
                    if (msg.content[6:] == "Static" or msg.content[6:] == "Non-Static") or (
                            msg.content[8:] == "Static" or msg.content[8:] == "Non-Static"):
                        break
                msg = await onMisinput(i)
                if not msg:
                    return

            defaultNumbers = msg.content

            prefloodEmbed = discord.Embed(
                title="RR:H - SUBMIT PROMPT",
                description=f"Is {name} prefloodable?",
                color=16711680
            )
            prefloodEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
            components = [
                Button(style=ButtonStyle.green, label="Yes", custom_id="yes"),
                Button(style=ButtonStyle.red, label="No", custom_id="no")
            ]
            msg = await dm.send(embed=prefloodEmbed, components=[components])

            res1 = await discordClient.wait_for("button_click", check=buttonCheck)
            if res1.channel == dm and res1.component.custom_id == "yes":
                await msg.edit(embed=prefloodEmbed, components=[])

                earlyEmbed = discord.Embed(
                    title="RR:H - SUBMIT PROMPT",
                    description=f"Please time the **earliest** time {name} is open to be preflooded in **UTC 24-hour time [HH:mm]**.\n\ne.g: ``13:00``, ``08:00``.\n\n*Use the [time zone converter](https://dateful.com/time-zone-converter) site if uncertain of EST.*",
                    color=16711680
                )
                earlyEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                await dm.send(embed=earlyEmbed)

                msg1 = await discordClient.wait_for('message', check=check)
                firstTime = None
                for i in range(1, 4):
                    test = processTime(msg1.content)
                    if test:
                        firstTime = toDisplayTimes(test).rsplit(" ")
                        break
                    msg1 = await onMisinput(i)
                    if not msg1:
                        return

                lateEmbed = discord.Embed(
                    title="RR:H - SUBMIT PROMPT",
                    description=f"Please time the **latest** time {name} is open to be preflooded in **UTC 24-hour time [HH:mm]**.\n\ne.g: ``13:00``, ``08:00``.\n\n*Use the [time zone converter](https://dateful.com/time-zone-converter) site if uncertain of EST.*",
                    color=16711680
                )
                lateEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                await dm.send(embed=lateEmbed)

                msg2 = await discordClient.wait_for('message', check=check)
                lastTime = None
                for i in range(1, 4):
                    test = processTime(msg2.content)
                    if test:
                        lastTime = toDisplayTimes(test).rsplit(" ")
                        break
                    msg2 = await onMisinput(i)
                    if not msg2:
                        return

                prefloodTimes = f"{firstTime[0]}-{lastTime[0]} (EST), {firstTime[2]}-{lastTime[2]} (GMT)"

            notesEmbed = discord.Embed(
                title="RR-H - SUBMIT PROMPT",
                description="Are there any notes you wish to include for people to know about this place?\n\nIf not, please type ``no``.",
                color=16711680
            )
            notesEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
            await dm.send(embed=notesEmbed)

            msg = await discordClient.wait_for('message', check=check)
            notes = "N/A"
            if msg.content != "no":
                notes = msg.content

            infoEmbed = discord.Embed(
                title="RR:H - SUBMIT PROMPT",
                description=f"**Does this information look correct?**\n\n[{name}](https://www.roblox.com/games/{place})",
                color=16711680
            )
            infoEmbed.add_field(name="Default Numbers: ", value=defaultNumbers, inline=False)
            infoEmbed.add_field(name="Preflood Times: ", value=prefloodTimes, inline=False)
            infoEmbed.add_field(name="Notes: ", value=notes, inline=False)
            infoEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
            components = [
                Button(style=ButtonStyle.blue, label="Yes", custom_id="yes0"),
                Button(style=ButtonStyle.red, label="No", custom_id="no0")
            ]

            msg = await dm.send(embed=infoEmbed, components=[components])

            res2 = await discordClient.wait_for("button_click", check=buttonCheck)
            if res2.channel == dm and res2.component.custom_id == "yes0":
                await msg.edit(embed=infoEmbed, components=[])

                group = await roClient.get_group(group_id=gid)
                confirmPrompt = discord.Embed(
                    title="RR:H - SUBMIT PROMPT",
                    description=f"Thank you for using the RR:H submission service!\nYour represented group [{group.name}](https://www.roblox.com/groups/{gid}) will be rewarded **5 points** when the application is accepted!",
                    color=65280  # Green
                )
                confirmPrompt.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                await dm.send(embed=confirmPrompt)

                role = ctx.message.guild.get_role(automationRole)
                modChannel = discordClient.get_channel(id=submissionsChannel)

                submitApplication = discord.Embed(
                    title="RR:H - SUBMIT APPLICATION",
                    color=16711680
                )
                submitApplication.add_field(name="Name:", value=f"[{name}](https://www.roblox.com/games/{place})", inline=False)
                submitApplication.add_field(name="Type:", value=type, inline=False)
                submitApplication.add_field(name="Default Numbers:", value=defaultNumbers, inline=False)
                submitApplication.add_field(name="Preflood Times:", value=prefloodTimes, inline=False)
                submitApplication.add_field(name="Notes:", value=notes, inline=False)
                submitApplication.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                submitApplication.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
                submitApplication.set_footer(text=f"User ID: {ctx.message.author.id}")
                components = [
                    Button(style=ButtonStyle.blue, label="Accept", custom_id="accept"),
                    Button(style=ButtonStyle.red, label="Decline", custom_id="decline")
                ]
                msg = await modChannel.send(f"{role.mention} | A new clan is requesting to upload a submission to RR:H.", embed=submitApplication, components=[components])

                def modChannelCheck(b):
                    return b.channel == modChannel

                res3 = await discordClient.wait_for("button_click", check=modChannelCheck)
                if res3.channel == modChannel and res3.component.custom_id == "accept":

                    await dm.send("Your application was accepted!")
                    newComponents = [
                        Button(style=ButtonStyle.green, label="Accept", disabled=True),
                        Button(style=ButtonStyle.gray, label="Decline", disabled=True)
                    ]
                    await msg.edit(f"{role.mention} | {res3.user.mention} has accepted the following submission.", embed=submitApplication, components=[newComponents])
                    await res3.respond(content=":thumbsup:")
                    bigRow = None
                    for row in cursor.execute('SELECT * FROM groups ORDER BY points'):
                        if row[0] == gid:
                            bigRow = row
                    results = bigRow[7]
                    addition = str(int(results) + 5)
                    cursor.execute("UPDATE groups SET points =? WHERE groupid =?", (addition, gid))
                    cursor.execute("INSERT INTO places VALUES (?, ?, ?, ?, ?, ?)",
                                   (str(place), str(gid), str(type), str(defaultNumbers), str(prefloodTimes), str(notes)))
                    db.commit()

                    logEmbed = discord.Embed(
                        title=":white_check_mark: __Submission Action Log:__",
                        description=f"**{group.name}** has added a new {type} to Raid Request: Hub!\n\n**Name:** ``{name}``\n**Default Numbers:** ``{defaultNumbers}``\n**Preflood Times:** ``{prefloodTimes}`` ```{notes}```",
                        color=65280
                    )
                    logEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                    logChannel = discordClient.get_channel(actionLogChannel)
                    await logChannel.send(embed=logEmbed)
                elif res3.channel == modChannel and res3.component.custom_id == "decline":
                    newComponents = [
                        Button(style=ButtonStyle.gray, label="Accept", disabled=True),
                        Button(style=ButtonStyle.green, label="Decline", disabled=True)
                    ]
                    await dm.send("Your application has been declined.")
                    await res3.respond(content=":thumbsup:")
                    await msg.edit(
                        f"{role.mention} | {res3.user.mention} has declined the following submission.", embed=submitApplication, components=[newComponents])

            elif res2.channel == dm and res2.component.custom_id == "no0":
                await msg.edit(embed=infoEmbed, components=[])

                await dm.send(content=":x: Submission not sent.")
                return

    async def editSub():
        enterEmbed = discord.Embed(
            title="RR:H - SUBMIT PROMPT",
            description="Please enter the ID of the place you wish to edit.",
            color=16776960
        )
        enterEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        await dm.send(embed=enterEmbed)

        msg = await discordClient.wait_for('message', check=check)
        for i in range(1, 4):
            if str(msg.content).isnumeric():
                break
            msg = await onMisinput(i)
            if not msg:
                return

        place = msg.content

        selectEmbed = discord.Embed(
            title="RR:H - SUBMIT PROMPT",
            description="Please select what you want to edit.",
            color=16776960
        )
        selectEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        components = [
            Button(style=ButtonStyle.gray, label="Base Information", custom_id="base"),
            Button(style=ButtonStyle.gray, label="Prefloodable Value", custom_id="preflood"),
            Button(style=ButtonStyle.gray, label="Notes", custom_id="notes")
        ]
        msg = await dm.send(embed=selectEmbed, components=[components])

        res0 = await discordClient.wait_for("button_click", check=buttonCheck)
        if res0.channel == dm and res0.component.custom_id == "base":
            await msg.edit(embed=selectEmbed, components=[])

            defaultNumbersEmbed = discord.Embed(
                title="RR:H - SUBMIT PROMPT",
                description="Please enter the following information about your base **IN THE GIVEN FORMAT.**",
                color=16711680
            )
            defaultNumbersEmbed.add_field(name="FORMAT:", value="```Default Numbers - Static/Non-Static```",
                                          inline=False)
            defaultNumbersEmbed.add_field(name="EXAMPLE:", value="10v10 - Static", inline=False)
            defaultNumbersEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
            await dm.send(embed=defaultNumbersEmbed)

            msg = await discordClient.wait_for('message', check=check)
            for i in range(1, 4):
                if (msg.content[0].isnumeric() or msg.content[1].isnumeric()) and (
                        msg.content[2].isnumeric() or msg.content[4].isnumeric()):
                    if (msg.content[6:] == "Static" or msg.content[6:] == "Non-Static") or (
                            msg.content[8:] == "Static" or msg.content[8:] == "Non-Static"):
                        break
                msg = await onMisinput(i)
                if not msg:
                    return

            cursor.execute(f"UPDATE places SET defaultNumbers = ? WHERE placeid = {place}", (msg.content,))
            db.commit()

            await dm.send(":white_check_mark: **Base Information Updated.**")
        elif res0.channel == dm and res0.component.custom_id == "preflood":
            await msg.edit(embed=selectEmbed, components=[])

            prefloodTimes = "N/A"

            prefloodEmbed = discord.Embed(
                title="RR:H - SUBMIT PROMPT",
                description=f"Is your place prefloodable?",
                color=16711680
            )
            prefloodEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
            components = [
                Button(style=ButtonStyle.green, label="Yes", custom_id="yes"),
                Button(style=ButtonStyle.red, label="No", custom_id="no")
            ]
            msg = await dm.send(embed=prefloodEmbed, components=[components])

            res1 = await discordClient.wait_for("button_click", check=buttonCheck)
            if res1.channel == dm and res1.component.custom_id == "yes":
                await msg.edit(embed=prefloodEmbed, components=[])

                earlyEmbed = discord.Embed(
                    title="RR:H - SUBMIT PROMPT",
                    description=f"Please time the **earliest** time {name} is open to be preflooded in **UTC 24-hour time [HH:mm]**.\n\ne.g: ``13:00``, ``08:00``.\n\n*Use the [time zone converter](https://dateful.com/time-zone-converter) site if uncertain of EST.*",
                    color=16711680
                )
                earlyEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                await dm.send(embed=earlyEmbed)

                msg1 = await discordClient.wait_for('message', check=check)
                firstTime = None
                for i in range(1, 4):
                    test = processTime(msg1.content)
                    if test:
                        firstTime = toDisplayTimes(test).rsplit(" ")
                        break
                    msg1 = await onMisinput(i)
                    if not msg1:
                        return

                lateEmbed = discord.Embed(
                    title="RR:H - SUBMIT PROMPT",
                    description=f"Please time the **latest** time {name} is open to be preflooded in **UTC 24-hour time [HH:mm]**.\n\ne.g: ``13:00``, ``08:00``.\n\n*Use the [time zone converter](https://dateful.com/time-zone-converter) site if uncertain of EST.*",
                    color=16711680
                )
                lateEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                await dm.send(embed=lateEmbed)

                msg2 = await discordClient.wait_for('message', check=check)
                lastTime = None
                for i in range(1, 4):
                    test = processTime(msg2.content)
                    if test:
                        lastTime = toDisplayTimes(test).rsplit(" ")
                        break
                    msg2 = await onMisinput(i)
                    if not msg2:
                        return

                prefloodTimes = f"{firstTime[0]}-{lastTime[0]} (EST), {firstTime[2]}-{lastTime[2]} (GMT)"

            cursor.execute(f"UPDATE places SET prefloodTimes = ? WHERE placeid = {place}", (prefloodTimes,))
            db.commit()

            await dm.send(":white_check_mark: **Preflood Times Updated.**")
        elif res0.channel == dm and res0.component.custom_id == "notes":
            await msg.edit(embed=selectEmbed, components=[])

            notesEmbed = discord.Embed(
                title="RR-H - SUBMIT PROMPT",
                description="Are there any notes you wish to include for people to know about this place?\n\nIf not, please type ``no``.",
                color=16711680
            )
            notesEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
            await dm.send(embed=notesEmbed)

            msg = await discordClient.wait_for('message', check=check)
            notes = "N/A"
            if msg.content != "no":
                notes = msg.content

            cursor.execute(f"UPDATE places SET notes = ? WHERE placeid = {place}", (notes,))
            db.commit()

            await dm.send(":white_check_mark: **Notes Updated.**")

    async def deleteSub():
        enterEmbed = discord.Embed(
            title="RR:H - SUBMIT PROMPT",
            description="Please enter the ID of the place you wish to delete.",
            color=16776960
        )
        enterEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        await dm.send(embed=enterEmbed)

        msg = await discordClient.wait_for('message', check=check)
        for i in range(1, 4):
            if str(msg.content).isnumeric():
                break
            msg = await onMisinput(i)
            if not msg:
                return

        place = msg.content

        cursor.execute(f"DELETE FROM places WHERE placeid = {place}")
        db.commit()

        await dm.send(":white_check_mark: **Submission Deleted.**")


    res = await discordClient.wait_for("button_click", check=buttonCheck)
    if res.channel == dm and res.component.custom_id == "newSub":
        await msg.edit(embed=submitPrompt, components=[])
        await newSub()
    elif res.channel == dm and res.component.custom_id == "editSub":
        await msg.edit(embed=submitPrompt, components=[])
        await editSub()
    elif res.channel == dm and res.component.custom_id == "deleteSub":
        await msg.edit(embed=submitPrompt, components=[])
        await deleteSub()
