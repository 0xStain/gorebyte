🔴 GoreByte

Automated Post Monitoring & Discord Notification System

GoreByte is a Python-based monitoring system that checks a configured website for new posts and automatically sends notifications to a Discord channel through a webhook.

It uses Playwright for browser automation and Discord Webhooks for notifications.

[!WARNING]
This project may monitor websites containing graphic or disturbing content. It is intended strictly for adults (18+). Use responsibly and comply with applicable laws and the monitored website's terms of service.
✨ Features
Automated Monitoring – Continuously checks a configured website for new posts.
Discord Notifications – Sends new post titles and URLs directly to a Discord channel.
Duplicate Prevention – Tracks previously discovered posts during the current session.
Configurable Check Interval – Choose how frequently the website is checked.
Initial Notifications – Optionally send existing posts when the bot first starts.
Browser Automation – Uses Playwright with Chromium to retrieve posts.
Headless Operation – Runs without displaying a browser window.
📁 Project Structure
text
GoreByte/
├── config.py
├── main_final.py
├── index.py
├── requirements.txt
└── README.md

File	Description
config.py	Main configuration settings
main_final.py	Primary monitoring script
index.py	Flask-based monitoring endpoint and dashboard
requirements.txt	Python dependencies
⚙️ Configuration

Open config.py and configure the following values:

python
URL = "https://example.com/home"
DISCORD_WEBHOOK = "YOUR_DISCORD_WEBHOOK_URL"
CHECK_INTERVAL = 60
SEND_INITIAL = True

Configuration Options
Variable	Description	Default
URL	Website URL to monitor	Empty
DISCORD_WEBHOOK	Discord webhook URL	Empty
CHECK_INTERVAL	Time between checks, in seconds	60
SEND_INITIAL	Send existing posts on startup	True

Note: Set SEND_INITIAL = False if you only want notifications for newly discovered posts after startup.

🚀 Installation
1. Clone the repository
bash
git clone https://github.com/0xStain/gorebyte.git
cd gorebyte

2. Create a virtual environment
bash
python -m venv .venv


Activate it on Windows:

powershell
.venv\Scripts\activate


On Linux:

bash
source .venv/bin/activate

3. Install dependencies
bash
pip install -r requirements.txt

4. Install Playwright Chromium
bash
playwright install chromium


On Linux, you may also need:

bash
playwright install-deps chromium

5. Configure the bot

Edit config.py and provide your website URL and Discord webhook URL.

6. Start GoreByte
bash
python main_final.py


GoreByte will start monitoring the configured website and send notifications according to your settings.

🔔 Discord Notifications

When a new post is discovered, GoreByte sends a message in this format:

text
**Post Title**
https://example.com/post/123/


Make sure your Discord webhook is valid and has permission to send messages in the selected channel.

🌐 Flask Dashboard (index.py)

The repository also includes a Flask-based implementation with:

A web dashboard displaying monitoring status.
An /api/cron endpoint for triggering a monitoring check.
Discord webhook notifications.
A stored list of previously discovered posts.

This implementation is separate from main_final.py and uses environment variables:

env
URL=https://example.com/home
DISCORD_WEBHOOK=YOUR_DISCORD_WEBHOOK_URL


The dashboard is available at /, while the monitoring endpoint is available at /api/cron.

🔒 Security
Never commit your actual Discord webhook URL.
Keep sensitive configuration out of public repositories.
Use environment variables or a private configuration file for deployment secrets.
Rotate your Discord webhook immediately if it becomes publicly exposed.
🛠️ Technologies Used
Python
Playwright
Chromium
Requests
Flask (dashboard implementation)
📌 Notes
The monitoring process must remain running to continuously detect new posts.
The current main_final.py implementation stores previously discovered posts in memory. Restarting the script resets its tracking history.
The Flask implementation stores tracking data in /tmp/seen_posts.json, which may not persist across server restarts or deployments.
Website changes may require updates to the post extraction logic.
📄 License

No license has been specified yet. All rights and permissions are reserved by default unless a license is added to this repository.

GoreByte v1.0
Automated monitoring. Instant notifications.
