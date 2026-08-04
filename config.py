import os

# Site to monitor
URL = os.environ.get("URL", "https://watchpeopledie.tv/home")

# Discord webhook
DISCORD_WEBHOOK = os.environ.get("https://discord.com/api/webhooks/1534195842569994322/9BxxdNuLqiX6cv8FpslIz_F26QOpiRa21Vfl1ZWbDgwGj2y3w57d-KSx0UxiCYK8EDF0", "")

# Check interval (used by Vercel cron)
CHECK_INTERVAL = 60