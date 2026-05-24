# from openai import OpenAI
# import base64
# import os
# import platform
#
# client = OpenAI(
#     base_url="https://api.gapgpt.app/v1",
#     api_key="sk-TFnTiM7cLOYZ3vWWOl8C6i3vt35u2xTMUjp5iZ1Zv4Q40frt"
# )
#
# print("در حال ساخت تصویر...")
#
# response = client.images.generate(
#     model="imagen-4.0-generate-001",
#     prompt="انیشتین که کتاب فیزیک دستش گرفته و داره با تسلا صحبت می کنه ",
#     size="1024x1024"
# )
#
# # گرفتن تصویر base64
# image_base64 = response.data[0].b64_json
#
# # تبدیل base64 به بایت
# image_bytes = base64.b64decode(image_base64)
#
# # ذخیره فایل
# filename = "ph.png"
# with open(filename, "wb") as f:
#     f.write(image_bytes)
#
# print("تصویر ذخیره شد:", filename)
#
# # باز کردن تصویر
# if platform.system() == "Windows":
#     os.startfile(filename)
# elif platform.system() == "Darwin":
#     os.system(f"open {filename}")
# else:
#     os.system(f"xdg-open {filename}")



from openai import OpenAI

client = OpenAI(base_url="https://api.gapgpt.app/v1", api_key="sk-FGFbqS6zxBEBNecUckr11dqbL3mCaXpEid9WbVebHT7uP8rF")

response = client.chat.completions.create(
    model="gapgpt-qwen-3.5",
    messages=[{"role": "user", "content": "سلام!"}]
)
print(response.choices[0].message.content)
