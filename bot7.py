import json
import os
import random
import string
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Configuration
TOKEN = "8850025657:AAGggbj-Q9uiaxNPYXj4znGyUtxT6HWxSAY"
OWNER_ID = 8785590284
OWNER_USERNAME = "@ESCROW2929"
DB_FILE = "database.json"

# Initialize or load database
def load_db():
    if not os.path.exists(DB_FILE):
        default_data = {"admins": [], "keys": {}, "users": {}}
        with open(DB_FILE, "w") as f:
            json.dump(default_data, f, indent=4)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Helpers
def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    db = load_db()
    return user_id == OWNER_ID or user_id in db["admins"]

def has_active_subscription(user_id):
    if is_admin(user_id) or is_owner(user_id):
        return True
    db = load_db()
    str_id = str(user_id)
    if str_id in db["users"]:
        expiry = datetime.fromisoformat(db["users"][str_id])
        if datetime.now() < expiry:
            return True
    return False

# Simulate Gateway Check (Replace this with your actual API integration)
def process_single_card(card_line):
    try:
        parts = card_line.split('|')
        if len(parts) < 4:
            return f"❌ `{card_line}` - Invalid Format"
        cc, mes, ano, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        
        # Mock Response (Implement your live gateway API request here)
        return f"✅ `{cc[:6]}******|{mes}|{ano}|{cvv}` ➔ **Approved [LIVE]**"
    except Exception:
        return f"❌ `{card_line}` - Error parsing"

# --- COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 **Welcome to CC Checker Bot!**\n\n"
        f"👑 **Owner:** {OWNER_USERNAME}\n\n"
        "To view all available commands and instructions, please type: `/cmd`",
        parse_mode="Markdown"
    )

async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_user_admin = is_admin(user_id)
    
    cmd_text = (
        "📋 **Bot Commands List:**\n\n"
        "• `/cmd` - View all commands\n"
        "• `/chk CC|MM|YY|CVV` - Check a single card\n"
        "• `/chks` (with bulk cards below) - Check multiple cards\n"
        "• `/chf` (upload text file with `/chf` caption) - Check a file containing cards\n"
        "• `/redeem <KEY>` - Activate your subscription using a key\n"
    )
    
    if is_user_admin:
        cmd_text += (
            "\n🛡 **Admin Panel Commands:**\n"
            "• `/admin` - Open Admin Panel\n"
            "• `/admin panel` - Open Admin Panel\n"
            "• `/key <amount> <days>` - Generate subscription keys\n"
            "• `/makeadmin <user_id>` - (Owner Only) Promote user to admin\n"
            "• `/removeadmin <user_id>` - (Owner Only) Demote admin"
        )
        
    await update.message.reply_text(cmd_text, parse_mode="Markdown")

# Admin Panel Command Handler
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ You are not admin")
        return

    await update.message.reply_text(
        "🛠 **Admin Control Panel**\n\n"
        "• `/key <amount> <days>` - Generate subscription keys\n"
        "• `/makeadmin <user_id>` - (Owner Only) Add admin\n"
        "• `/removeadmin <user_id>` - (Owner Only) Remove admin",
        parse_mode="Markdown"
    )

# Owner Only: Add Admin
async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ You are not admin")
        return
    if not is_owner(user_id):
        await update.message.reply_text("❌ Access Denied! Only the Owner can add admins.")
        return

    try:
        target_id = int(context.args[0])
        db = load_db()
        if target_id == OWNER_ID:
            await update.message.reply_text("⚠️ Owner is already the master administrator.")
            return
            
        if target_id not in db["admins"]:
            db["admins"].append(target_id)
            save_db(db)
            await update.message.reply_text(f"✅ Successfully promoted `{target_id}` to Admin.")
        else:
            await update.message.reply_text("⚠️ This user is already an Admin.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/makeadmin <user_id>`", parse_mode="Markdown")

# Owner Only: Remove Admin
async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ You are not admin")
        return
    if not is_owner(user_id):
        await update.message.reply_text("❌ Access Denied! Only the Owner can remove admins.")
        return

    try:
        target_id = int(context.args[0])
        if target_id == OWNER_ID:
            await update.message.reply_text("❌ You cannot remove the Owner from the admin panel!")
            return
            
        db = load_db()
        if target_id in db["admins"]:
            db["admins"].remove(target_id)
            save_db(db)
            await update.message.reply_text(f"✅ Successfully removed `{target_id}` from Admins.")
        else:
            await update.message.reply_text("⚠️ User is not in the admin list.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/removeadmin <user_id>`", parse_mode="Markdown")

# Owner & Admin: Generate Keys
async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ You are not admin")
        return

    try:
        amount = int(context.args[0])
        duration_days = int(context.args[1])
        
        db = load_db()
        generated_keys = []
        
        for _ in range(amount):
            key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            formatted_key = f"KEY-{key[:4]}-{key[4:8]}-{key[8:12]}-{key[12:]}"
            db["keys"][formatted_key] = duration_days
            generated_keys.append(formatted_key)
            
        save_db(db)
        
        keys_text = "\n".join(generated_keys)
        await update.message.reply_text(f"🔑 **Generated Keys ({duration_days} days):**\n`{keys_text}`", parse_mode="Markdown")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/key <amount> <duration_in_days>`", parse_mode="Markdown")

# User: Redeem Key
async def redeem_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        key_input = context.args[0].strip()
        db = load_db()
        
        if key_input in db["keys"]:
            days = db["keys"][key_input]
            del db["keys"][key_input]
            
            str_id = str(user_id)
            current_expiry = datetime.now()
            
            if str_id in db["users"] and datetime.fromisoformat(db["users"][str_id]) > datetime.now():
                current_expiry = datetime.fromisoformat(db["users"][str_id])
                
            new_expiry = current_expiry + timedelta(days=days)
            db["users"][str_id] = new_expiry.isoformat()
            save_db(db)
            
            await update.message.reply_text(f"✅ Success! Subscription active until: `{new_expiry.strftime('%Y-%m-%d %H:%M:%S')}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Invalid or already redeemed key.")
    except IndexError:
        await update.message.reply_text("Usage: `/redeem <KEY>`", parse_mode="Markdown")

# --- CHECKER FEATURES ---

# 1. Single Card Check: /chk
async def chk_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not has_active_subscription(user_id):
        await update.message.reply_text("❌ Access denied! Redeem a subscription key first using `/redeem <key>`.")
        return

    try:
        card_data = " ".join(context.args)
        if not card_data:
            await update.message.reply_text("Usage: `/chk CC|MM|YY|CVV`", parse_mode="Markdown")
            return
            
        result = process_single_card(card_data)
        await update.message.reply_text(f"💳 **Single Check Result:**\n{result}", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ Error processing card.")

# 2. Bulk Text Check: /chks
async def chks_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not has_active_subscription(user_id):
        await update.message.reply_text("❌ Access denied! Redeem a subscription key first.")
        return

    text = update.message.text
    lines = text.split('\n')[1:]
    
    if not lines:
        await update.message.reply_text("Usage:\n`/chks`\n`CC|MM|YY|CVV`\n`CC|MM|YY|CVV`", parse_mode="Markdown")
        return

    await update.message.reply_text(f"🔄 Processing {len(lines)} cards... Please wait.")
    
    results = []
    for line in lines:
        if '|' in line:
            res = process_single_card(line.strip())
            results.append(res)
            
    response_text = "\n".join(results[:25])
    await update.message.reply_text(f"📊 **Bulk Check Results:**\n\n{response_text}", parse_mode="Markdown")

# 3. File Check: /chf
async def chf_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not has_active_subscription(user_id):
        await update.message.reply_text("❌ Access denied! Redeem a subscription key first.")
        return

    message = update.message
    if not message.document:
        await update.message.reply_text("❌ Please upload a text file with `/chf` caption containing cards formatted as `CC|MM|YY|CVV`.", parse_mode="Markdown")
        return

    file = await context.bot.get_file(message.document.file_id)
    file_bytes = await file.download_as_bytearray()
    file_content = file_bytes.decode('utf-8', errors='ignore')
    
    lines = file_content.splitlines()
    await update.message.reply_text(f"📁 File received! Processing {len(lines)} cards...")

    results = []
    for line in lines:
        if '|' in line:
            res = process_single_card(line.strip())
            results.append(res)

    output_filename = "checked_results.txt"
    with open(output_filename, "w") as f:
        f.write("\n".join(results))

    with open(output_filename, "rb") as f:
        await update.message.reply_document(document=f, caption="✅ **File Check Completed!** Here are your results.")
    
    os.remove(output_filename)

if __name__ == '__main__':
    load_db()
    app = ApplicationBuilder().token(TOKEN).build()

    # Core & Admin Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmd", show_commands))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("makeadmin", make_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    app.add_handler(CommandHandler("key", generate_key))
    app.add_handler(CommandHandler("redeem", redeem_key))
    
    # Checker Commands
    app.add_handler(CommandHandler("chk", chk_card))
    app.add_handler(CommandHandler("chks", chks_cards))
    app.add_handler(CommandHandler("chf", chf_cards))

    print("Bot is up and running...")
    app.run_polling()
  
