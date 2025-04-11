import os
import discord
from discord.ext import commands, tasks
import json
from dotenv import load_dotenv
import sys
import itertools
import datetime
import aiohttp
import logging
import asyncio
import pytz


logging.basicConfig(level=logging.INFO)

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ Lỗi: DISCORD_TOKEN không tồn tại. Hãy kiểm tra biến môi trường trên Railway hoặc file .env!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")
VIOLATION_LOG = os.path.join(BASE_DIR, "violations.json")
LOG_FILE = os.path.join(BASE_DIR, "unauthorized_servers.log")

# Thiết lập múi giờ Việt Nam
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

# Cập nhật thời gian đúng múi giờ Việt Nam
def get_vn_time():
    return datetime.datetime.now(VN_TZ)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"❌ Không tìm thấy file cấu hình: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
# Hàm lưu config
def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        
config = load_config()
PREFIX = config.get("prefix", "!")
if not PREFIX:
    raise ValueError("❌ Lỗi: Không tìm thấy `prefix` trong config.json! Kiểm tra lại cấu hình.")
    
ALLOWED_GUILDS = config.get("allowed_guilds", [])
if not isinstance(ALLOWED_GUILDS, list) or not all(isinstance(i, int) for i in ALLOWED_GUILDS):
    raise ValueError("❌ Lỗi: `allowed_guilds` trong config.json phải là một danh sách ID máy chủ hợp lệ!")
 

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, case_insensitive=True)

status_cycle = itertools.cycle([
    discord.Game("🚑 Sự Kiện 24/7!"),
    discord.Game("💙 Hỗ trợ Crews Tổ Chức hết mình!"),
    discord.Game("🏥 Tham gia sự kiện hãy 1 cách công bằng!"),
    discord.Game("🚨 Combat - Hãy gọi tôi!"),
    discord.Game("✨ Luôn yêu đời, luôn giúp đỡ!"),
    discord.Game("📞 Alo - Bạn cần giúp gì?"),
])

@tasks.loop(seconds=60)
async def change_status():
    try:
        await bot.change_presence(activity=next(status_cycle))
    except Exception as e:
        print(f"⚠️ Lỗi khi đổi trạng thái: {e}")

@change_status.before_loop
async def before_status_change():
    await bot.wait_until_ready()

@bot.command()
@commands.is_owner()  # Chỉ chủ sở hữu bot mới có thể chạy lệnh này
async def addguild(ctx, guild_id: int):
    config = load_config()

    if "allowed_guilds" not in config:
        config["allowed_guilds"] = []

    if guild_id in config["allowed_guilds"]:
        await ctx.send(f"✅ Máy chủ `{guild_id}` đã có trong danh sách hợp lệ!")
        return

    config["allowed_guilds"].append(guild_id)
    save_config(config)
    
    await ctx.send(f"✅ Đã thêm máy chủ `{guild_id}` vào danh sách hợp lệ!")

@addguild.error
async def addguild_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("❌ Chỉ **chủ sở hữu bot** mới có thể sử dụng lệnh này!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Vui lòng nhập **ID máy chủ** cần thêm! Ví dụ: `!addguild 123456789012345678`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ ID máy chủ phải là **số**!")
@bot.event
async def on_ready():
    if not hasattr(bot, "session") or bot.session.closed:
        bot.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))

    print(f"✅ Bot đã online với tên: {bot.user}")
    print(f"🔹 Prefix: {PREFIX}")
    print(f"🔹 Các cogs đã load: {list(bot.cogs.keys())}")
    print(f"🔹 Đang kết nối với {len(bot.guilds)} máy chủ!")
    
    for guild in bot.guilds:
        if guild.id not in ALLOWED_GUILDS:
            await handle_unauthorized_guild(guild)
    

    # 🔥 Gửi tin nhắn thông báo vào hệ thống
    message_sent = False
    for guild in bot.guilds:
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            try:
                embed = discord.Embed(
                    title="🚀 Bot đã khởi động thành công!",
                    description=f"✅ **{bot.user.name}** đã hoạt động. Dùng `{PREFIX}help` để xem các lệnh có sẵn.",
                    color=discord.Color.green()
                )
                await guild.system_channel.send(embed=embed)
                message_sent = True
            except:
                pass

    if not message_sent:
        print("⚠️ Không tìm thấy kênh hợp lệ để gửi thông báo!")

    change_status.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    print(f"[DEBUG] Nhận tin nhắn: {message.content} từ {message.author}")
    await bot.process_commands(message)

@bot.event
async def on_disconnect():
    print("🔴 Bot đã mất kết nối!")

@bot.event
async def on_resumed():
    print("🔄 Bot đã kết nối lại sau khi bị gián đoạn!")

async def load_extensions():
    """Tự động load tất cả cogs và events"""
    for folder in ["cogs", "events"]:
        dir_path = os.path.join(BASE_DIR, folder)
        
        if not os.path.exists(dir_path):
            print(f"⚠️ Thư mục `{folder}` không tồn tại! Bỏ qua...")
            continue

        for root, _, files in os.walk(dir_path):
            for filename in files:
                if filename.endswith(".py") and not filename.startswith("_"):
                    module_name = os.path.relpath(os.path.join(root, filename), BASE_DIR)
                    module_name = module_name.replace(os.sep, ".")[:-3]  # Chuyển đường dẫn thành module importable
                    
                    try:
                        await bot.load_extension(module_name)
                        print(f"✅ Loaded: {module_name}")
                    except Exception as e:
                        print(f"❌ Không thể load `{module_name}`: {e}")

@bot.event
async def on_guild_join(guild):
    if guild.id not in ALLOWED_GUILDS:
        await handle_unauthorized_guild(guild)

async def handle_unauthorized_guild(guild):
    log_unauthorized_guild(guild)
    save_violation(guild)

    warning_image_url = "https://cdn.discordapp.com/attachments/1284562100345372784/1354431577769377892/f8f95e8b41324e28587154ce962ab75e.jpg?ex=67e54434&is=67e3f2b4&hm=a3287172b56862a51c4b0623dc18e2cecd27316508790d63e9e97fd50b6c2849&"  # Link ảnh cảnh báo

    # Gửi tin nhắn cảnh báo trên kênh hệ thống
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        embed = discord.Embed(
            title="❌ Máy chủ không hợp lệ!",
            description="Bot này chỉ hoạt động trên **máy chủ chính thức**! 🚨\nLiên hệ: **Mr Leonard (Whiterk)**\nTạm biệt! 👋",
            color=discord.Color.red()
        )
        embed.set_image(url=warning_image_url)

        try:
            await guild.system_channel.send(embed=embed)
            await asyncio.sleep(3)  # Chờ 3 giây để đảm bảo tin nhắn được gửi trước khi rời khỏi server
        except:
            print(f"⚠️ Không thể gửi tin nhắn trong server: {guild.name}")

    # Gửi tin nhắn riêng cho chủ sở hữu
    owner = await bot.fetch_user(guild.owner_id)
    if owner:
        embed_dm = discord.Embed(
            title="🚫 Bạn đã bị cấm sử dụng bot EMS!",
            description=f"**Máy chủ `{guild.name}` không hợp lệ.**\nVui lòng liên hệ **Mr Leonard** hoặc **Discord: Whiterk** để biết thêm chi tiết.",
            color=discord.Color.red()
        )
        embed_dm.set_image(url=warning_image_url)

        try:
            await owner.send(embed=embed_dm)
        except:
            print(f"⚠️ Không thể gửi tin nhắn riêng cho chủ sở hữu của {guild.name} ({guild.owner_id})")

    # Rời khỏi máy chủ sau khi đã gửi thông báo
    await guild.leave()
    print(f"🚨 Bot đã rời khỏi máy chủ không hợp lệ: {guild.name} ({guild.id})")


def log_unauthorized_guild(guild):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        log_entry = (
            f"🛑 [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n"
            f"🔹 Máy chủ: {guild.name} (ID: {guild.id})\n"
            f"🔸 Chủ sở hữu: {guild.owner} (ID: {guild.owner_id})\n"
            f"👥 Thành viên: {guild.member_count}\n"
            f"{'-'*40}\n"
        )
        f.write(log_entry)

def save_violation(guild):
    data = {}
    if os.path.exists(VIOLATION_LOG):
        with open(VIOLATION_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    data[str(guild.id)] = {
        "name": guild.name,
        "owner_id": guild.owner_id,
        "member_count": guild.member_count,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(VIOLATION_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    async def main():
        try:
            await load_extensions()
            await bot.start(TOKEN, reconnect=True)
        except discord.LoginFailure:
            print("❌ Lỗi: Token không hợp lệ! Hãy kiểm tra lại biến môi trường hoặc file `.env`")
        except Exception as e:
            print(f"❌ Lỗi khi khởi động bot: {e}")
    asyncio.run(main())
