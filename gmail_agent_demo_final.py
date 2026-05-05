import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

def load_rules():
    if not os.path.exists("agent_rules.json"):
        print("agent_rules.json not found!")
        return None
    with open("agent_rules.json", 'r') as f:
        return f.read()

def analyze_email(email_content, rules):
    client = anthropic.Anthropic()
    prompt = f"""You MUST respond with ONLY valid JSON, nothing else.

RULES:
{rules}

EMAIL:
From: {email_content['from']}
Subject: {email_content['subject']}
Body: {email_content['body']}

Respond with ONLY this JSON format (no other text):
{{"action": "reply", "reason": "explanation", "message": "response"}}

or

{{"action": "ignore", "reason": "explanation", "message": ""}}

or

{{"action": "alert", "reason": "explanation", "message": "alert text"}}"""
    
    try:
        msg = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        text = msg.content[0].text.strip()
        print(f"DEBUG: {text}")  # Show what Claude returned
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

EMAILS = [
    {'from': 'boss@company.com', 'subject': 'Q4 Planning', 'body': 'Discuss Q4?'},
    {'from': 'newsletter@site.com', 'subject': 'Newsletter', 'body': 'Check articles'},
    {'from': 'client@acme.com', 'subject': 'URGENT: Deadline', 'body': 'Need ASAP'},
]

def main():
    print("\n🤖 AI GMAIL AGENT\n")
    rules = load_rules()
    if not rules:
        return
    
    for i, email in enumerate(EMAILS, 1):
        print(f"Email {i}: {email['subject']}")
        decision = analyze_email(email, rules)
        print(f"  Action: {decision.get('action', 'error')}")

        print(f"  Error: {decision.get('error', '')}\n")
    
    print("✅ Done!")

if __name__ == "__main__":
    main()