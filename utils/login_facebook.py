from playwright.sync_api import sync_playwright
import json

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto("https://www.facebook.com/")

#     input("👉 Đăng nhập Facebook xong, nhấn Enter để lưu cookie...")

#     cookies = context.cookies()
#     with open("facebook_cookies.json", "w", encoding="utf-8") as f:
#         json.dump(cookies, f)

#     browser.close()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.facebook.com/")

    input("👉 Đăng nhập facebook xong, nhấn Enter để lưu cookie...")

    cookies = context.cookies()
    with open("facebook_cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f)

    browser.close()
