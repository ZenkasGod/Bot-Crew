from datetime import datetime, timedelta
import pytz  # Thêm thư viện pytz để xử lý múi giờ
import discord
import re
from discord.ext import commands

class CountImages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_date(self, date_str):
        """Hỗ trợ định dạng ngày DD/MM/YYYY hoặc YYYY/MM/DD"""
        for fmt in ("%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    @commands.command()
    async def countsk(self, ctx, member: discord.Member = None, start_date: str = None, end_date: str = None):
        """Đếm số hình ảnh của một người trong kênh theo khoảng thời gian (hỗ trợ định dạng DD/MM/YYYY hoặc YYYY/MM/DD)"""
        
        # Kiểm tra nếu người dùng không được chỉ định
        if member is None:
            await ctx.send("⚠ Vui lòng đề cập đến một người dùng! (VD: !countsk @Zenka 2024-03-01 2024-03-07)")
            return
        
        # Kiểm tra và phân tích ngày bắt đầu và kết thúc
        start = self.parse_date(start_date) if start_date else None
        end = self.parse_date(end_date) if end_date else None

        # Kiểm tra nếu ngày tháng không hợp lệ
        if (start_date and not start) or (end_date and not end):
            await ctx.send("⚠ Định dạng ngày không hợp lệ! Vui lòng nhập theo dạng DD/MM/YYYY hoặc YYYY/MM/DD.")
            return
        
        # Chuyển đổi start và end sang datetime có múi giờ UTC
        if start:
            start = pytz.utc.localize(start)  # Chuyển đổi start sang thời gian có múi giờ UTC
        if end:
            end = pytz.utc.localize(end)  # Chuyển đổi end sang thời gian có múi giờ UTC

        # Nếu ngày bắt đầu và kết thúc giống nhau, tính khoảng thời gian trong ngày đó
        if start == end:
            end = start + timedelta(days=1) - timedelta(seconds=1)

        count = 0
        image_extensions = ('png', 'jpg', 'jpeg', 'gif', 'webp')
        image_url_regex = re.compile(r"(https?://\S+\.(?:png|jpg|jpeg|gif|webp))")

        try:
            async for message in ctx.channel.history(limit=5000, oldest_first=False):
                if message.author == member:
                    # So sánh với thời gian UTC của message
                    if start and message.created_at < start:
                        break
                    if end and message.created_at > end:
                        continue

                    # Đếm hình ảnh
                    count += len([att for att in message.attachments if att.filename.lower().endswith(image_extensions)])
                    count += len([embed for embed in message.embeds if embed.thumbnail and embed.thumbnail.url.lower().endswith(image_extensions)])
                    count += len(image_url_regex.findall(message.content))

            # Tạo và gửi kết quả
            embed = discord.Embed(
                title="📸 Kết Quả Đếm Hình Ảnh Sự Kiện",
                description=f"🔍 **Kênh:** {ctx.channel.mention}\n👤 **Người dùng:** {member.mention}\n📅 **Khoảng thời gian:** {start_date} - {end_date}\n📷 **Tổng số hình ảnh:** {count}",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"⚠ Đã xảy ra lỗi khi thực hiện lệnh: {str(e)}")
            print(f"Error: {str(e)}")  # In lỗi ra console để debug thêm nếu cần

async def setup(bot):
    await bot.add_cog(CountImages(bot))
