from flask import Flask, jsonify
from datetime import datetime
import asyncio
import json
import os
from playwright.async_api import async_playwright
import requests

app = Flask(__name__)
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
            args=['--no-sandbox'],
            executable_path='/vercel/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell'
        )
        context = await browser.new_context(user_agent='Mozilla/5.0')
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
                const posts = []; const seen = new Set();
                document.querySelectorAll('a[href*="/post/"]').forEach(a => {
                    const href = a.href;
                    const match = href.match(/\\/post\\/(\d+)\\//);
                    if (match && !href.includes('#comment') && !seen.has(match[1])) {
                        seen.add(match[1]);
                        const t = a.textContent.trim();
                        if (t && t.length > 5) posts.push({id: match[1], url: href, title: t.substring(0, 200)});
                    }
                });
                return posts;
            }''')
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()
        return posts

@app.route('/api/cron')
def cron():
    seen = load_seen()
    seen_urls = {p['url'] for p in seen}
    posts = asyncio.run(fetch_posts())
    new_posts = [p for p in posts if p['url'] not in seen_urls]
    all_posts = [{"id": p['id'], "url": p['url'], "title": p['title']} for p in posts]
    save_seen(all_posts)
    
    webhook = os.environ.get("DISCORD_WEBHOOK")
    sent = 0
    if webhook:
        for post in new_posts:
            try:
                r = requests.post(webhook, json={"content": f"**{post['title']}**\n{post['url']}"}, timeout=10)
                if r.status_code == 204:
                    sent += 1
            except:
                pass
    return jsonify({"found": len(posts), "new": len(new_posts), "sent": sent})

@app.route('/')
def dashboard():
    return f'''<!DOCTYPE html>
<html><head><title>GoreByte</title><meta charset="UTF-8"><meta http-equiv="refresh" content="30">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{background:#0a0a0f;color:#e0e0e0;font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}
.container{{max-width:700px;width:100%}}
.logo{{font-size:3em;font-weight:900;background:linear-gradient(135deg,#ff1744,#d50000);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center}}
.subtitle{{color:#666;text-align:center;margin-bottom:30px}}
.card{{background:#12121a;border:1px solid #1e1e2e;border-radius:16px;padding:24px;margin-bottom:16px}}
.card-title{{color:#aaa;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;font-size:.9em}}
.pulse{{width:10px;height:10px;background:#00e676;border-radius:50%;display:inline-block;animation:pulse 2s infinite;margin-right:10px}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(0,230,118,.4)}}50%{{box-shadow:0 0 0 12px rgba(0,230,118,0)}}}}
.status-text{{color:#00e676;font-weight:500}}
.info-row{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #1a1a24}}
.info-label{{color:#888}}.info-value{{color:#ccc;font-size:.9em}}
.badge{{padding:4px 10px;border-radius:20px;font-size:.8em;background:rgba(0,230,118,.15);color:#00e676}}
.footer{{text-align:center;color:#333;font-size:.8em;margin-top:20px}}
</style></head>
<body><div class="container">
<div class="logo">🔴 GoreByte</div><p class="subtitle">Monitoring System</p>
<div class="card"><div class="card-title">Status</div><div><span class="pulse"></span><span class="status-text">Active</span></div><p style="color:#555;margin-top:8px;font-size:.9em">Checking every 60s</p></div>
<div class="card"><div class="card-title">Config</div>
<div class="info-row"><span class="info-label">Source</span><span class="info-value">https://www.fbi.gov/</span></div>
<div class="info-row"><span class="info-label">Interval</span><span class="info-value">186,000 mi/sec</span></div>
<div class="info-row"><span class="info-label">Webhook</span><span class="badge">Set</span></div></div>
<div class="footer">GoreByte v1.0</div>
</div></body></html>'''

if __name__ == '__main__':
    app.run()
