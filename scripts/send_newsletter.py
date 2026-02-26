import smtplib
import json
import sqlite3
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send():
    try:
        with open('config/email_credentials.json', 'r') as f:
            creds = json.load(f)
    except Exception as e:
        print('Failed to read config:', e)
        return

    port = int(creds.get('smtp_port', 465))
    host = creds.get('smtp_server')
    user = creds.get('email')
    pw = creds.get('password')

    conn = sqlite3.connect('data/db/newsletter.db')
    subs = [row[0] for row in conn.execute('SELECT email FROM subscribers').fetchall()]
    conn.close()

    if not subs:
        print('No subscribers to send to.')
        return

    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port)
        else:
            server = smtplib.SMTP(host, port)
            server.starttls()
        server.login(user, pw)
    except Exception as e:
        print('Failed to connect/login to SMTP:', e)
        return

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; padding: 0; background-color: #050505; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #e0e0e0; }
            .container { max-width: 650px; margin: 0 auto; background-color: #0f0f13; border: 1px solid #1f2937; border-radius: 12px; overflow: hidden; box-shadow: 0 0 20px rgba(0, 242, 254, 0.1); }
            .header-img { width: 100%; display: block; border-bottom: 2px solid #00f2fe; }
            .logo-container { text-align: center; padding: 25px 0; background-color: #000; }
            .logo { max-width: 200px; }
            .content { padding: 40px 30px; }
            h2 { color: #ffffff; font-size: 24px; text-transform: uppercase; letter-spacing: 2px; margin-top: 0; text-align: center; border-bottom: 1px solid #333; padding-bottom: 15px; }
            .article { margin-bottom: 40px; background: #161b22; padding: 25px; border-radius: 8px; border-left: 4px solid #00f2fe; transition: transform 0.3s; }
            .article h3 { color: #00f2fe; margin-top: 0; font-size: 20px; }
            .article p { font-size: 15px; line-height: 1.6; color: #b0b8c4; }
            .btn-container { margin-top: 20px; }
            .read-more { display: inline-block; padding: 12px 24px; background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%); color: #ffffff !important; text-decoration: none; border-radius: 4px; font-weight: bold; text-transform: uppercase; font-size: 13px; letter-spacing: 1px; }
            .footer { background-color: #050505; padding: 30px; text-align: center; border-top: 1px solid #1f2937; }
            .footer p { color: #666; font-size: 12px; margin: 5px 0; }
            .footer a { color: #00f2fe; text-decoration: none; }
        </style>
    </head>
    <body>
        <div style="padding: 20px; background-color: #050505;">
            <div class="container">
                <div class="logo-container">
                    <img src="https://theaiupdate.org/img/logo.png" alt="The AI Update Logo" class="logo">
                </div>
                <img src="https://theaiupdate.org/img/banner.png" alt="Futuristic AI Banner" class="header-img">

                <div class="content">
                    <h2>Weekly Intelligence: Issue #001</h2>

                    <div class="article">
                        <h3>1. The Zero-Budget AI Business</h3>
                        <p>You don't need a $4,000 GPU to build an AI business. We break down the exact freemium stack (Google Colab + DeepSeek + n8n) to build passive income streams today.</p>
                        <div class="btn-container">
                            <a href="https://theaiupdate.org" class="read-more">Access Deep Dive &rarr;</a>
                        </div>
                    </div>

                    <div class="article">
                        <h3>2. The Evolution of Agentic LLMs in 2026</h3>
                        <p>The transition from standard chat interfaces to autonomous agentic workflows is the defining shift of the year. Here is why developers building parallel pipelines will outpace chat models entirely.</p>
                        <div class="btn-container">
                            <a href="https://theaiupdate.org" class="read-more">Access Deep Dive &rarr;</a>
                        </div>
                    </div>

                    <div class="article">
                        <h3>3. OpenClaw: Parallel Agents are INSANE!</h3>
                        <p>We break down how OpenClaw allows users to run parallel AI agents directly from Discord to generate passive income. This is the next frontier of extreme productivity.</p>
                        <div class="btn-container">
                            <a href="https://theaiupdate.org" class="read-more">Access Deep Dive &rarr;</a>
                        </div>
                    </div>
                </div>

                <div class="footer">
                    <p><strong>Stay Ahead of the Curve.</strong></p>
                    <p>You are receiving this because you subscribed at <a href="https://theaiupdate.org">theaiupdate.org</a>.</p>
                    <p>&copy; 2026 The AI Update. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    for sub in subs:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[UPDATED] Issue #001: Zero-Budget AI, Agentic Workflows & OpenClaw'
        msg['From'] = f'The AI Update <{user}>'
        msg['To'] = sub
        part = MIMEText(html, 'html')
        msg.attach(part)

        try:
            server.sendmail(user, sub, msg.as_string())
            print(f'Sent futuristic version successfully to {sub}')
        except Exception as e:
            print(f'Failed to send to {sub}: {e}')

    server.quit()

if __name__ == '__main__':
    send()
