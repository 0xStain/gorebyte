import asyncio
from playwright.async_api import async_playwright
import requests
import config

seen_posts = set()

async def verify_age(page):
    try:
        await page.wait_for_selector('text=I am 18 or older', timeout=5000)
        await page.click('text=I am 18 or older')
        await page.wait_for_timeout(2000)
    except:
        pass
    try:
        for sel in ['text=Yes', 'text=Continue', 'text=Agree']:
            try:
                await page.click(sel, timeout=2000)
                await page.wait_for_timeout(2000)
                break
            except:
                continue
    except:
        pass

async def fetch_posts(page):
    await page.wait_for_timeout(5000)
    posts = await page.evaluate('''() => {
        const posts = [];
        const seen = new Set();
        document.querySelectorAll('a[href*="/post/"]').forEach(a => {
            const href = a.href;
            const parts = href.split('/post/');
            if (parts.length < 2) return;
            const idPart = parts[1].split('/')[0];
            if (!idPart || idPart.includes('#')) return;
            if (seen.has(idPart)) return;
            seen.add(idPart);
            const title = a.textContent.trim();
            if (title && title.length > 5) {
                posts.push({url: href, title: title.substring(0, 200)});
            }
        });
        return posts;
    }''')
    return posts

def send_discord(post):
    msg = f"**{post['title']}**\n{post['url']}"
    try:
        r = requests.post(config.DISCORD_WEBHOOK, json={"content": msg}, timeout=10)
        if r.status_code == 204:
            print(f"Sent: {post['title'][:50]}")
    except Exception as e:
        print(f"Send error: {e}")

async def main():
    global seen_posts
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        page = await context.new_page()
        await page.goto(config.URL, wait_until='domcontentloaded', timeout=60000)
        await verify_age(page)

        posts = await fetch_posts(page)
        if config.SEND_INITIAL:
            print(f"Sending all {len(posts)} posts now...")
            for p in posts:
                send_discord(p)
                seen_posts.add(p['url'])
                await asyncio.sleep(1)
        else:
            for p in posts:
                seen_posts.add(p['url'])
            print(f"Cached {len(seen_posts)} existing posts.")

        while True:
            await asyncio.sleep(config.CHECK_INTERVAL)
            await page.reload(wait_until='domcontentloaded')
            await page.wait_for_timeout(5000)
            await verify_age(page)

            posts = await fetch_posts(page)
            new_posts = [p for p in posts if p['url'] not in seen_posts]
            for p in new_posts:
                send_discord(p)
                seen_posts.add(p['url'])
                await asyncio.sleep(1)
            if new_posts:
                print(f"Sent {len(new_posts)} new posts.")
            else:
                print("No new posts.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())