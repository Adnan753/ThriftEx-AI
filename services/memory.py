import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

headers = {
    "apiKey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def get_past_decisions(limit: int = 10):
    try :
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/recommendations",
            headers=headers,
            params={
                'order': 'created_at.desc',
                'limit': limit,
                'select': 'service,action,status,priority,created_at'
            }
        )
        return response.json()
    except Exception as e:
        print(f"Memory fetch error: {e}")
        return []
    
def format_memory_for_prompt(decisions: list) -> str:
    if not decisions:
        return "No previous decisions recorded."
    
    lines = []
    for d in decisions:
        lines.append(
            f"- [{d.get('status', 'unknown')}] {d.get('service')}: {d.get('action')} (Priority: {d.get('priority')})"
        )
        
    return "\n".join(lines)