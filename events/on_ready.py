from discord.ext import commands

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot {self.bot.user} đã hoạt động và chuẩn bị tham gia công tác tại GTA5VN - LOS SANTOS!")

def setup(bot):
    bot.add_cog(OnReady(bot))
