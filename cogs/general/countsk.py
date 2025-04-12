import discord
import re
from discord.ext import commands
from datetime import datetime

class CountImages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def countsk(self, ctx, member: discord.Member = None, start_date: str = None, end_date: str = None):
        """Đếm số hình ảnh của một người trong kênh theo tuần (có chọn ngày bắt đầu và kết thúc)"""
        if member is None:
            await ctx.send("⚠ Vui lòng đề cập đến một người dùng! (VD: !countsk @Zenka 2024-03-01 2024-03-07)")
            return

        # Kiểm tra ngày hợp lệ
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
            end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        except ValueError:
            await ctx.send("⚠ Định dạng ngày không hợp lệ! Vui lòng nhập theo dạng YYYY-MM-DD.")
            return

        count = 0  # Số lượng hình ảnh
        image_extensions = ('png', 'jpg', 'jpeg', 'gif', 'webp')
        image_url_regex = re.compile(r"(https?://\S+\.(?:png|jpg|jpeg|gif|webp))")

        async for message in ctx.channel.history(limit=5000, oldest_first=False):  
            if message.author == member:
                if start and message.created_at < start:
                    break  # Dừng khi đã quá phạm vi ngày

                if end and message.created_at > end:
                    continue  # Bỏ qua tin nhắn ngoài phạm vi

                count += len([att for att in message.attachments if att.filename.lower().endswith(image_extensions)])
                count += len([embed for embed in message.embeds if embed.thumbnail and embed.thumbnail.url.lower().endswith(image_extensions)])
                count += len(image_url_regex.findall(message.content))

        # Gửi kết quả
        embed = discord.Embed(
            title="📸 Kết Quả Đếm Hình Ảnh Sự Kiện",
            description=f"🔍 **Kênh:** {ctx.channel.mention}\n👤 **Người dùng:** {member.mention}\n📅 **Khoảng thời gian:** {start_date} - {end_date}\n📷 **Tổng số hình ảnh:** {count}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CountImages(bot))
