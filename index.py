from flask import Flask, render_template
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html', timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))

# For local testing
if __name__ == '__main__':
    app.run(debug=True, port=3000)