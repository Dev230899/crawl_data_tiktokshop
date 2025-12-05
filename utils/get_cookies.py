import asyncio
import nodriver as uc
import time


async def tiktok():
    browser = await uc.start(lang="vi-VN")

    page = await browser.get("https://www.tiktok.com/login?lang=vi-VN")

    login_type = await page.find("Sử dụng số điện thoại/email/tên người dùng")
    await login_type.click()

    pass_type = await page.find("Đăng nhập bằng mật khẩu")
    await pass_type.click()
    await asyncio.sleep(2)

    mobile = await page.select("input[name=mobile]")
    await mobile.send_keys("0775078956")
    await asyncio.sleep(2)

    password = await page.select("input[type=password]")
    await password.send_keys("Phuoc230899@")

    await asyncio.sleep(5)
    btn_login = await page.select("button[type=submit]")
    await btn_login.click()

    await asyncio.sleep(30)
    await browser.cookies.save(file="tiktok.session.data")

    await page.get("https://www.tiktok.com/shop/vn/c?source=ecommerce_category&enter_method=bread_crumbs&first_entrance=tiktok_others&lang=vi-VN")
    await asyncio.sleep(5)
 
async def facebook():
    browser = await uc.start(
        browser_executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
    )

    page = await browser.get("https://www.facebook.com/")

    email = await page.select("input[name=email]")
    await email.send_keys("100037866225490")

    email = await page.select("input[name=pass]")
    await email.send_keys("Phuoc230899")

    await asyncio.sleep(5)

    btn_login = await page.select("button[name=login]")
    await btn_login.click()

    await asyncio.sleep(60)
    await browser.cookies.save(file="facebook.session.data")


async def main():
    await tiktok()
    # await facebook()


# Facebook account : 100037866225490 password : Phuoc230899
# tiktok account : 0775078956 password : Phuoc230899@
if __name__ == "__main__":
    # uc.loop().run_until_complete(facebook())
    uc.loop().run_until_complete(main())
