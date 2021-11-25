async def gPing(ctx, latency):
    await ctx.send(f"Pong! ``{round(latency * 1000)}ms``")
