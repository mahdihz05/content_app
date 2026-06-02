# from messaging_automation.services.telegram_service import TelegramService
#
# service = TelegramService(bot_token="8960877163:AAFhOCBIBAodvSXXJQ8eBFhMljWJc7E8e3Y")
#
# service.send_text(
#     chat_id=-1003913224802,
#     text="تست"
# )


from messaging_automation.services.telegram_service import TelegramService

service = TelegramService(
    bot_token="8960877163:AAFhOCBIBAodvSXXJQ8eBFhMljWJc7E8e3Y"
)

text = """d
<b>🚀 معرفی نرم‌افزار Remote Desktop Pro</b>

🔹 مدیریت کامل سیستم‌های راه دور  
🔹 اتصال امن و رمزنگاری‌شده  
🔹 مناسب برای تیم‌های IT و شرکت‌ها  

━━━━━━━━━━━━━━
<b>✨ ویژگی‌ها:</b>

• کنترل کامل سیستم از راه دور  
• انتقال فایل سریع  
• رابط کاربری ساده  

━━━━━━━━━━━━━━
<b>💡 نسخه تست</b>
"""

image_path = r"C:\Users\m.hosseinzadeh\Pictures\Screenshots\Screenshot 2026-05-10 150238.png"


# ارسال عکس به کانال
result = service.send_photo(
    chat_id=-1003913224802,
    photo_url=image_path,   # چون سرویس فعلی تو اسمش photo_url هست
    caption=text
)

print(result)