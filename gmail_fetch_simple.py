"""
Simple Gmail Fetcher using Gmail API with simplified auth
"""

import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Get Gmail service"""
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_emails(service, max_results=5):
    """Fetch unread emails"""
    try:
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg_id in messages:
            msg = service.users().messages().get(
                userId='me',
                id=msg_id['id'],
                format='full'
            ).execute()
            
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            body = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
            else:
                data = msg['payload']['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            emails.append({
                'id': msg_id['id'],
                'from': from_email,
                'subject': subject,
                'body': body[:300]
            })
        
        return emails
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

if __name__ == "__main__":
    print("🔐 Connecting to Gmail...")
    service = get_gmail_service()
    print("✅ Connected!")
    
    print("\n📬 Fetching emails...")
    emails = get_emails(service)
    
    if emails:
        print(f"Found {len(emails)} emails:\n")
        for i, email in enumerate(emails, 1):
            print(f"{i}. From: {email['from']}")
            print(f"   Subject: {email['subject']}\n")
    else:
        print("No unread emails")