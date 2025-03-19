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
        self.ensure_data_folder()  # Kiểm tra và tạo thư mục nếu chưa có
        self.load_data()

    def ensure_data_folder(self):
        """Đảm bảo thư mục lưu dữ liệu tồn tại"""
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

    def get_data_file(self):
        """Trả về đường dẫn file JSON theo tháng hiện tại"""
        current_month = datetime.now().strftime("%Y-%m")
        return os.path.join(DATA_FOLDER, f"onduty_thang_{current_month}.json")

    def load_data(self):
        """Load dữ liệu từ file JSON theo tháng hiện tại"""
        data_file = self.get_data_file()
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                self.duty_data = json.load(f)
        else:
            self.duty_data = {}

    def save_data(self):
        """Lưu dữ liệu vào file JSON theo tháng hiện tại"""
        data_file = self.get_data_file()
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(self.duty_data, f, indent=4)

    @commands.command()
    async def onduty(self, ctx, vehicle_plate: str = None):
        """Lệnh vào ca trực với biển số xe"""
        if vehicle_plate is None:
            await ctx.send(f"🚨 **{ctx.author.mention}, bạn chưa nhập biển số xe!**\nVui lòng nhập: `!onduty <Biển số xe>`")
            return

        start_time = time.time()
        user_id = str(ctx.author.id)
        today_date = datetime.now().strftime("%Y-%m-%d")

        if user_id in self.active_duty_users:
            await ctx.send(f"⚠ **{ctx.author.mention}, bạn đã vào ca trực rồi!**\nDùng `!offduty` để kết thúc trước khi vào xe khác.")
            return

        self.active_duty_users[user_id] = {"start_time": start_time, "vehicle": vehicle_plate}

        if user_id not in self.duty_data:
            self.duty_data[user_id] = {"today": 0, "month": 0, "last_date": today_date, "vehicles": [vehicle_plate]}
        else:
            # Nếu là ngày mới, reset danh sách xe của ngày
            if self.duty_data[user_id]["last_date"] != today_date:
                self.duty_data[user_id]["vehicles"] = []

            self.duty_data[user_id]["last_date"] = today_date

            # Nếu xe chưa có trong danh sách hôm nay, thêm vào
            if vehicle_plate not in self.duty_data[user_id]["vehicles"]:
                self.duty_data[user_id]["vehicles"].append(vehicle_plate)

        self.save_data()

        embed = discord.Embed(
            title="✅ ON DUTY - Bắt Đầu Ca Trực",
            description=f"🚨 **{ctx.author.mention} đã vào ca trực!**",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.add_field(name="🚑 Xe sử dụng", value=f"**🚔 Biển Số Xe `{vehicle_plate}` 🚔**", inline=False)
        embed.add_field(
            name="📋 Danh sách xe hôm nay",
            value=", ".join(f"`{plate}`" for plate in self.duty_data[user_id]["vehicles"]),
            inline=False
        )
        embed.add_field(
            name="⚠ Lưu ý:",
            value="Nhớ **offduty** khi thoát game và cất xe.\nOnDuty **không AFK**!",
            inline=False
        )
        embed.set_footer(text="✅ Cảm ơn bạn và làm việc vui vẻ!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OnDuty(bot))
