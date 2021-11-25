import discord
from discord_components import *
import sqlite3

db = sqlite3.connect("main.sqlite")
cursor = db.cursor()

reviewChannel = 899055098217529354
winsChannel = 899067189968113674
automationRole = 906749972999966741
actionLogChannel = 910022427046731817


async def sReview(ctx, gid1, gid2, roClient, discordClient):
    isHighRank = False
    roles = ctx.message.author.roles
    for i in range(len(roles)):
        if roles[i].id == 909593464155553862 or ctx.message.author.guild_permissions.administrator:
            isHighRank = True
    if not isHighRank:
        await ctx.send("You cannot use this command.")
        return ctx.message.author.id

    group1Row = None
    for row in cursor.execute("SELECT * FROM groups ORDER BY groupid"):
        if row[0] == gid1:
            group1Row = row
    if not group1Row:
        await ctx.send("Your group is not in the database!")
        return ctx.message.author.id

    group2Row = None
    for row in cursor.execute("SELECT * FROM groups ORDER BY groupid"):
        if row[0] == gid2:
            group2Row = row
    if not group2Row:
        cursor.execute("INSERT INTO groups VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
        str(gid2), "[None]", "[None]", "[None]", "[None]", "[None]", str(gid2), "0", "0", "10.0", "0", "no"))
        db.commit()

    await ctx.send("Check your dms! (If you did not get one, please enable \"Allow direct messages from server members\" in your Privacy and Safety settings)")
    dm = await ctx.message.author.create_dm()

    pos = None
    type = None
    win = False
    startingNumbers = None
    imageLink = None
    punctuality = 0
    concord = 0
    hostRating = 0
    overallNotes = None

    def check(m):
        return m.channel == dm and m.author == ctx.message.author

    def buttonCheck(b):
        return b.channel == dm

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


    async def overview():
        overallRating = round(((punctuality + concord + hostRating) / 15) * 5)

        group1 = await roClient.get_group(int(gid1))
        group2 = await roClient.get_group(int(gid2))

        overviewEmbed = discord.Embed(
            title=f"REVIEW ON {group1.name}",
            description=f"``Group Action Type:`` {pos}\n``Other Party:`` [{group2.name}](https://www.roblox.com/groups/{gid2})\n``Achieved Victory:`` {win}\n``Image Proof:`` {imageLink}\n\n``Overall Review:``\n{overallNotes}",
            color=16776960
        )
        overviewEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

        punctualityChecks = ""
        for i in range(punctuality):
            checkMark = ":white_check_mark:"
            punctualityChecks = f"{punctualityChecks}{checkMark}"
        for i in range((5 - punctuality)):
            square = ":black_large_square:"
            punctualityChecks = f"{punctualityChecks}{square}"

        concordChecks = ""
        for i in range(concord):
            checkMark = ":white_check_mark:"
            concordChecks = f"{concordChecks}{checkMark}"
        for i in range((5 - concord)):
            square = ":black_large_square:"
            concordChecks = f"{concordChecks}{square}"

        hostRatingChecks = ""
        for i in range(hostRating):
            checkMark = ":white_check_mark:"
            hostRatingChecks = f"{hostRatingChecks}{checkMark}"
        for i in range((5 - hostRating)):
            square = ":black_large_square:"
            hostRatingChecks = f"{hostRatingChecks}{square}"

        overallRatingChecks = ""
        for i in range(overallRating):
            checkMark = ":white_check_mark:"
            overallRatingChecks = f"{overallRatingChecks}{checkMark}"
        for i in range((5 - overallRating)):
            square = ":black_large_square:"
            overallRatingChecks = f"{overallRatingChecks}{square}"

        overviewEmbed.add_field(name=f"Punctuality: ``[{punctuality}/5]``", value=punctualityChecks, inline=False)
        overviewEmbed.add_field(name=f"Concord: ``[{concord}/5]``", value=concordChecks, inline=False)
        overviewEmbed.add_field(name=f"Host Rating: ``[{hostRating}/5]``", value=hostRatingChecks, inline=False)
        overviewEmbed.add_field(name=f"Overall Rating: ``[{overallRating}/5]``", value=overallRatingChecks,
                                inline=False)
        overviewEmbed.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)

        components = [
            Button(style=ButtonStyle.gray, label="Cancel", custom_id="no"),
            Button(style=ButtonStyle.gray, label="Submit", custom_id="yes")
        ]

        msg = await dm.send("Here's a preview of your post. Do you wish to send it?", embed=overviewEmbed,
                      components=[components])

        res6 = await discordClient.wait_for("button_click", check=buttonCheck)
        if res6.channel == dm and res6.component.custom_id == "yes":
            newComponents = [
                Button(style=ButtonStyle.green, label="Yes", disabled=True),
                Button(style=ButtonStyle.gray, label="No", disabled=True)
            ]
            await msg.edit("Here's a preview of your post. Do you wish to send it?", embed=overviewEmbed, components=[newComponents])

            completeEmbed = discord.Embed(
                title="RR:H - REVIEW PROMPT",
                description=f"__**REVIEW COMPLETE**__\nThank you for using the RR:H review service!\nYour group [{group1.name}](https://www.roblox.com/groups/{gid1}) will be rewarded **10 points** if the application is accepted!\n\nIf you have a question regarding this review, don't hesitate to contact anybody with the ``Server Handler`` role.",
                color=16776960
            )
            completeEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")

            await res6.respond(embed=completeEmbed)

            components = [
                Button(style=ButtonStyle.blue, label="Accept", custom_id="accept"),
                Button(style=ButtonStyle.red, label="Decline", custom_id="deny")
            ]
            role = ctx.message.guild.get_role(automationRole)
            modChannel = discordClient.get_channel(id=reviewChannel)

            msg = await modChannel.send(f"{role.mention} | A clan is attempting to submit a review:", embed=overviewEmbed, components=[components])

            def modChannelCheck(b):
                return b.channel == modChannel

            res7 = await discordClient.wait_for("button_click", check=modChannelCheck)
            if res7.channel == modChannel and res7.component.custom_id == "accept":
                newComponents = [
                    Button(style=ButtonStyle.green, label="Accept", disabled=True),
                    Button(style=ButtonStyle.gray, label="Decline", disabled=True)
                ]
                await msg.edit(f"{role.mention} | {res7.user.mention} has accepted the following review.",
                               embed=overviewEmbed, components=[newComponents])
                await res7.respond(content=":thumbsup:")
                await dm.send("Your review has been accepted!")

                pointsResults = group1Row[7]
                pointsAddition = str(int(pointsResults) + 10)
                cursor.execute("UPDATE groups SET points = ? WHERE groupid = ? ", (pointsAddition, gid1))

                reputationResults = group2Row[10]
                reputationAddition = str(int(reputationResults) + 1)
                cursor.execute("UPDATE groups SET reputationCount = ? WHERE groupid = ?", (reputationAddition, gid2))

                score = (float(group2Row[9]) + (overallRating * 2))/int(reputationAddition) # FORMULA IS WRONG
                cursor.execute("UPDATE groups set reputationScore = ? WHERE groupid = ?", (str(score), gid2))

                db.commit()

                if win:
                    victoryEmbed = discord.Embed(
                        title=f":trophy: __{group1.name} Victory Log__",
                        description=f"[{group1.name}](https://www.roblox.com/groups/{gid1}) has successfully defeated [{group2.name}](https://www.roblox.com/groups/{gid2}) in a raid!\n\n**Starting Numbers:** ``{startingNumbers}``\n**Schedule Type:** ``{type}``",
                        color=16776960
                    )
                    victoryEmbed.set_image(url=imageLink)
                    victoryChannel = discordClient.get_channel(winsChannel)
                    victoryMessage = await victoryChannel.send(embed=victoryEmbed)
                    await victoryMessage.add_reaction(emoji="⚠")

                logEmbed = discord.Embed(
                    title=":white_check_mark: __Battle Review Action Log:__",
                    description=f"**{group1.name}** has reviewed a **{type}** against **{group2Name}**! ```{overallNotes}```\n**Overall Review:** ``{overallRating}/5``",
                    color=65280
                )
                logEmbed.add_field(name="Punctuality:", value=punctualityChecks, inline=True)
                logEmbed.add_field(name="Concord:", value=concordChecks, inline=True)
                logEmbed.add_field(name="Host's Rating:", value=hostRatingChecks, inline=True)
                logEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                logChannel = discordClient.get_channel(actionLogChannel)
                await logChannel.send(embed=logEmbed)
                return ctx.message.author.id
            elif res7.channel == modChannel and res7.component.custom_id == "deny":
                newComponents = [
                    Button(style=ButtonStyle.gray, label="Accept", disabled=True),
                    Button(style=ButtonStyle.green, label="Decline", disabled=True)
                ]
                await msg.edit(f"{role.mention} | {res7.user} has denied the following review.", embed=overviewEmbed,
                               components=[newComponents])

                await res7.respond(content=":thumbsup:")
                await dm.send("Your review has been denied.")
                return ctx.message.author.id
        elif res6.channel == dm and res6.component.custom_id == "no":
            newComponents = [
                Button(style=ButtonStyle.gray, label="Yes", disabled=True),
                Button(style=ButtonStyle.green, label="No", disabled=True)
            ]
            await msg.edit("Here's a preview of your post. Do you wish to send it?", embed=overviewEmbed,
                           components=[newComponents])

            noEmbed = discord.Embed(
                title=":white_check_mark: SUCCESS",
                description="The application was not sent.",
                color=65280
            )
            await res6.respond(embed=noEmbed)
            return ctx.message.author.id


    reviewPrompt = discord.Embed(
        title="RR:H - REVIEW PROMPT",
        description="Reviews are to be made on groups after the clan you represent has had an event with them. **You "
                    "are allowed to submit a review on a group every event you have with them.**\n\nA reviewal team "
                    "is in charge of processing reviews so ensure that the review you leave is an honest and "
                    "non-exaggerated one. **Reviews should be based on the event you had, not your thoughts on the "
                    "clan.**\n\n**Once read and agreed to the above, click ``Continue``** ",
        color=16776960
    )
    reviewPrompt.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
    components = [
        Button(style=ButtonStyle.gray, label="Continue", custom_id="continue")
    ]
    msg = await dm.send(embed=reviewPrompt, components=[components])

    resCont = await discordClient.wait_for("button_click", check=buttonCheck)
    if resCont.channel == dm and resCont.component.custom_id == "continue":
        await msg.edit(embed=reviewPrompt, components=[])
        posEmbed = discord.Embed(
            title="RR:H - REVIEW PROMPT",
            description="Was your group the raiding or defending group?",
            color=16776960
        )
        posEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
        components = [
            Button(style=ButtonStyle.gray, label="Raiding", custom_id="raiding"),
            Button(style=ButtonStyle.gray, label="Defending", custom_id="defending")
        ]
        msg = await dm.send(embed=posEmbed, components=[components])

        res = await discordClient.wait_for("button_click", check=buttonCheck)
        if res.channel == dm:
            await msg.edit(embed=posEmbed, components=[])

            pos = res.component.custom_id

            typeEmbed = discord.Embed(
                title="RR:H - REVIEW PROMPT",
                description="Was this a scheduled event or a preflood?",
                color=16776960
            )
            typeEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
            components = [
                Button(style=ButtonStyle.gray, label="Scheduled", custom_id="scheduled"),
                Button(style=ButtonStyle.gray, label="Preflood", custom_id="preflood")
            ]
            msg = await dm.send(embed=typeEmbed, components=[components])

            res0 = await discordClient.wait_for("button_click", check=buttonCheck)
            if res0.channel == dm:
                await msg.edit(embed=typeEmbed, components=[])

                type = res0.component.custom_id

                group2 = await roClient.get_group(int(gid2))
                group2Name = group2.name

                attendEmbed = discord.Embed(
                    title="RR:H - REVIEW PROMPT",
                    description=f"Did {group2Name} fail to attend or did they attend the event?",
                    color=16776960
                )
                attendEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                components = [
                    Button(style=ButtonStyle.gray, label="Attended Event", custom_id="attended"),
                    Button(style=ButtonStyle.gray, label="Failed to Attend", custom_id="failed")
                ]
                msg = await dm.send(embed=attendEmbed, components=[components])

                res1 = await discordClient.wait_for("button_click", check=buttonCheck)
                if res1.channel == dm and res1.component.custom_id == "attended":
                    await msg.edit(embed=attendEmbed, components=[])

                    winEmbed = discord.Embed(
                        title="RR:H - PROMPT",
                        description="Did your group win the battle?",
                        color=16776960
                    )
                    winEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                    components = [
                        Button(style=ButtonStyle.gray, label="Yes", custom_id="win"),
                        Button(style=ButtonStyle.gray, label="No", custom_id="loss")
                    ]
                    msg = await dm.send(embed=winEmbed, components=[components])

                    res2 = await discordClient.wait_for("button_click", check=buttonCheck)
                    if res2.channel == dm and res2.component.custom_id == "win":
                        await msg.edit(embed=winEmbed, components=[])

                        win = True

                        numbersEmbed = discord.Embed(
                            title="RR:H - REVIEW PROMPT",
                            description="What were the starting numbers in the battle?\n\nPlease use the following format (CASE SENSITIVE):\n#v# - Static/Non-Static\n\nExamples:\n- ``10v10 - Static``\n- ``8v8 - Non-Static``",
                            color=16776960
                        )
                        numbersEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                        await dm.send(embed=numbersEmbed)

                        msg = await discordClient.wait_for("message", check=check)

                        for i in range(1, 4):
                            if (msg.content[0].isnumeric() or msg.content[1].isnumeric()) and (
                                    msg.content[2].isnumeric() or msg.content[4].isnumeric()):
                                if (msg.content[6:] == "Static" or msg.content[6:] == "Non-Static") or (
                                        msg.content[8:] == "Static" or msg.content[8:] == "Non-Static"):
                                    break
                            msg = await onMisinput(i)
                            if not msg:
                                return ctx.message.author.id

                        startingNumbers = msg.content

                        imageEmbed = discord.Embed(
                            title="RR:H - REVIEW PROMPT",
                            description="Please provide a screenshot proof **LINK** of your group winning the "
                                        "defence.\nYou can use image hosting sites like [Imgur](https://imgur.com/) "
                                        "and [Gyazo](https://gyazo.com/). ",
                            color=16776960
                        )
                        imageEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                        await dm.send(embed=imageEmbed)

                        msg = await discordClient.wait_for("message", check=check)
                        for i in range(1, 4):
                            if msg.content[:8] == "https://":
                                break
                            msg = await onMisinput(i)
                            if not msg:
                                return ctx.message.author.id

                        imageLink = msg.content
                    elif res2.channel == dm and res2.component.custom_id == "loss":
                        await msg.edit(embed=winEmbed, components=[])

                    if res2.channel == dm:
                        serviceEmbed1 = discord.Embed(
                            title="RR:H - REVIEW PROMPT",
                            description="__**HOST SERVICE**__\nWere the opposition ready to the battle at a quick "
                                        "time, or was there a delay in starting?\n\n``1/5:`` Massive delay. The host "
                                        "took an incredibly long time to start.\n``5/5:`` No delay. The host were "
                                        "ready to defend in a quick time. ",
                            color=16776960
                        )
                        serviceEmbed1.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                        contents = [
                            Button(style=ButtonStyle.gray, label="One", custom_id="1-1"),
                            Button(style=ButtonStyle.gray, label="Two", custom_id="2-1"),
                            Button(style=ButtonStyle.gray, label="Three", custom_id="3-1"),
                            Button(style=ButtonStyle.gray, label="Four", custom_id="4-1"),
                            Button(style=ButtonStyle.gray, label="Five", custom_id="5-1")
                        ]

                        msg = await dm.send(embed=serviceEmbed1, components=[contents])

                        res3 = await discordClient.wait_for("button_click", check=buttonCheck)
                        if res3.channel == dm and res3.component.custom_id[2] == "1":
                            await msg.edit(embed=serviceEmbed1, components=[])

                            punctuality = int(res3.component.custom_id[0])

                            serviceEmbed2 = discord.Embed(
                                title="RR:H - REVIEW PROMPT",
                                description="__**HOST SERVICE**__\nWere there are issues regarding cheating, "
                                            "admin-abusing or exploiting, or did the event go smoothly?\n\n``1/5:`` "
                                            "Multiple issues. Very high amounts of these things occured.\n``5/5:`` No "
                                            "issues. The event went smooth with no problems. ",
                                color=16776960
                            )
                            serviceEmbed2.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                            contents = [
                                Button(style=ButtonStyle.gray, label="One", custom_id="1-2"),
                                Button(style=ButtonStyle.gray, label="Two", custom_id="2-2"),
                                Button(style=ButtonStyle.gray, label="Three", custom_id="3-2"),
                                Button(style=ButtonStyle.gray, label="Four", custom_id="4-2"),
                                Button(style=ButtonStyle.gray, label="Five", custom_id="5-2")
                            ]
                            msg = await dm.send(embed=serviceEmbed2, components=[contents])

                            res4 = await discordClient.wait_for("button_click", check=buttonCheck)
                            if res4.channel == dm and res4.component.custom_id[2] == "2":
                                await msg.edit(embed=serviceEmbed2, components=[])

                                concord = int(res4.component.custom_id[0])

                                serviceEmbed3 = discord.Embed(
                                    title="RR:H - REVIEW PROMPT",
                                    description=f"__**HOST SERVICE**__\nWhat would you rate the host of {group2Name} out of 5?",
                                    color=16776960
                                )
                                serviceEmbed3.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                                contents = [
                                    Button(style=ButtonStyle.gray, label="One", custom_id="1-3"),
                                    Button(style=ButtonStyle.gray, label="Two", custom_id="2-3"),
                                    Button(style=ButtonStyle.gray, label="Three", custom_id="3-3"),
                                    Button(style=ButtonStyle.gray, label="Four", custom_id="4-3"),
                                    Button(style=ButtonStyle.gray, label="Five", custom_id="5-3")
                                ]
                                msg = await dm.send(embed=serviceEmbed3, components=[contents])

                                res5 = await discordClient.wait_for("button_click", check=buttonCheck)
                                if res5.channel == dm and res5.component.custom_id[2] == "3":
                                    await msg.edit(embed=serviceEmbed3, components=[])

                                    hostRating = int(res5.component.custom_id[0])

                                    overallEmbed = discord.Embed(
                                        title="RR:H - REVIEW PROMPT",
                                        description="Please include your overall review on how the event went and why "
                                                    "you gave your rating. Feel free to include any appropriate "
                                                    "evidence. ",
                                        color=16776960
                                    )
                                    overallEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                                    await dm.send(embed=overallEmbed)

                                    msg = await discordClient.wait_for("message", check=check)
                                    overallNotes = msg.content

                                    await overview()

                elif res1.channel == dm and res1.component.custom_id == "failed":
                    await msg.edit(embed=attendEmbed, components=[])

                    serviceEmbed3 = discord.Embed(
                        title="RR:H - REVIEW PROMPT",
                        description=f"__**HOST SERVICE**__\nWhat would you rate the host of {group2Name} out of 5?",
                        color=16776960
                    )
                    serviceEmbed3.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                    contents = [
                        Button(style=ButtonStyle.gray, label="One", custom_id="1-4"),
                        Button(style=ButtonStyle.gray, label="Two", custom_id="2-4"),
                        Button(style=ButtonStyle.gray, label="Three", custom_id="3-4"),
                        Button(style=ButtonStyle.gray, label="Four", custom_id="4-4"),
                        Button(style=ButtonStyle.gray, label="Five", custom_id="5-4")
                    ]
                    msg = await dm.send(embed=serviceEmbed3, components=[contents])

                    res5 = await discordClient.wait_for("button_click", check=buttonCheck)
                    if res5.channel == dm and res5.component.custom_id[2] == "4":
                        await msg.edit(embed=serviceEmbed3, components=[])

                        hostRating = int(res5.component.custom_id[0])

                        overallEmbed = discord.Embed(
                            title="RR:H - REVIEW PROMPT",
                            description="Please include your overall review on how the event went and why "
                                        "you gave your rating. Feel free to include any appropriate "
                                        "evidence. ",
                            color=16776960
                        )
                        overallEmbed.set_thumbnail(url="https://i.imgur.com/O0qaTbb.jpg")
                        await res5.respond(embed=overallEmbed)

                        msg = await discordClient.wait_for("message", check=check)
                        overallNotes = msg.content

                        await overview()
