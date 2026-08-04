import asyncio
from playwright.async_api import async_playwright
import requests
import config


seen_videos = set()


async def fetch_page_with_verification():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            print("Loading page...")
            await page.goto(config.URL, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Handle first age verification
            try:
                print("Looking for 'I am 18 or older' button...")
                await page.wait_for_selector('text=I am 18 or older', timeout=10000)
                await page.click('text=I am 18 or older')
                print("Clicked first verification!")
                await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"First verification: {e}")
            
            # Handle second verification
            try:
                print("Checking for second verification...")
                selectors = [
                    'text=I am 18 or older',
                    'text=Yes',
                    'text=Continue',
                    'text=Enter',
                    'text=Agree',
                    'button:has-text("18")',
                    'button:has-text("Yes")',
                    'button:has-text("Continue")',
                ]
                
                for selector in selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=2000)
                        if element:
                            print(f"Clicking second: '{selector}'")
                            await element.click()
                            await page.wait_for_timeout(3000)
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Second verification: {e}")
            
            print("Waiting for video content to load...")
            await page.wait_for_timeout(5000)
            
            # Get ALL video sources and post info
            videos_data = await page.evaluate('''() => {
                const videos = [];
                
                // Find video elements
                document.querySelectorAll('video, video source, [src*=".mp4"]').forEach(el => {
                    const src = el.src || el.getAttribute('src');
                    if (src && src.includes('.mp4')) {
                        videos.push({
                            videoUrl: src,
                            type: 'direct_video'
                        });
                    }
                });
                
                // Find post containers with links
                document.querySelectorAll('a[href*="/post/"], a[href*="/video/"], a[href*="/watch/"]').forEach(a => {
                    const postUrl = a.href;
                    const title = a.textContent.trim() || a.closest('article')?.textContent.trim() || '';
                    
                    // Look for video within the post
                    const parent = a.closest('article, .post, .video-card, [class*="post"], [class*="video"]');
                    const videoEl = parent ? parent.querySelector('video, video source, [src*=".mp4"]') : null;
                    const videoSrc = videoEl ? (videoEl.src || videoEl.getAttribute('src')) : null;
                    
                    videos.push({
                        postUrl: postUrl,
                        videoUrl: videoSrc,
                        title: title.substring(0, 200)
                    });
                });
                
                return videos;
            }''')
            
            print(f"Found {len(videos_data)} videos/posts")
            await browser.close()
            return videos_data
            
        except Exception as e:
            print(f"Error: {e}")
            await browser.close()
            return []


def send_to_discord(video_data):
    try:
        message = None
        
        # Check for direct video URL first (Discord embeds .mp4 automatically)
        if video_data and video_data.get('videoUrl'):
            message = video_data['videoUrl']
        # Fall back to post URL
        elif video_data and video_data.get('postUrl'):
            message = video_data['postUrl']
        
        if not message:
            return
        
        print(f"Sending to Discord: {message[:100]}...")
        response = requests.post(
            config.DISCORD_WEBHOOK,
            json={"content": message},
            timeout=10
        )
        if response.status_code == 204:
            print(f"✅ Sent successfully!")
        else:
            print(f"❌ Discord error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Failed to send: {e}")


async def main():
    global seen_videos
    
    print("🤖 GoreByte Bot Started")
    print(f"📡 Monitoring: {config.URL}")
    print(f"⏰ Check interval: {config.CHECK_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            videos_data = await fetch_page_with_verification()
            
            if videos_data:
                new_videos = []
                for video in videos_data:
                    video_id = video.get('videoUrl') or video.get('postUrl')
                    if video_id and video_id not in seen_videos:
                        new_videos.append(video)
                        seen_videos.add(video_id)
                
                if new_videos:
                    print(f"\n🆕 Found {len(new_videos)} new videos!")
                    for video in new_videos:
                        video_url = video.get('videoUrl') or video.get('postUrl') or ''
                        print(f"   📹 {video_url[:100]}")
                        send_to_discord(video)
                        await asyncio.sleep(1)
                else:
                    print("✅ No new videos found")
            else:
                print("⚠️ No videos found on page")
            
            print(f"⏳ Waiting {config.CHECK_INTERVAL} seconds...\n")
            await asyncio.sleep(config.CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            await asyncio.sleep(config.CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())