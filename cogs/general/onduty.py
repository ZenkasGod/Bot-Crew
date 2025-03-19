import discord
from discord.ext import commands
import time
import json
import os
from datetime import datetime

DATA_FOLDER = "data_onduty"  # Thư mục lưu file dữ liệu

class OnDuty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_duty_users = {}
        self.ensure_data_folder()
        self.load_data()

    def ensure_data_folder(self):
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

    def get_data_file(self):
        current_month = datetime.now().strftime("%Y-%m")
        return os.path.join(DATA_FOLDER, f"onduty_thang_{current_month}.json")

    def load_data(self):
        data_file = self.get_data_file()
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                self.duty_data = json.load(f)
        else:
            self.duty_data = {}

    def save_data(self):
        data_file = self.get_data_file()
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(self.duty_data, f, indent=4)

    @commands.command()
    async def onduty(self, ctx, *, mission: str = None):
        """Lệnh vào ca trực với nhiệm vụ"""
        if mission is None:
            await ctx.send(f"🚨 **{ctx.author.mention}, bạn chưa nhập nhiệm vụ!**\nVui lòng nhập: `!onduty <Nhiệm vụ>`")
            return

        start_time = time.time()
        user_id = str(ctx.author.id)
        today_date = datetime.now().strftime("%Y-%m-%d")

        if user_id in self.active_duty_users:
            await ctx.send(f"⚠ **{ctx.author.mention}, bạn đã vào ca trực rồi!**\nDùng `!offduty` để kết thúc trước khi vào nhiệm vụ khác.")
            return

        self.active_duty_users[user_id] = {"start_time": start_time, "mission": mission}

        if user_id not in self.duty_data:
            self.duty_data[user_id] = {"today": 0, "month": 0, "last_date": today_date, "missions": {}}
        else:
            if self.duty_data[user_id]["last_date"] != today_date:
                self.duty_data[user_id]["missions"] = {}
            self.duty_data[user_id]["last_date"] = today_date

        # Cập nhật số lần nhiệm vụ
        if mission not in self.duty_data[user_id]["missions"]:
            self.duty_data[user_id]["missions"][mission] = 1
        else:
            self.duty_data[user_id]["missions"][mission] += 1

        self.save_data()

        # Hiển thị danh sách nhiệm vụ trong ngày
        missions_today = self.duty_data[user_id]["missions"]
        mission_list = []
        for task, count in missions_today.items():
            if count > 1:
                mission_list.append(f"`{task}` (x{count})")
            else:
                mission_list.append(f"`{task}`")

        embed = discord.Embed(
            title="✅ ON DUTY - Bắt Đầu Ca Trực",
            description=f"🚨 **{ctx.author.mention} đã vào ca trực!**",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.add_field(name="📌 Nhiệm vụ hiện tại", value=f"**{mission}**", inline=False)
        embed.add_field(name="📋 Nhiệm vụ trong ngày", value=", ".join(mission_list), inline=False)
        embed.set_footer(text="✅ Cảm ơn bạn và làm việc vui vẻ!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OnDuty(bot))
