import discord
from discord.ext import commands
import json
import os
from datetime import datetime

DATA_FOLDER = "data_onduty"

class MyInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_folder()

    def ensure_data_folder(self):
        """Tạo thư mục lưu dữ liệu nếu chưa tồn tại"""
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

    def get_onduty_files(self):
        """Lấy danh sách tất cả các file dữ liệu trực"""
        return sorted(
            [f for f in os.listdir(DATA_FOLDER) if f.startswith("onduty_thang_") and f.endswith(".json")]
        )

    def get_total_work_time(self, user_id):
        """Tính tổng thời gian làm việc từ lịch sử"""
        total_minutes = 0
        start_date = None  # Ngày đầu tiên có dữ liệu trực

        for file in self.get_onduty_files():
            file_path = os.path.join(DATA_FOLDER, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if user_id in data and "history" in data[user_id]:
                    for date in sorted(data[user_id]["history"].keys()):
                        if start_date is None:
                            start_date = date  # Ghi nhận ngày làm việc đầu tiên

                        day_data = data[user_id]["history"].get(date, {})
                        total_minutes += day_data.get("hours", 0) * 60 + day_data.get("minutes", 0)
            
            except (json.JSONDecodeError, FileNotFoundError):
                print(f"[⚠ ERROR] Lỗi đọc file: {file_path}")
                continue

        total_hours = total_minutes // 60
        total_minutes %= 60
        return total_hours, total_minutes, start_date

    @commands.command()
    async def myinfo(self, ctx):
        """Hiển thị thông tin cá nhân của người dùng"""
        user = ctx.author
        user_id = str(user.id)
        nickname = user.display_name  # Biệt danh trên server
        highest_role = user.top_role.name if user.top_role != ctx.guild.default_role else "Không có"  # Role cao nhất
        join_date = user.joined_at.strftime("%d-%m-%Y") if user.joined_at else "Không rõ"  # Ngày vào server

        # Lấy tổng số giờ làm việc từ lịch sử
        total_hours, total_minutes, first_work_date = self.get_total_work_time(user_id)

        embed = discord.Embed(
            title=f"👤 {nickname}",
            description="🌟 **Thông tin cá nhân EMS**",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=user.avatar.url)  # Ảnh đại diện người dùng

        embed.add_field(name="🛡 **Chức vụ**", value=f"```{highest_role}```", inline=False)
        embed.add_field(name="📅 **Ngày vào**", value=f"🗓 `{join_date}`", inline=True)

        if first_work_date:
            embed.add_field(name="📆 **Ngày bắt đầu trực**", value=f"🔰 `{first_work_date}`", inline=True)

        embed.add_field(name="⏳ **Kinh nghiệm làm việc**", value=f"⏱ `{total_hours} giờ {total_minutes} phút`", inline=False)

        embed.set_footer(text="💙 Cảm ơn những đóng góp của bạn cho EMS.", icon_url="https://cdn-icons-png.flaticon.com/512/833/833472.png")

        await ctx.send(embed=embed)

async def setup(bot):
    """Nạp cog vào bot"""
    await bot.add_cog(MyInfo(bot))
