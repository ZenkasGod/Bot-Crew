import discord
import re
from discord.ext import commands
from datetime import datetime

class CountImages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_date(self, date_str):
        """Hỗ trợ nhiều định dạng ngày"""
        for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    @commands.command()
    async def countsk(self, ctx, member: discord.Member = None, start_date: str = None, end_date: str = None):
        """Đếm số hình ảnh của một người trong kênh theo khoảng thời gian (hỗ trợ định dạng YYYY-MM-DD và YYYY/MM/DD)"""
        if member is None:
            await ctx.send("⚠ Vui lòng đề cập đến một người dùng! (VD: !countsk @Zenka 2024-03-01 2024-03-07)")
            return

        # Parse ngày bắt đầu và kết thúc
        start = self.parse_date(start_date) if start_date else None
        end = self.parse_date(end_date) if end_date else None

        if (start_date and not start) or (end_date and not end):
            await ctx.send("⚠ Định dạng ngày không hợp lệ! Vui lòng nhập theo dạng DD/MM/YYYY hoặc YYYY/MM/DD.")
            return

        # Cập nhật kết quả để hiển thị ngày theo định dạng DD/MM/YYYY
        count = 0
        image_extensions = ('png', 'jpg', 'jpeg', 'gif', 'webp')
        image_url_regex = re.compile(r"(https?://\S+\.(?:png|jpg|jpeg|gif|webp))")

        async for message in ctx.channel.history(limit=5000, oldest_first=False):
            if message.author == member:
                if start and message.created_at < start:
                    break
                if end and message.created_at > end:
                    continue

                count += len([att for att in message.attachments if att.filename.lower().endswith(image_extensions)])
                count += len([embed for embed in message.embeds if embed.thumbnail and embed.thumbnail.url.lower().endswith(image_extensions)])
                count += len(image_url_regex.findall(message.content))

        # Hiển thị kết quả với định dạng ngày DD/MM/YYYY
        embed = discord.Embed(
            title="📸 Kết Quả Đếm Hình Ảnh Sự Kiện",
            description=f"🔍 **Kênh:** {ctx.channel.mention}\n👤 **Người dùng:** {member.mention}\n📅 **Khoảng thời gian:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}\n📷 **Tổng số hình ảnh:** {count}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CountImages(bot))
