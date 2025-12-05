import nodriver as uc
import asyncio
from utils.alphabet import Alphabet
from bs4 import BeautifulSoup
from modules.config import settings
import random
import time
from modules.tiktok_mongo_handler import TiktokShopMongoHandler
from datetime import datetime, timedelta, timezone
import re
import hashlib
from playwright.async_api import async_playwright
import json
from pathlib import Path
from nodriver import cdp
from model.models import TiktokShop, Product, Shop, Category
from crawl_tiktokshop import CrawlTiktokShop
from googletrans import Translator

translator = Translator()
class Crawler:
    def __init__(self):
        self.db_handler = TiktokShopMongoHandler(settings=settings)
        self.al = Alphabet()

    async def get_categories_lv1(self, browser):
        
        categories = []
        page = await asyncio.wait_for(
            browser.get("https://www.tiktok.com/shop/vn/c?source=ecommerce_category&enter_method=bread_crumbs&first_entrance=ecommerce_mall&first_entrance_position=categories&lang=vi-VN"), timeout=120
        )
        await asyncio.sleep(5)

        await page.wait_for("a[class*='w-full']", timeout=15000)

        html_content = await page.evaluate("document.documentElement.outerHTML")
        soup = BeautifulSoup(html_content, "html.parser")
        
        category_tags = soup.find_all(
            "a", {"class":"w-full"}
        )

        for tag in category_tags:
            if tag.get("href"):
                categories.append(tag.get("href"))
        
        return categories
    
    async def fetch_data(self, page, product_url, crawl_tiktok):
        try:
            images = []
            await page.get(f"{product_url}?lang=vi-VN")
            await asyncio.sleep(5)

            html_content = await page.evaluate("document.documentElement.outerHTML")
            soup = BeautifulSoup(html_content, "html.parser")
            
            # product id
            product_id = self.al.get_product_id(product_url)
            
            # category and sub_categories
            sub_categories = []
            ol = soup.find("ol",{"class":"items-center"})
            li_tags = ol.find_all("li")

            category_tag = li_tags[-2].find("a")
            cat_url = category_tag.get("href")
            cat_id = self.al.get_cat_id(cat_url)
            ct_tag = category_tag.find("span").text.strip()
            category_name = translator.translate(ct_tag, src="auto", dest="vi").text 

            for li in li_tags[1:len(li_tags)-1]:
                a_tag = li.find("a")
                subcat_url = a_tag.get("href")
                subcat_id = self.al.get_cat_id(subcat_url)
                sb_tag = a_tag.text.strip()
                subcat_name = translator.translate(sb_tag, src="auto", dest="vi").text

                sub_categorie = Category(
                    id = subcat_id,
                    name = subcat_name,
                    url = subcat_url
                )
                sub_categories.append(sub_categorie)

            # description
            try:
                desc = soup.find("div",{"class":"transition-all"}).text.strip()
            except:
                desc = None

            # name
            product_name = soup.find("h1").text.strip()

            # images
            image_tag = soup.find("div",{"class":"slick-track"})
            image_list = image_tag.find_all("img")

            for img in image_list:
                if img.get("src"):
                    images.append(img.get("src"))

            # video
            videos = []
            try:
                video = soup.find("video",{"class":"w-full"}).get("src")
                videos.append(video)
            except:
                pass

            # price
            try:
                price = int(soup.find("span",{"class":"flex flex-row items-baseline"}).text.strip().replace("₫","").replace(".",""))
            except:
                price = None

            # rating star
            try:
                rating_star = str(soup.find("div",{"class":"H1-Bold text-color-UIText1Display"}).text.strip())
            except:
                rating_star = None
            # rating count
            try:
                rating_count = str(soup.find("div",{"class":"text-color-UIText1Display H2-Semibold"}).text.replace("global reviews","").strip())
            except:
                rating_count = None

            # like count
            liked_count = None

            # quantity_sold
            try:
                quantity_sold = int(soup.find_all("span",{"class":"H3-Regular text-color-UIText2"})[-1].text.replace("đã được bán").strip())
            except:
                quantity_sold = None

            # product option
            try:
                product_options = []             
                option_tag = soup.find("div",{"class":"flex flex-col gap-20"})
                # option_name = option_tag.find("span",{"class":"H2-Semibold text-color-UIText1Display"}).text.replace(":","").strip()
                # options = option_tag.find_all("span",{"class":"w-full P3-Regular"})
                # print(len(options))
                # for op in options:
                #     if op.text.strip():
                #         ops.append(op.text.strip())
                # product_options.append({
                #     option_name : ops
                # })
                option_tag_name = option_tag.find_all("div",{"class":"flex flex-row items-center mb-12"})
                options_tag = option_tag.find_all("div",{"class":"flex flex-row overflow-x-auto gap-12 flex-wrap"})

                for i in range(0,len(option_tag_name)):
                    ops = []
                    option_name = option_tag_name[i].find("span",{"class":"H2-Semibold text-color-UIText1Display"}).text.replace(":","").strip()
                    options = options_tag[i].find_all("span",{"class":"w-full P3-Regular"})
                    for op in options:
                        if op.text.strip():
                            ops.append(op.text.strip())
                    product_options.append({
                        option_name : ops
                    })                    

            except:
                product_options = None

            # shop
            shop_tag = soup.find("div",{"data-testid":"tux-config-provider"})
            # shop_id = self.al.get_cat_id(soup.find("a",{"class":"H3-Regular text-color-UIText2"}).get("href"))
            shop_name = shop_tag.find("span",{"class":"H2-Bold text-color-UIText1"}).text.strip()
            shop_rating = str(shop_tag.find("span",{"class":"P2-Semibold text-color-UIText1"}).text.strip())

            tiktok_profile_info, facebook_profile_info, zalo_profile_info = await crawl_tiktok.crawl_user(shop_name)
            shop = Shop(
                shop_id = None,
                url = tiktok_profile_info["url"],
                name = shop_name,
                location = None,
                rating = shop_rating,
                is_official = None
            )

            product = Product(
                product_id=str(product_id),
                product_sku=None,
                category_id=cat_id,
                crawl_category_name=category_name,
                crawl_category_url=cat_url,
                crawl_category_key=None,
                descriptions = desc,
                url=product_url,
                name=product_name,
                domain= "https://tiktok.com/",
                images=images,
                videos=videos,
                price=price,
                sub_categories=sub_categories,
                price_before_discount=None,
                price_range=None,
                price_range_before_discount=None,
                rating_star=rating_star,
                rating_count=rating_count,
                liked_count=liked_count,
                quantity_sold=quantity_sold,
                stock=None,
                shop=shop,
                is_adult=None,
                currency="VND",
                product_options=product_options,
            )
            self.db_handler.insert_product(product)
            
            products = []
            products.append(f"https://www.tiktok.com/view/product/{product_id}")

            if tiktok_profile_info:
                tiktok_shop = TiktokShop(
                    url=tiktok_profile_info["url"],
                    shop_name=shop_name,
                    rating=shop_rating,
                    following=tiktok_profile_info["following_count"],
                    followers=tiktok_profile_info["follower_count"],
                    likes=tiktok_profile_info["like_count"],
                    phones=tiktok_profile_info["phones"],
                    bio=tiktok_profile_info["bio"],
                    facebook_info=facebook_profile_info,
                    zalo_info=zalo_profile_info,
                    products = products
                )
                self.db_handler.inser_shop(tiktok_shop)
        except:
            import traceback
            traceback.print_exc()
    async def crawl(self, page, crawl_tiktok):
        while True:
            try:
                load_more = await page.find("View more")
                await load_more.click()

                await asyncio.sleep(5)
            except:
                await asyncio.sleep(5)
                break
        
        html_content = await page.evaluate("document.documentElement.outerHTML")
        soup = BeautifulSoup(html_content, "html.parser")

        a_tags = soup.find_all("a",{"class":"P2-Regular"})
        for tag in a_tags:
            if tag.get("href"):
                await self.fetch_data(page, tag.get("href"), crawl_tiktok)


        

    async def get_categories_child(self, page):
        categories = []

        html_content = await page.evaluate("document.documentElement.outerHTML")
        soup = BeautifulSoup(html_content, "html.parser")
        
        category_tags = soup.find_all(
            "a", {"class":"H4-Semibold"}
        )

        for tag in category_tags:
            if tag.get("href"):
                categories.append(tag.get("href"))
        
        return categories       

    async def crawl_category(self, page, cat_url, crawl_tiktok, visited=set()):
        if cat_url in visited:
            return
        visited.add(cat_url)

        await page.get(f"{cat_url}?lang=vi-VN")
        await asyncio.sleep(3)

        child_categories = await self.get_categories_child(page)

        if child_categories:
            print(f"Category cha: {cat_url}")
            for child_url in child_categories:
                await self.crawl_category(page, child_url, crawl_tiktok, visited)
        else:
            print(f"    - Category con: {cat_url} → crawl sản phẩm")
            await self.crawl(page, crawl_tiktok)



async def start_crawl():
    browser = await uc.start(headless=False, no_sandbox=True, lang="vi-VN")
    await browser.main_tab.maximize()
    await browser.cookies.load(file="tiktok.session.data")
    crawler = Crawler()
    crawl_tiktok = CrawlTiktokShop(browser)

    categories_lv1 = await crawler.get_categories_lv1(browser=browser)
    for category_lv1 in categories_lv1:
        page = await asyncio.wait_for(
            browser.get(category_lv1), timeout=120
        )
        await crawler.crawl_category(page, category_lv1, crawl_tiktok)

if __name__ == "__main__":
    asyncio.run(start_crawl())
