import discord
import re
from discord.ext import commands
from datetime import datetime, timedelta

class CountImages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def countsk(self, ctx, *args):
        """Đếm số hình ảnh theo ngày hoặc khoảng ngày (dd/mm/yyyy) của một người trong kênh"""

        # Kiểm tra đủ số lượng tham số
        if len(args) < 2:
            await ctx.send("⚠ Vui lòng nhập ngày và đề cập người dùng! Ví dụ:\n"
                           "`!countsk 12/04/2025 @Zenka` hoặc `!countsk 10/04/2025 12/04/2025 @Zenka`")
            return

        try:
            # Trường hợp chỉ có 1 ngày và 1 người dùng
            if len(args) == 2:
                start_date = end_date = datetime.strptime(args[0], "%d/%m/%Y")
                member = ctx.message.mentions[0]
            # Trường hợp có 2 ngày và 1 người dùng
            elif len(args) == 3:
                start_date = datetime.strptime(args[0], "%d/%m/%Y")
                end_date = datetime.strptime(args[1], "%d/%m/%Y")
                member = ctx.message.mentions[0]
            else:
                await ctx.send("⚠ Cú pháp không đúng! Dùng `!countsk dd/mm/yyyy [dd/mm/yyyy] @user`")
                return

        except (ValueError, IndexError):
            await ctx.send("⚠ Lỗi định dạng ngày (dd/mm/yyyy) hoặc không tìm thấy người dùng!")
            return

        # Thời gian bắt đầu từ 00:00:00 và kết thúc đến 23:59:59 của ngày cuối
        start = start_date
        end = end_date + timedelta(days=1) - timedelta(seconds=1)

        count = 0
        image_extensions = ('png', 'jpg', 'jpeg', 'gif', 'webp')
        image_url_regex = re.compile(r"(https?://\S+\.(?:png|jpg|jpeg|gif|webp))")

        async for message in ctx.channel.history(limit=5000, oldest_first=False):
            if message.author == member and start <= message.created_at <= end:
                count += len([att for att in message.attachments if att.filename.lower().endswith(image_extensions)])
                count += len([embed for embed in message.embeds if embed.thumbnail and embed.thumbnail.url.lower().endswith(image_extensions)])
                count += len(image_url_regex.findall(message.content))

        embed = discord.Embed(
            title="📸 Kết Quả Đếm Hình Ảnh Sự Kiện",
            description=f"🔍 **Kênh:** {ctx.channel.mention}\n👤 **Người dùng:** {member.mention}\n📅 **Khoảng thời gian:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}\n📷 **Tổng số hình ảnh:** {count}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CountImages(bot))
