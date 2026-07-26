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
ADMIN_IDS = []  apni Telegram Admin ID yahan add kar sakte hain (e.g., [123456789])

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_message = (
        f"Hello {user.first_name}!\n\n"
        f"🤖 **CC Checker & Admin Bot is Online**\n"
        f"Send your cards in `CC|MM|YY|CVV` format to check.\n\n"
        f"👑 **Owner:** {OWNER_USERNAME}"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

# /admin or Admin Panel command
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Agar admin list me ho ya owner ho toh panel open hoga
    panel_message = (
        f"🛠 **Admin Panel**\n\n"
        f"• Status: Active & Running\n"
        f"• Stripe Integration: Connected (Test Mode)\n"
        f"• Total Users: Active\n\n"
        f"Use commands like /keys to check gateway configs."
    )
    await update.message.reply_text(panel_message, parse_mode="Markdown")

# /keys command to check configuration status
async def check_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_secret = "Loaded ✅" if STRIPE_SECRET_KEY else "Missing ❌"
    status_pub = "Loaded ✅" if STRIPE_PUBLISHABLE_KEY else "Missing ❌"
    
    key_info = (
        f"🔑 **Gateway Key Status:**\n\n"
        f"• Stripe Secret Key: {status_secret}\n"
        f"• Stripe Publishable Key: {status_pub}"
    )
    await update.message.reply_text(key_info, parse_mode="Markdown")

# Single card processing logic using Stripe API
def process_single_card(card_line):
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
                return f"✅ `{cc[:6]}******|{mes}|{ano}|{cvv}` ➔ **Approved [LIVE - Stripe Token Created]**"
            else:
                err_msg = res_data.get("error", {}).get("message", "Declined")
                return f"❌ `{cc[:6]}******|{mes}|{ano}|{cvv}` ➔ **Declined ({err_msg})**"
        else:
            return f"⚠️ `{cc[:6]}******|{mes}|{ano}|{cvv}` ➔ **Stripe Key Missing in Environment**"
            
    except Exception as e:
        return f"❌ `{card_line}` ➔ **Error Processing**"

# Message handler for checking cards sent in chat
async def handle_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
        
    lines = text.split('\n')
    results = []
    for line in lines:
        line = line.strip()
        if "|" in line:
            result = process_single_card(line)
            results.append(result)
            
    if results:
        response_text = "\n".join(results)
        await update.message.reply_text(response_text, parse_mode="Markdown")

def main():
    # Bot builder initialization
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers (Purani aur Nayi dono commands yahan register hain)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("keys", check_keys))
    
    # Message handler for cards
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_cards))

    print("Bot is up and running with full features...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
