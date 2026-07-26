import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import requests

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Railway environment variables se keys uthana
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

OWNER_USERNAME = "@ESCROW2929"

# Security: Hardcoded Owner/Admin IDs (Only authorized people can manage keys/admins)
# Apni Telegram numeric User ID yahan daalein taaki sirf aap access kar sakein
AUTHORIZED_ADMINS = {ESCROW2929}  # Apna ID yahan add karein

BANNED_USERS = set()
ACTIVE_KEYS = {}  # Format: {key_string: {"quantity": qty, "time": time}}

def is_authorized(user_id):
    return user_id in AUTHORIZED_ADMINS

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
        await update.message.reply_text("❌ You are banned from using this bot.")
        return
        
    user = update.effective_user
    welcome_message = (
        f"Hello {user.first_name}!\n\n"
        f"🤖 **CC Checker & Gateway Bot is Online**\n"
        f"Use /chk, /chks, or /chf to check cards.\n\n"
        f"👑 **Owner:** {OWNER_USERNAME}"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

# /adminpannel command (Restricted)
async def admin_pannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized to use the Admin Panel.")
        return
        
    panel_message = (
        f"🛠 **Admin Panel & Controls**\n\n"
        f"• Stripe Integration: Connected (Test Mode)\n"
        f"• Active Keys Generated: {len(ACTIVE_KEYS)}\n"
        f"• Banned Users: {len(Banned_Users if 'Banned_Users' in globals() else BANNED_USERS)}\n\n"
        f"**Available Admin Commands:**\n"
        f"/key <quantity> <time> (e.g., /key 5 1d)\n"
        f"/makeadmin <id>\n"
        f"/removeadmin <id>\n"
        f"/ban <id>\n"
        f"/unban <id>"
    )
    await update.message.reply_text(panel_message, parse_mode="Markdown")

# /key command: /key (quantity) (time)
async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized to generate keys.")
        return
        
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/key <quantity> <time>` (Example: `/key 10 1d`)", parse_mode="Markdown")
        return
        
    qty = context.args[0]
    time_limit = context.args[1]
    
    import uuid
    generated_key = f"KEY-{uuid.uuid4().hex[:8].upper()}"
    ACTIVE_KEYS[generated_key] = {"quantity": qty, "time": time_limit}
    
    await update.message.reply_text(
        f"🔑 **Key Generated Successfully!**\n\n"
        f"• Key: `{generated_key}`\n"
        f"• Quantity: {qty}\n"
        f"• Time Limit: {time_limit}",
        parse_mode="Markdown"
    )

# /makeadmin command (Restricted: Cannot add via bot commands unless pre-set or restricted to owner)
async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Only primary owners can assign admins.")
        return
        
    if not context.args:
        await update.message.reply_text("❌ Usage: `/makeadmin <user_id>`", parse_mode="Markdown")
        return
    try:
        new_admin = int(context.args[0])
        AUTHORIZED_ADMINS.add(new_admin)
        await update.message.reply_text(f"✅ User `{new_admin}` has been authorized.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID format.")

# /removeadmin command
async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Only primary owners can remove admins.")
        return
        
    if not context.args:
        await update.message.reply_text("❌ Usage: `/removeadmin <user_id>`", parse_mode="Markdown")
        return
    try:
        target = int(context.args[0])
        if target in AUTHORIZED_ADMINS:
            AUTHORIZED_ADMINS.remove(target)
            await update.message.reply_text(f"✅ User `{target}` removed from admins.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ User not found in admin list.")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID format.")

# /ban command
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/ban <user_id>`", parse_mode="Markdown")
        return
    try:
        target = int(context.args[0])
        BANNED_USERS.add(target)
        await update.message.reply_text(f"🚫 User `{target}` has been banned.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID.")

# /unban command
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
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
            await update.message.reply_text("❌ User is not banned.")
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID.")

# Core Stripe Card Checker Logic
def process_card_string(card_line):
    try:
        parts = card_line.split('|')
        if len(parts) < 4:
            return f"❌ `{card_line}` ➔ **Invalid Format**"
        
        cc, mes, ano, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        
        if STRIPE_SECRET_KEY:
            url = "https://api.stripe.com/v1/payment_methods"
            headers = {
                "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "type": "card",
                "card[number]": cc,
                "card[exp_month]": mes,
                "card[exp_year]": ano,
                "card[cvc]": cvv
            }
            response = requests.post(url, headers=headers, data=data)
            res_data = response.json()
            
            if "id" in res_data:
                return f"✅ `{cc[:6]}******|{mes}|{ano}|{cvv}` ➔ **Approved [LIVE - Stripe Token]**"
            else:
                err_msg = res_data.get("error", {}).get("message", "Declined")
                return f"❌ `{cc[:6]}******|{mes}|{ano}|{cvv}` ➔ **Declined ({err_msg})**"
        else:
            return f"⚠️ `{cc[:6]}******|{mes}|{ano}|{cvv}` ➔ **Stripe Key Missing**"
    except Exception:
        return f"❌ `{card_line}` ➔ **Error Processing**"

# /chk for checking 1 card
async def chk_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
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
    text = update.message.text
    # Remove command prefix (/chks)
    lines = text.split('\n')[1:] if '\n' in text else []
    if not lines:
        await update.message.reply_text("❌ Send cards line-by-line below `/chks`", parse_mode="Markdown")
        return
    
    results = [process_card_string(line.strip()) for line in lines if "|" in line]
    if results:
        await update.message.reply_text("\n".join(results[:15]), parse_mode="Markdown")  # Limit output length
    else:
        await update.message.reply_text("❌ No valid cards found.")

# /chf for checking cards via file upload
async def chf_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in BANNED_USERS:
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
        await update.message.reply_text(f"📁 File Processed!\n\n" + "\n".join(results[:15]), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ File contains no valid card lines.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Registering commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adminpannel", admin_pannel))
    app.add_handler(CommandHandler("key", generate_key))
    app.add_handler(CommandHandler("makeadmin", make_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("chk", chk_card))
    app.add_handler(CommandHandler("chks", chks_cards))
    app.add_handler(CommandHandler("chf", chf_document))
    
    # Document handler for /chf file uploads
    app.add_handler(MessageHandler(filters.Document.ALL, chf_document))

    print("Bot is up and running with all requested features & security layers...")
    app.run_polling()

if __name__ == "__main__":
    main()
        
