import os 
import yaml
import re
import io
import discord
from discord.ext import commands

import helpers

description = """A1D image upscale bot entirely in python"""


config = yaml.safe_load(open("./config.yml"))


bot = commands.Bot()

# bot.remove_command("help")


if config['global_guild_block']:
	@bot.check
	# Note to anyone who sees this, you can safely remove this if you want to run a bot that runs anywhere
	async def globally_block_not_guild(ctx):
		is_dm = ctx.guild is None
		if is_dm and config["block_dms"]:
			print(f"DM, {ctx.author.name}")
			guild = bot.get_guild(config["guild_id"])
			guild_member = await guild.fetch_member(ctx.author.id)
			role = discord.utils.find(
				lambda r: r.name == config["patreon_role_name"], guild_member.roles
			)
			if role:
				print(f"{ctx.author.name} is permitted to use the bot in DMs.")
				return True
			else:
				await ctx.message.channel.send(
					"{}, A1D bot is not permitted for use in DMs. Sorry.".format(
						ctx.author.mention
					)
				)
			return False
		else:
			is_gu = ctx.guild.id == config["guild_id"]
			if not is_gu:
				print(f"{ctx.guild.name}, {ctx.author.name}")
				await ctx.message.channel.send(
					"{}, A1D bot is not permitted for use in this server.Sorry.".format(
						ctx.author.mention
					)
				)
				return False
			return True

class A1D():
    def __init__(self, bot):
        self.bot = bot
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name} - {bot.user.id}")

        await bot.change_presence(
            status=discord.Status.online, activity=discord.Game("A1D Upscale")
        )


    # 测试代码
    # @slash.slash(name="ping")
    # async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
    #     await ctx.send(f"Pong! ({bot.latency*1000}ms)")
    
    @bot.slash_command(name="help",description="description for a1d image upscale bot usage")
    async def help(ctx):
        embed = discord.Embed(description=(
            """Commands:

`/image [url]` Upscale your image with a label up to scale what you want 

There is four distinct type of labels:
General/general、Anime/anime、Landscope/landscope and Protrait/protrait

scaleFactor is allowed to input from 1 to 4


Example: `/image www.imageurl.com/image.png`""".format(
                bot.command_prefix
            )
        ))
        embed.set_author(name="Image Upscale", icon_url="https://cdn.discordapp.com/app-icons/1147108244825854013/456a49b3de52aad7d3c9043596f4660d.png?size=256")
        embed.set_thumbnail(url="https://pbs.twimg.com/media/F6_lZPgaAAAi7Yz?format=png&name=small")
        embed.set_image(url="https://pbs.twimg.com/media/F6_kjcCbYAA6Fi4?format=webp&name=small")
        await ctx.respond(embed=embed) 
       
        
    
    #一个是命令行交互的能力
    @bot.slash_command(name="image",description="upscale image with a1d")
    async def upscale(ctx,input:str):
        imageurl = ""
        model = ""
        scale = ""
        result = "result.jpg"
     
        if re.match(r'^(?:http|ftp)s?://', input) is not None:
            imageurl = input
   
        if imageurl == "":
            await ctx.respond("The input format is incorrect. Please check and try again.")
            return 
        
        # 对上传图片的大小和分辨率做出限制
        '''
        check_passport：
        原则上 上传图片不超过 3M 和1600px * 1600px
        倍率不超过4x
        '''
        await ctx.defer()
        info, content, is_vaild = await helpers.check_passport(imageurl)
        # 检查失败，返回失败内容，提醒user重试
        if is_vaild == False:
            await ctx.respond(info)
            return 
        # 输入图片文件名
        result = info

        file = discord.File(io.BytesIO(content),result)
        await ctx.respond(file=file, view=helpers.UIFormat(ctx, imageurl, model, scale, result))

       
# bot.add_cog(A1D(bot))
A1D(bot)
bot.run(config["bot_token"])
