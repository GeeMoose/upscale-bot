import discord
from discord.ext import commands
import aiohttp
import asyncio
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='>', intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')
# con = aiohttp.ProxyConnector(proxy="http://localhost:7890")
# client = discord.Client(connector = con)
# @bot.command()
async def test():
    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://google.com") as r:
            print('yey')
            
# coro = test()
# asyncio.run(coro)
# bot.run('TOKEN_KEY')