import discord
from discord.ext import commands
from datetime import datetime

class CheckDuty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="checkduty")
    async def check_duty(self, ctx):
        """Kiểm tra danh sách những người đang on duty"""
        cog = self.bot.get_cog("OnDuty")
        if not cog or not hasattr(cog, "active_duty_users") or not cog.active_duty_users:
            await ctx.send("📢 **Hiện tại không có ai đang on duty.**")
            return

        embed = discord.Embed(title="📜 DANH SÁCH NHÂN VIÊN EMS ĐANG ON DUTY 📜", color=discord.Color.blue())
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1343515357171683407/1349998300626948156/fd487a8315c2d8d6aa6c7ebb2d74c1b8.jpg")

        for index, (user_id, data) in enumerate(cog.active_duty_users.items(), start=1):
            user = ctx.guild.get_member(int(user_id))
            username = user.display_name if user else f"Người dùng không xác định (`{user_id}`)"

            vehicle_info = data.get('vehicle', 'Không có phương tiện')
            location = data.get('location', 'Không rõ vị trí')
            speed = data.get('speed', 0)

            # Lấy thời gian bắt đầu On Duty
            timestamp = data.get("start_time", datetime.now().timestamp())
            start_time = datetime.fromtimestamp(float(timestamp)).strftime("%H:%M:%S")

            # Kiểm tra trạng thái hoạt động
            activity_status = "❌ **Không hoạt động**"
            gta_info = ""

            if user and user.activities:
                for act in user.activities:
                    if isinstance(act, discord.Game):
                        activity_status = f"🎮 **Chơi game:** `{act.name}`"
                        if "GTA5VN.NET" in act.name.upper():
                            gta_info = f"🗺 **{username}** đang lái xe **{vehicle_info}** tại **{location}** tốc độ **{speed}Km/h**"
                        break
                    elif isinstance(act, discord.Streaming):
                        activity_status = f"📺 **Streaming:** `{act.name}`"
                        break
                    elif isinstance(act, discord.Activity):
                        activity_status = f"🔹 **Hoạt động:** `{act.name}`"
                        break

            # Hiển thị thông tin nhân viên
            embed.add_field(
                name=f"{index}. 👤 **{username}**",
                value=f"⏳ **Bắt đầu Ca:** `{start_time}`\n🚑 **Phương tiện:** `{vehicle_info}`\n📍 **Vị trí:** `{location}`\n🏎 **Tốc độ:** `{speed} Km/h`\n🟢 **Vị Trí Hoạt Động:** {activity_status}\n{gta_info if gta_info else ''}\n—",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CheckDuty(bot))
