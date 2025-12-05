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
import json
from pathlib import Path
from nodriver import cdp

class CrawlTiktokShop:
    def __init__(self, browser):
        self.browser = browser
        self.al = Alphabet()

    async def init(self):
        self.browser = await uc.start(headless=False)
        await self.browser.cookies.load(file="facebook.session.data")
        await self.browser.cookies.load(file="tiktok.session.data")

    async def close(self):
        self.browser.stop()

    async def process_bio(self, bio_text):
        phones = []
        links = []
        links, phones = self.al.get_link_and_phone([bio_text])
        links = list(set(links))
        phones = list(set(phones))
        return links, phones

    def check_link_type(self, link):
        if "facebook" in link or "fb" in link:
            return "fb"
        if "zalo.me" in link or "zaloapp.com" in link:
            return "zalo"
        if "beacons" in link:
            return "beacons"
        if "bio" in link:
            return "bio"
        return ""

    async def scrape_beacon_profile(self, link_beacons):
        try:
            link_fb = []
            link_zalo = []
            another_link = []
            link_beacons = (
                "https://" + link_beacons
                if "https://" not in link_beacons
                else link_beacons
            )
            try:
                page = await asyncio.wait_for(
                    self.browser.get(link_beacons), timeout=120
                )
            except:
                await self.close()
                await self.init()
                page = await asyncio.wait_for(
                    self.browser.get(link_beacons), timeout=120
                )

            await asyncio.sleep(5)
            html_content = await page.evaluate("document.documentElement.outerHTML")
            soup = BeautifulSoup(html_content, "html.parser")
            a_tags = soup.find_all("a", href=True)
            for a in a_tags:
                link = a.get("href")
                if "fb" in link.lower() or "facebook" in link.lower():
                    link_fb.append(link)
                elif "zalo.me" in link.lower() or "zaloapp.com" in link.lower():
                    link_zalo.append(link)
                else:
                    another_link.append(link)

            return link_fb, link_zalo, another_link
        except Exception as e:
            print(f"An error occurred while scraping beacon: {str(e)}")
            return None, None, None
        
    async def scrape_facebook_profile(self, link):
        try:
            if "https://" not in link:
                link = f"https://{link.strip()}"
            try:
                page = await asyncio.wait_for(
                    self.browser.get(link.strip()), timeout=120
                )
            except:
                await self.close()
                await self.init()
                page = await asyncio.wait_for(
                    self.browser.get(link.strip()), timeout=120
                )
            await asyncio.sleep(5)
            html_content = await page.evaluate("document.documentElement.outerHTML")
            soup = BeautifulSoup(html_content, "html.parser")
            sum = ""
            email = None
            list_info = []
            try:
                intro = soup.find(
                    "div", {"class": "x2b8uid x80vd3b x1q0q8m5 xso031l x1l90r2v"}
                ).text.strip()
            except:
                intro = ""
            info_tags = soup.find_all(
                "div",
                {
                    "class": "x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x193iq5w xeuugli x1r8uery x1iyjqo2 xs83m0k xamitd3 xsyo7zv x16hj40l x10b6aqq x1yrsyyn"
                },
            )
            for tag in info_tags:
                info = tag.text.strip()
                sum += f" {info}"
                list_info.append(info)
            list_info.append(intro)
            links, phones = self.al.get_link_and_phone(list_info)
            for l in links:
                if "@gmail" in l:
                    email = l
                    links.remove(l)
            profile_info = {
                "link_fb": link,
                "intro": intro,
                "another_links": list(set(links)),
                "phones": list(set(phones)),
                "description": f"{intro} {sum}",
                "email": email,
            }
            return profile_info
        except Exception as e:
            print(f"An error occurred while scraping facebook: {str(e)}")
            import traceback

            print(traceback.format_exc())
            return None
           
    async def process_link(self, link):
        link = link if link else ""
        if self.check_link_type(link) == "fb":
            try:
                profile_info = await asyncio.wait_for(
                    self.scrape_facebook_profile(link), timeout=120
                )
            except:
                await self.close()
                await self.init()
                profile_info = await self.scrape_facebook_profile(link)
            return "fb", profile_info
        elif self.check_link_type(link) == "zalo":
            return "zalo", {"link_zalo": link}
        elif self.check_link_type(link) == "beacons":
            result = []
            links_fb, links_zalo, another_links = await self.scrape_beacon_profile(link)
            if links_fb:
                for fb in links_fb:
                    try:
                        profile_info = await asyncio.wait_for(
                            self.scrape_facebook_profile(fb), timeout=120
                        )
                    except:
                        await self.close()
                        await self.init()
                        profile_info = await self.scrape_facebook_profile(fb)
                    result.append({"domain": "fb", "info": profile_info})
            if links_zalo:
                for zl in links_zalo:
                    result.append({"domain": "zalo", "link": zl})
            if another_links:
                for l in another_links:
                    result.append({"domain": "another", "link": l})
            return "beacon", result
        elif self.check_link_type(link) == "bio":
            result = []
            try:
                links_fb, links_zalo, another_links = await asyncio.wait_for(
                    self.scrape_beacon_profile(link), timeout=120
                )
            except:
                await self.close()
                await self.init()
                links_fb, links_zalo, another_links = await asyncio.wait_for(
                    self.scrape_beacon_profile(link), timeout=120
                )
            if links_fb:
                for fb in links_fb:
                    try:
                        profile_info = await asyncio.wait_for(
                            self.scrape_facebook_profile(fb), timeout=120
                        )
                    except:
                        await self.close()
                        await self.init()
                        profile_info = await self.scrape_facebook_profile(fb)
                    result.append({"domain": "fb", "info": profile_info})
            if links_zalo:
                for zl in links_zalo:
                    result.append({"domain": "zalo", "link": zl})
            if another_links:
                for l in another_links:
                    result.append({"domain": "another", "link": l})
            return "bio", result
        return "", None
        
    async def scrape_profile(self, url):
        try:
            try:
                page = await asyncio.wait_for(self.browser.get(url), timeout=120)
            except:
                await self.close()
                await self.init()
                page = await asyncio.wait_for(self.browser.get(url), timeout=120)
            links = []
            phones = []
            another_links = []
            facebook_profile_info, zalo_profile_info = None, None
            await asyncio.sleep(5)
            await page.sleep(10)
            html_content = await page.evaluate("document.documentElement.outerHTML")
            soup = BeautifulSoup(html_content, "html.parser")
            try:
                bio_text = soup.select_one('h2[data-e2e="user-bio"]').text.strip()
            except:
                bio_text = None
            if bio_text:
                try:
                    links, phones = await asyncio.wait_for(
                        self.process_bio(bio_text), timeout=120
                    )
                except:
                    await self.close()
                    await self.init()
                    links, phones = await asyncio.wait_for(
                        self.process_bio(bio_text), timeout=120
                    )
            try:
                user_link = soup.find(
                    "span", {"class": "css-847r2g-SpanLink"}
                ).text.strip()
            except:
                user_link = None
            if user_link:
                links.append(user_link)
                another_links.append(user_link)
            if links:
                for link in links:
                    try:
                        domain, result = await asyncio.wait_for(
                            self.process_link(link), timeout=120
                        )
                    except:
                        await self.close()
                        await self.init()
                        domain, result = await asyncio.wait_for(
                            self.process_link(link), timeout=120
                        )
                    if domain == "fb":
                        facebook_profile_info = result
                    elif domain == "zalo":
                        zalo_profile_info = result
                    elif domain == "beacon":
                        for r in result:
                            if r["domain"] == "fb":
                                facebook_profile_info = r["info"]
                            elif r["domain"] == "zalo":
                                zalo_profile_info = {"link_zalo": r["link"]}
                            elif r["domain"] == "another":
                                another_links.append(r["link"])
                    elif domain == "bio":
                        for r in result:
                            if r["domain"] == "fb":
                                facebook_profile_info = r["info"]
                            elif r["domain"] == "zalo":
                                zalo_profile_info = {"link_zalo": r["link"]}
                            elif r["domain"] == "another":
                                another_links.append(r["link"])
            tiktok_profile_info = {
                "username": (
                    soup.select_one('h1[data-e2e="user-title"]').text.strip()
                    if soup.select_one('h1[data-e2e="user-title"]')
                    else None
                ),
                "display_name": (
                    soup.select_one('h2[data-e2e="user-subtitle"]').text.strip()
                    if soup.select_one('h2[data-e2e="user-subtitle"]')
                    else None
                ),
                "follower_count": (
                    self.al.value_to_float(
                        soup.select_one(
                            'strong[data-e2e="followers-count"]'
                        ).text.strip()
                    )
                    if soup.select_one('strong[data-e2e="followers-count"]')
                    else None
                ),
                "following_count": (
                    self.al.value_to_float(
                        soup.select_one(
                            'strong[data-e2e="following-count"]'
                        ).text.strip()
                    )
                    if soup.select_one('strong[data-e2e="following-count"]')
                    else None
                ),
                "like_count": (
                    self.al.value_to_float(
                        soup.select_one('strong[data-e2e="likes-count"]').text.strip()
                    )
                    if soup.select_one('strong[data-e2e="likes-count"]')
                    else None
                ),
                "bio": (
                    soup.select_one('h2[data-e2e="user-bio"]').text.strip()
                    if soup.select_one('h2[data-e2e="user-bio"]')
                    else None
                ),
                "phones": phones,
                "another_links": another_links,
                "url": url
            }
            return tiktok_profile_info, facebook_profile_info, zalo_profile_info

        except Exception as e:
            print(f"An error occurred while scraping tiktok profile: {str(e)}")
            import traceback

            print(traceback.format_exc())
            return None, None, None
        
    async def crawl_user(self,user_link):
        try:
            (
                tiktok_profile_info,
                facebook_profile_info,
                zalo_profile_info,
            ) = await asyncio.wait_for(
                self.scrape_profile(user_link), timeout=120
            )
        except:
            self.close()
            self.init()
            (
                tiktok_profile_info,
                facebook_profile_info,
                zalo_profile_info,
            ) = await asyncio.wait_for(
                self.scrape_profile(user_link), timeout=120
            )

        return tiktok_profile_info, facebook_profile_info, zalo_profile_info          

    async def crawl_user(self, user_name):
        page = await asyncio.wait_for(
            self.browser.get(f"https://www.tiktok.com/search/user?q={user_name}"), timeout=120
        )
        await page.wait_for("a[data-e2e='search-user-info-container']", timeout=15000)
        await asyncio.sleep(3)
        html_content = await page.evaluate("document.documentElement.outerHTML")
        soup = BeautifulSoup(html_content, "html.parser")
        tiktok_profile_info, facebook_profile_info, zalo_profile_info = None, None, None
        list_user = soup.find_all("a",{"data-e2e":"search-user-info-container"})
        for u in list_user:
            user_nickname = u.find("p",{"data-e2e":"search-user-nickname"}).text.strip()
            if user_nickname == user_name:
                user_link = u.get("href")
                try:
                    (
                        tiktok_profile_info,
                        facebook_profile_info,
                        zalo_profile_info,
                    ) = await asyncio.wait_for(
                        self.scrape_profile(f"https://www.tiktok.com{user_link}"), timeout=120
                    )
                except:
                    self.close()
                    self.init()
                    (
                        tiktok_profile_info,
                        facebook_profile_info,
                        zalo_profile_info,
                    ) = await asyncio.wait_for(
                        self.scrape_profile(f"https://www.tiktok.com{user_link}"), timeout=120
                    )
                break

        return tiktok_profile_info, facebook_profile_info, zalo_profile_info

# async def start():
#     browser = await uc.start()

#     ct = CrawlTiktokShop(browser)
#     tiktok_profile_info, facebook_profile_info, zalo_profile_info = await ct.crawl_user("GDT-Mall-VN")
#     print(tiktok_profile_info)
# if __name__ == "__main__":
#     uc.loop().run_until_complete(start())