import asyncio
import json
import os
from playwright.async_api import async_playwright
import requests

DATA_FILE = "/tmp/seen_posts.json"

def load_seen():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_seen(seen):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(seen, f)
    except:
        pass

async def fetch_posts():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = await context.new_page()
        posts = []
        
        try:
            url = os.environ.get("URL", "https://watchpeopledie.tv/home")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)
            
            try:
                await page.click('text=I am 18 or older', timeout=5000)
                await page.wait_for_timeout(3000)
            except:
                pass
            
            await page.wait_for_timeout(5000)
            
            posts = await page.evaluate('''() => {
                const posts = [];
                const seen = new Set();
                document.querySelectorAll('a[href*="/post/"]').forEach(a => {
                    const href = a.href;
                    const match = href.match(/\\/post\\/(\d+)\\//);
                    if (match && !href.includes('#comment') && !seen.has(match[1])) {
                        seen.add(match[1]);
                        const title = a.textContent.trim();
                        if (title && title.length > 5) {
                            posts.push({id: match[1], url: href, title: title.substring(0, 200)});
                        }
                    }
                });
                return posts;
            }''')
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()
        return posts

def handler(request):
    seen = load_seen()
    seen_urls = {p['url'] for p in seen}
    
    posts = asyncio.run(fetch_posts())
    
    new_posts = []
    all_posts = []
    for post in posts:
        all_posts.append({"id": post['id'], "url": post['url'], "title": post['title']})
        if post['url'] not in seen_urls:
            new_posts.append(post)
    
    save_seen(all_posts)
    
    webhook = os.environ.get("DISCORD_WEBHOOK")
    sent = 0
    for post in new_posts:
        try:
            msg = f"**{post['title']}**\n{post['url']}"
            r = requests.post(webhook, json={"content": msg}, timeout=10)
            if r.status_code == 204:
                sent += 1
        except:
            pass
    
    return {
        "statusCode": 200,
        "body": json.dumps({"found": len(posts), "new": len(new_posts), "sent": sent})
    }
