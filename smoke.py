import telebot
import sqlite3
from telebot import types

# Insert your Bot Token and Admin ID below
API_TOKEN = '7949556972:AAFE4mmt0q_uWFVimkFPQFbJ_1DccKOkduI'  # Your bot token
BOT_USERNAME = 'smokeblogmanagerbot'  # Your bot username
ADMIN_ID = 5605574743  # Your admin ID

bot = telebot.TeleBot(API_TOKEN)

# --- Database Setup ---
conn = sqlite3.connect('referrals.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables for referrals, users, repairs, and new features
cursor.execute('''CREATE TABLE IF NOT EXISTS referrals (
    user_id INTEGER PRIMARY KEY,
    referred_by INTEGER,
    count INTEGER DEFAULT 0
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    device_name TEXT,
    device_status TEXT,
    membership_level TEXT DEFAULT 'free'
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS repairs (
    repair_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    device TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS tools (
    tool_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT,
    tool_link TEXT,
    category TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    payment_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

conn.commit()

# --- Sparkling Button Effect ---
def create_sparkling_buttons():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Buttons with emojis for each function
    buttons = [
        ("✨ Get Tools ✨", "get_tools"),
        ("💬 Give Feedback 💬", "give_feedback"),
        ("🔧 Repair Status 🔧", "repair_status"),
        ("🎉 Referrals 🎉", "referrals"),
        ("🌐 Visit Website 🌐", "visit_website"),
        ("📦 My Repairs 📦", "my_repairs"),
        ("🚀 Upgrade Plan 🚀", "upgrade_plan"),
        ("📲 Device Tools 📲", "device_tools"),
        ("🧠 Smart FAQ 🧠", "smart_faq"),
        ("🧾 Request Repair 🧾", "request_repair"),
        ("💡 Tips & Tricks 💡", "tips_tricks"),
        ("👤 My Profile 👤", "my_profile"),
        ("🪙 Make Payment 🪙", "make_payment"),
        ("📤 Upload Tool (Admin) 📤", "upload_tool"),
        ("📊 Analytics Dashboard 📊", "analytics")
    ]
    
    # Adding all the buttons to the keyboard
    for label, data in buttons:
        button = types.InlineKeyboardButton(text=label, callback_data=data)
        keyboard.add(button)

    return keyboard

# --- /start Command ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    referred_by = int(args[1]) if len(args) > 1 else None

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    cursor.execute("SELECT * FROM referrals WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO referrals (user_id, referred_by) VALUES (?, ?)", (user_id, referred_by))
        if referred_by:
            cursor.execute("UPDATE referrals SET count = count + 1 WHERE user_id=?", (referred_by,))
        conn.commit()

    # Greeting message with sparkling buttons
    bot.send_message(
        user_id,
        "✨ Welcome to Smoke Technologies Bot! ✨\nChoose an option below to get started.",
        reply_markup=create_sparkling_buttons()
    )

# --- Button Interaction Handlers ---

# Get Tools
@bot.callback_query_handler(func=lambda call: call.data == "get_tools")
def handle_get_tools(call):
    bot.answer_callback_query(call.id, "You will be redirected to the tools list...")
    bot.send_message(call.message.chat.id, "Here are your available tools:\n/get frp_tool\n/get flash_tool\n/get mtk_bypass")

# Give Feedback
@bot.callback_query_handler(func=lambda call: call.data == "give_feedback")
def handle_feedback(call):
    bot.answer_callback_query(call.id, "Please provide your feedback!")
    msg = bot.send_message(call.message.chat.id, "Please provide your feedback.")
    bot.register_next_step_handler(msg, save_feedback, call.from_user.id)

# Repair Status
@bot.callback_query_handler(func=lambda call: call.data == "repair_status")
def handle_repair_status(call):
    bot.answer_callback_query(call.id, "Please provide your repair ID!")
    msg = bot.send_message(call.message.chat.id, "Please enter your repair ID:")
    bot.register_next_step_handler(msg, get_repair_status)

# Referrals
@bot.callback_query_handler(func=lambda call: call.data == "referrals")
def handle_referrals(call):
    bot.answer_callback_query(call.id, "Here is your referral link!")
    user_id = call.from_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    cursor.execute("SELECT count FROM referrals WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    count = result[0] if result else 0

    response = f"Your referral link:\n{link}\n\nReferrals: {count}"
    if count >= 5:
        response += "\n\n**Congratulations!** You've unlocked the bonus tool!\nDownload: https://yourlink.com/bonus_tool"

    bot.send_message(call.message.chat.id, response, parse_mode="Markdown")

# Handle Feedback
def save_feedback(message, user_id):
    feedback_text = message.text
    cursor.execute("INSERT INTO feedback (user_id, message) VALUES (?, ?)", (user_id, feedback_text))
    conn.commit()
    bot.send_message(message.chat.id, "Thank you for your feedback!")

# Get Repair Status
def get_repair_status(message):
    try:
        repair_id = message.text
        cursor.execute("SELECT * FROM repairs WHERE repair_id=?", (repair_id,))
        repair = cursor.fetchone()

        if repair:
            status_message = f"Repair ID: {repair[0]}\n" \
                             f"Device: {repair[2]}\n" \
                             f"Status: {repair[3]}\n" \
                             f"Created At: {repair[4]}\n" \
                             f"Last Updated: {repair[5]}"
        else:
            status_message = "Repair ID not found. Please check your repair ID and try again."

        bot.send_message(message.chat.id, status_message)
    except IndexError:
        bot.send_message(message.chat.id, "Usage: /repair_status [repair_id]")

# Request Repair
@bot.callback_query_handler(func=lambda call: call.data == "request_repair")
def handle_request_repair(call):
    bot.answer_callback_query(call.id, "Please enter your repair details!")
    msg = bot.send_message(call.message.chat.id, "Please provide details for the repair request.")
    bot.register_next_step_handler(msg, save_repair_request)

# Save Repair Request
def save_repair_request(message):
    repair_details = message.text
    user_id = message.from_user.id
    cursor.execute("INSERT INTO repairs (user_id, device, status) VALUES (?, ?, ?)", (user_id, repair_details, "Pending"))
    conn.commit()
    bot.send_message(message.chat.id, "Repair request submitted successfully!")

# Other actions (e.g., upgrading plans, making payment, etc.) should follow a similar pattern:
# - Create a callback query handler for each button.
# - Define the corresponding function to handle the specific action.

# Start the bot
bot.polling()
