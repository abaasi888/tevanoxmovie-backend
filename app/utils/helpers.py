import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict
import json

def generate_uuid() -> str:
    """Generate a unique UUID"""
    return str(uuid.uuid4())

def generate_short_uuid(length: int = 8) -> str:
    """Generate a short UUID"""
    return uuid.uuid4().hex[:length].upper()

def format_currency(amount: float, currency: str = "UGX") -> str:
    """Format currency amount"""
    return f"{currency} {amount:,.2f}"

def format_date(date: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime"""
    if not date:
        return ""
    return date.strftime(format_str)

def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[datetime]:
    """Parse date string to datetime"""
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

def validate_email(email: str) -> bool:
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    pattern = r'^[0-9]{10,13}$'
    return bool(re.match(pattern, phone))

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def safe_json_parse(json_str: str) -> Dict:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {}

def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase to snake_case"""
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', camel_str).lower()

def get_time_ago(date: datetime) -> str:
    """Get time ago string"""
    now = datetime.utcnow()
    diff = now - date
    
    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30
    years = days / 365
    
    if seconds < 60:
        return "Just now"
    elif minutes < 60:
        return f"{int(minutes)}m ago"
    elif hours < 24:
        return f"{int(hours)}h ago"
    elif days < 7:
        return f"{int(days)}d ago"
    elif weeks < 4:
        return f"{int(weeks)}w ago"
    elif months < 12:
        return f"{int(months)}mo ago"
    else:
        return f"{int(years)}y ago"

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text"""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]