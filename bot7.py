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

# Railway environment variables se Stripe keys uthana
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Aapka Telegram Bot Token

OWNER_USERNAME = "@ESCROW2929"

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_message = (
        f"Hello {user.first_name}!\n\n"
        f"🤖 **CC Checker Bot is Online**\n"
        f"Send your cards in `CC|MM|YY|CVV` format to check.\n\n"
        f"👑 **Owner:** {OWNER_USERNAME}"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

# Single card processing logic using Stripe API (Test/Live mode depending on keys)
def process_single_card(card_line):
    try:
        parts = card_line.split('|')
        if len(parts) < 4:
            return f"❌ `{card_line}` ➔ **Invalid Format**"
        
        cc, mes, ano, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        
        # Agar Stripe Secret Key available hai toh Stripe API hit karega
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
            # Fallback agar key set na ho
            return f"⚠️ `{cc[:6]}******|{mes}|{ano}|{cvv}` ➔ **Stripe Key Missing in Environment**"
            
    except Exception as e:
        return f"❌ `{card_line}` ➔ **Error Processing**"

# Message handler for checking cards sent in chat
async def handle_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
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
    else:
        await update.message.reply_text("❌ No valid card format found! Use `CC|MM|YY|CVV`")

def main():
    # Bot builder initialization
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_cards))

    print("Bot is up and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
                                       
