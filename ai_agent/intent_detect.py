import re
import dateparser
from datetime import datetime, timedelta

def detect_intent(message: str) -> str:
    """
    Detect user intent for meeting/calendar operations.
    Returns: 'book', 'fetch', or 'chat'
    """
    if not message or not isinstance(message, str):
        return "chat"
    
    message = message.lower().strip()
    
    # Remove common filler words for better analysis
    filler_words = ['please', 'can', 'could', 'would', 'will', 'i', 'want', 'to', 'the', 'a', 'an']
    words = [word for word in message.split() if word not in filler_words]
    clean_message = ' '.join(words)
    
    # Try to parse any date/time from the message
    dt = dateparser.parse(message)
    has_time_reference = dt is not None
    
    # Enhanced booking keywords - more comprehensive
    booking_keywords = [
        # Direct booking words
        'book', 'schedule', 'set', 'arrange', 'plan', 'create',
        'add', 'reserve', 'fix', 'organize', 'setup',
        
        # Meeting/appointment words
        'meeting', 'appointment', 'call', 'session', 'conference',
        'discussion', 'interview', 'catch up', 'catchup',
        
        # Hindi/Hinglish
        'meeting book kar', 'appointment set kar', 'meeting rakhi',
    ]
    
    # Enhanced fetch keywords - more comprehensive  
    fetch_keywords = [
        # Today's meetings
        'today', 'aaj', 'today\'s meetings', 'aaj ki meetings',
        'today meetings', 'meetings today', 'aaj ka schedule',
        
        # Tomorrow's meetings
        'tomorrow', 'kal', 'tomorrow\'s meetings', 'kal ki meetings',
        'tomorrow meetings', 'meetings tomorrow',
        
        # General listing
        'show', 'list', 'display', 'get', 'fetch', 'see', 'check',
        'what', 'when', 'schedule', 'calendar', 'agenda',
        'upcoming', 'next', 'previous', 'past', 'all meetings',
        
        # Time-based queries
        'this week', 'next week', 'this month', 'next month',
        'weekend', 'monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday', 'sunday',
        
        # Hindi/Hinglish
        'dikhao', 'batao', 'kya hai', 'meetings kya hai',
    ]
    
    # Casual/chat keywords
    chat_keywords = [
        'hello', 'hi', 'hey', 'how are you', 'what\'s up',
        'thanks', 'thank you', 'bye', 'goodbye', 'help',
        'what can you do', 'how do you work', 'namaste',
    ]
    
    # Question patterns that usually indicate fetching
    fetch_patterns = [
        r'\bwhat.*meetings?\b',
        r'\bwhen.*meeting\b',
        r'\bdo i have.*meeting\b',
        r'\bany.*meetings?\b',
        r'\bhow many.*meetings?\b',
        r'\bwhich.*meetings?\b',
    ]
    
    # Booking patterns that strongly indicate booking intent
    booking_patterns = [
        r'\bbook.*(?:meeting|appointment|call)\b',
        r'\bschedule.*(?:meeting|appointment|call)\b',
        r'\bset up.*(?:meeting|appointment|call)\b',
        r'\bmeet.*(?:at|on|tomorrow|today)\b',
        r'\bappointment.*(?:at|on|for)\b',
    ]
    
    # Check for strong booking patterns first
    for pattern in booking_patterns:
        if re.search(pattern, message):
            return "book"
    
    # Check for strong fetch patterns
    for pattern in fetch_patterns:
        if re.search(pattern, message):
            return "fetch"
    
    # Count keyword matches
    booking_score = sum(1 for keyword in booking_keywords if keyword in message)
    fetch_score = sum(1 for keyword in fetch_keywords if keyword in message)
    chat_score = sum(1 for keyword in chat_keywords if keyword in message)
    
    # Contextual analysis
    
    # If message starts with question words, likely fetch
    if message.startswith(('what', 'when', 'where', 'which', 'how', 'do i', 'am i', 'is there')):
        fetch_score += 2
    
    # If message has time reference + booking keywords, likely booking
    if has_time_reference and booking_score > 0:
        booking_score += 2
    
    # If message has time reference + fetch keywords, could be either
    if has_time_reference and fetch_score > 0:
        fetch_score += 1
    
    # Common booking phrases
    if any(phrase in message for phrase in [
        'let\'s meet', 'can we meet', 'meeting with', 'call with',
        'lunch with', 'dinner with', 'coffee with'
    ]):
        booking_score += 3
    
    # Common fetch phrases  
    if any(phrase in message for phrase in [
        'free today', 'free tomorrow', 'busy today', 'busy tomorrow',
        'what\'s my schedule', 'check my calendar'
    ]):
        fetch_score += 3
    
    # Short messages with just greetings are usually chat
    if len(words) <= 2 and chat_score > 0:
        return "chat"
    
    # Decision logic
    if booking_score >= 2 and booking_score > fetch_score:
        return "book"
    elif fetch_score >= 1 and fetch_score >= booking_score:
        return "fetch"
    elif chat_score > booking_score and chat_score > fetch_score:
        return "chat"
    else:
        # Default logic based on patterns
        if has_time_reference and any(word in message for word in ['meet', 'call', 'appointment']):
            return "book"
        elif any(word in message for word in ['show', 'list', 'today', 'tomorrow', 'schedule']):
            return "fetch"
        else:
            return None