import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import json
import os
import anthropic
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import requests

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

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

def get_emails(service, max_results=10):
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
                'body': body[:500]
            })
        
        return emails
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def load_rules():
    if not os.path.exists("agent_rules.json"):
        print("❌ agent_rules.json not found!")
        return None
    with open("agent_rules.json", 'r') as f:
        return f.read()

def analyze_email(email_content, rules):
    """Analyze email with improved prompt"""
    client = anthropic.Anthropic()
    
    prompt = f"""Analyze this email. Respond with ONLY valid JSON, nothing else.

RULES:
{rules}

EMAIL:
From: {email_content['from']}
Subject: {email_content['subject']}
Body: {email_content['body']}

RESPOND WITH ONLY THIS JSON FORMAT (no other text):
{{"action": "alert", "reason": "why", "message": "text"}}
"""
    
    try:
        msg = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        text = msg.content[0].text.strip()
        
        # Extract JSON if Claude added extra text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "{" in text:
            # Find the JSON part
            start = text.find("{")
            end = text.rfind("}") + 1
            text = text[start:end]
        
        return json.loads(text)
    
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        # Return default based on subject
        if "urgent" in email_content['subject'].lower() or "job" in email_content['subject'].lower():
            return {"action": "alert", "reason": "urgent/job email", "message": "Important email detected"}
        else:
            return {"action": "ignore", "reason": "low priority", "message": ""}
    
    except Exception as e:
        return {"error": str(e), "action": "error"}

def send_whatsapp_alert(message, config_file='whatsapp_config.json'):
    """Send WhatsApp alert via Twilio"""
    try:
        if not os.path.exists(config_file):
            print("⚠️ WhatsApp not configured")
            return False
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{config['account_sid']}/Messages.json"
        
        data = {
            "From": f"whatsapp:{config['from_number']}",
            "To": f"whatsapp:{config['to_number']}",
            "Body": message
        }
        
        response = requests.post(
            url,
            data=data,
            auth=(config['account_sid'], config['auth_token'])
        )
        
        if response.status_code == 201:
            return True
        else:
            print(f"❌ WhatsApp error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ WhatsApp error: {str(e)}")
        return False

def send_reply(service, message_id, to_email, subject, reply_body):
    """Send auto-reply to email"""
    try:
        from email.mime.text import MIMEText
        
        message = MIMEText(reply_body)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}"
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {
            'raw': raw,
            'threadId': message_id
        }
        
        service.users().messages().send(
            userId='me',
            body=send_message
        ).execute()
        
        return True
    except Exception as e:
        print(f"❌ Reply error: {str(e)}")
        return False

def main():
    print("\n" + "="*80)
    print("🤖 AI GMAIL AGENT - INTELLIGENT EMAIL TRIAGE WITH AUTOMATION")
    print("="*80 + "\n")
    
    # Load rules
    print("📋 Loading intelligent email rules...")
    rules = load_rules()
    if not rules:
        return
    print("✅ Rules loaded\n")
    
    # Connect Gmail
    print("🔐 Connecting to Gmail...")
    try:
        service = get_gmail_service()
        print("✅ Connected!\n")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return
    
    # Fetch emails
    print("📬 Fetching unread emails...")
    emails = get_emails(service, max_results=10)
    
    if not emails:
        print("✅ No unread emails")
        return
    
    print(f"📧 Found {len(emails)} unread emails\n")
    
    # Statistics
    stats = {'alerted': 0, 'replied': 0, 'ignored': 0, 'errors': 0}
    
    # Analyze each email
    for i, email in enumerate(emails, 1):
        print("="*80)
        print(f"📧 EMAIL #{i}")
        print("="*80)
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        if len(email['body']) > 100:
            print(f"Body: {email['body'][:100]}...")
        else:
            print(f"Body: {email['body']}")
        print()
        
        # Get AI decision
        print("🤖 Claude AI Analysis:")
        print("-"*80)
        decision = analyze_email(email, rules)
        
        action = decision.get('action', 'error')
        reason = decision.get('reason', 'Unknown')
        message = decision.get('message', '')
        
        print(f"Action: {action.upper()}")
        print(f"Reason: {reason}")
        
        if action == 'alert':
            print(f"🚨 Alert Message: {message}")
            whatsapp_msg = f"📧 {email['subject']}\n\nFrom: {email['from']}\n\n{message}"
            if send_whatsapp_alert(whatsapp_msg):
                print("✅ WhatsApp alert sent!")
            stats['alerted'] += 1
        
        elif action == 'reply':
            print(f"✅ Auto-Reply: {message}")
            # Uncomment to actually send replies:
            # if send_reply(service, email['id'], email['from'], email['subject'], message):
            #     print("✅ Reply sent!")
            stats['replied'] += 1
        
        elif action == 'ignore':
            print(f"🗑️ Ignore (mark as read)")
            stats['ignored'] += 1
        
        else:
            if decision.get('action') in ['alert', 'reply', 'ignore']:
        # Action found but went into wrong branch - retry the action
               action = decision.get('action')
               if action == 'alert':
                     stats['alerted'] += 1
               elif action == 'reply':
                    stats['replied'] += 1
               elif action == 'ignore':
                    stats['ignored'] += 1
            else:
                print(f"❌ Error: {decision.get('error', 'Unknown error')}")
                stats['errors'] += 1
        
        print()
    
    # Summary
    print("="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Total Emails Processed: {len(emails)}")
    print(f"🚨 Alerts (Need User Action): {stats['alerted']}")
    print(f"✅ Auto-Replied: {stats['replied']}")
    print(f"🗑️ Ignored: {stats['ignored']}")
    print(f"❌ Errors: {stats['errors']}")
    print("\n✅ Email Triage Complete!")
    print("="*80)

if __name__ == "__main__":
    main()