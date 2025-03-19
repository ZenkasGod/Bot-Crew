import discord
from discord.ext import commands
import json
import os
from datetime import datetime

DATA_FOLDER = "data_onduty"  # Thư mục lưu dữ liệu OnDuty

class CheckPlate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_data_file(self):
        """Trả về tên file JSON theo tháng hiện tại"""
        current_month = datetime.now().strftime("%Y-%m")
        return os.path.join(DATA_FOLDER, f"onduty_thang_{current_month}.json")

    def load_data(self):
        """Load dữ liệu từ file JSON của tháng hiện tại"""
        data_file = self.get_data_file()
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @commands.command()
    async def checkpn(self, ctx, vehicle_plate: str = None):
        """Kiểm tra biển số xe đã được ai sử dụng gần nhất khi OnDuty"""
        if vehicle_plate is None:
            await ctx.send(f"⚠ **{ctx.author.mention}, vui lòng nhập biển số xe cần kiểm tra!**\nVí dụ: `!checkpn 51A-12345`")
            return

        duty_data = self.load_data()
        found_user = None

        for user_id, data in duty_data.items():
            vehicles = data.get("vehicles", [])  # Lấy danh sách vehicles (tránh lỗi KeyError)
            if vehicle_plate in vehicles:
                found_user = user_id
                break  # Thoát vòng lặp nếu tìm thấy

        if found_user:
            guild = ctx.guild  # Máy chủ hiện tại
            user = guild.get_member(int(found_user)) or await self.bot.fetch_user(int(found_user))
            display_name = user.display_name if isinstance(user, discord.Member) else user.name

            embed = discord.Embed(
                title="🔍 TRA CỨU BIỂN SỐ XE",
                description=f"🚔 Biển số xe `{vehicle_plate}` gần đây được sử dụng bởi: **{display_name}**",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ **Không tìm thấy ai đã sử dụng biển số xe `{vehicle_plate}` gần đây.**")

async def setup(bot):
    await bot.add_cog(CheckPlate(bot))
