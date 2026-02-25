import imaplib
import json
import os

class EmailCEO:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def check_inbox(self):
        print(f"Scanning {self.config['email']} for new opportunities...")
        try:
            mail = imaplib.IMAP4_SSL(self.config['imap_server'])
            mail.login(self.config['email'], self.config['password'])
            mail.select('inbox')
            status, data = mail.search(None, 'UNSEEN')
            mail_ids = data[0].split()
            print(f"Found {len(mail_ids)} unread messages.")
            mail.logout()
        except Exception as e:
            print(f"Inbox Error: {e}")

if __name__ == '__main__':
    ceo = EmailCEO('/a0/usr/projects/x-manage/config/email_credentials.json')
    ceo.check_inbox()
