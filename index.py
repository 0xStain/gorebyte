from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def dashboard():
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GoreByte - Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #0a0a0f; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }}
        .container {{ max-width: 700px; width: 100%; }}
        .logo {{ font-size: 3em; font-weight: 900; background: linear-gradient(135deg, #ff1744, #d50000); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }}
        .subtitle {{ color: #666; text-align: center; margin-bottom: 30px; }}
        .card {{ background: #12121a; border: 1px solid #1e1e2e; border-radius: 16px; padding: 24px; margin-bottom: 16px; }}
        .card-title {{ color: #aaa; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; font-size: 0.9em; }}
        .pulse {{ width: 10px; height: 10px; background: #00e676; border-radius: 50%; display: inline-block; animation: pulse 2s infinite; margin-right: 10px; }}
        @keyframes pulse {{ 0%, 100% {{ box-shadow: 0 0 0 0 rgba(0,230,118,0.4); }} 50% {{ box-shadow: 0 0 0 12px rgba(0,230,118,0); }} }}
        .status-text {{ color: #00e676; font-weight: 500; }}
        .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #1a1a24; }}
        .info-label {{ color: #888; }}
        .info-value {{ color: #ccc; font-size: 0.9em; }}
        .badge {{ padding: 4px 10px; border-radius: 20px; font-size: 0.8em; background: rgba(0,230,118,0.15); color: #00e676; }}
        .footer {{ text-align: center; color: #333; font-size: 0.8em; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔴 GoreByte</div>
        <p class="subtitle">watchpeopledie.tv monitoring system</p>
        <div class="card">
            <div class="card-title">Status</div>
            <div><span class="pulse"></span><span class="status-text">Active & Monitoring</span></div>
            <p style="color:#555;margin-top:8px;font-size:0.9em;">Checking every 60 seconds via Vercel Cron</p>
        </div>
        <div class="card">
            <div class="card-title">Configuration</div>
            <div class="info-row"><span class="info-label">Source</span><span class="info-value">watchpeopledie.tv/home</span></div>
            <div class="info-row"><span class="info-label">Interval</span><span class="info-value">60 seconds</span></div>
            <div class="info-row"><span class="info-label">Webhook</span><span class="badge">Configured</span></div>
            <div class="info-row"><span class="info-label">Platform</span><span class="info-value">Vercel Free</span></div>
        </div>
        <div class="footer">GoreByte v1.0 • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC</div>
    </div>
</body>
</html>'''

if __name__ == '__main__':
    app.run()