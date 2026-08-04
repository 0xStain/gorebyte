import asyncio
import json
import os
from playwright.async_api import async_playwright
import requests

# Store seen posts in Vercel's /tmp directory
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
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        posts = []
        
        try:
            url = os.environ.get("URL", "https://watchpeopledie.tv/home")
            print(f"Loading: {url}")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Click age verification
            try:
                await page.wait_for_selector('text=I am 18 or older', timeout=10000)
                await page.click('text=I am 18 or older')
                print("Age verified!")
                await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"Age verify 1: {e}")
            
            # Second verification
            try:
                for sel in ['text=I am 18 or older', 'text=Yes', 'text=Continue', 'text=Agree']:
                    try:
                        el = await page.wait_for_selector(sel, timeout=2000)
                        if el:
                            await el.click()
                            await page.wait_for_timeout(3000)
                            print(f"Clicked: {sel}")
                            break
                    except:
                        continue
            except:
                pass
            
            await page.wait_for_timeout(5000)
            
            # Extract posts
            posts = await page.evaluate('''() => {
                const posts = [];
                const links = document.querySelectorAll('a[href*="/post/"]');
                const seen = new Set();
                
                links.forEach(a => {
                    const href = a.href;
                    const match = href.match(/\\/post\\/(\d+)\\//);
                    if (match && !href.includes('#comment') && !seen.has(match[1])) {
                        const title = a.textContent.trim();
                        if (title && title.length > 5) {
                            seen.add(match[1]);
                            posts.push({
                                id: match[1],
                                url: href,
                                title: title.substring(0, 200)
                            });
                        }
                    }
                });
                return posts;
            }''')
            
            print(f"Found {len(posts)} posts")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()
        
        return posts


def send_to_discord(post):
    webhook = os.environ.get("DISCORD_WEBHOOK")
    if not webhook:
        print("No webhook configured")
        return False
    
    try:
        message = f"**{post['title']}**\n{post['url']}"
        r = requests.post(webhook, json={"content": message}, timeout=10)
        return r.status_code == 204
    except Exception as e:
        print(f"Discord error: {e}")
        return False


# Vercel serverless handler
def handler(request):
    print("GoreByte cron running...")
    
    seen = load_seen()
    seen_urls = {p['url'] for p in seen}
    
    posts = asyncio.run(fetch_posts())
    
    new_posts = []
    all_posts_data = []
    
    for post in posts:
        all_posts_data.append({"id": post['id'], "url": post['url'], "title": post['title']})
        if post['url'] not in seen_urls:
            new_posts.append(post)
    
    # Save updated list
    save_seen(all_posts_data)
    
    sent = 0
    for post in new_posts:
        if send_to_discord(post):
            sent += 1
    
    result = {
        "success": True,
        "total_found": len(posts),
        "new_posts": len(new_posts),
        "sent_to_discord": sent,
        "total_tracked": len(all_posts_data)
    }
    
    print(f"Result: {result}")
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result)
    }