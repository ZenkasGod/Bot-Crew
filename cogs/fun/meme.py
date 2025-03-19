import discord
from discord.ext import commands

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meme(self, ctx):
        await ctx.send("Đây là một meme!")

async def setup(bot):
    await bot.add_cog(Meme(bot))  # Quan trọng: phải có await khi dùng bot.load_extension()
