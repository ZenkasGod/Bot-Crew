import discord
from discord.ext import commands
import time
import json
import os
from datetime import datetime

DATA_FOLDER = "data_onduty"

class OffDuty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_data_file(self):
        """Trả về đường dẫn file JSON theo tháng hiện tại"""
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        current_month = datetime.now().strftime("%Y-%m")
        return os.path.join(DATA_FOLDER, f"onduty_thang_{current_month}.json")

    @commands.command()
    async def offduty(self, ctx):
        """Lệnh rời ca trực"""
        cog = self.bot.get_cog("OnDuty")
        if not cog:
            await ctx.send("⚠ **Không thể rời ca trực vì hệ thống gặp lỗi.**")
            return

        if str(ctx.author.id) not in cog.active_duty_users:
            await ctx.send(f"⚠ **{ctx.author.mention}, bạn chưa vào ca trực!**\nDùng `!onduty <Biển số xe>` trước.")
            return

        # Tính toán thời gian on duty
        start_time = cog.active_duty_users.pop(str(ctx.author.id))["start_time"]
        total_seconds = int(time.time() - start_time)

        user_id = str(ctx.author.id)
        today_date = datetime.now().strftime("%Y-%m-%d")
        data_file = self.get_data_file()

        # Load dữ liệu từ file JSON
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                duty_data = json.load(f)
        else:
            duty_data = {}

        # Nếu chưa có dữ liệu, khởi tạo
        if user_id not in duty_data:
            duty_data[user_id] = {"today": 0, "month": 0, "last_date": today_date}

        # Reset nếu qua ngày mới
        if duty_data[user_id]["last_date"] != today_date:
            duty_data[user_id]["today"] = 0

        # Cập nhật dữ liệu on duty
        duty_data[user_id]["today"] += total_seconds
        duty_data[user_id]["month"] += total_seconds
        duty_data[user_id]["last_date"] = today_date

        # Lưu lại vào file
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(duty_data, f, indent=4, ensure_ascii=False)

        def format_time(seconds):
            """Chuyển đổi thời gian từ giây sang giờ và phút (luôn hiển thị đủ 2 thành phần)"""
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"**{int(hours)} giờ {int(minutes)} phút**"

        # Lấy thời gian ca hiện tại, hôm nay và tháng này
        ca_hien_tai = format_time(total_seconds)
        hom_nay = format_time(duty_data[user_id]["today"])
        thang_nay = format_time(duty_data[user_id]["month"])

        # Gửi embed thông báo
        embed = discord.Embed(
            title="🔴 OFF DUTY - Kết Thúc Ca Trực",
            description=f"❌ **{ctx.author.display_name}** đã kết thúc ca trực!",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.add_field(name="⏳ Thời gian ca này:", value=ca_hien_tai, inline=False)
        embed.add_field(name="📆 Hôm nay đã on duty:", value=hom_nay, inline=False)
        embed.add_field(name="📅 Tháng này đã on duty:", value=thang_nay, inline=False)
        embed.set_footer(text="✅ Cảm ơn bạn đã làm việc! Chúc bạn 1 ngày tốt lành nhớ giữ gìn sức khỏe")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OffDuty(bot))
