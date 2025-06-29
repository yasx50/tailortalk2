import dateparser

def detect_intent(message: str) -> str:
    message = message.lower().strip()

    # Detect if datetime is mentioned
    dt = dateparser.parse(message)

    # Booking intent keywords
    booking_keywords = [
        "book", "schedule", "set meeting", "add event", "fix", "arrange",
        "meeting", "appointment", "call", "zoom", "google meet", "baithak", "milna", "nirdharit", "karna"
    ]

    # Fetching/viewing schedule
    fetch_keywords = [
        "list", "show", "view", "check", "what meetings", "aaj ki meetings", "kal ki meetings",
        "today's schedule", "upcoming events", "meri meeting", "meeting list", "kya meeting", "kaun si meeting"
    ]

    # General questions (date/day/bot)
    general_keywords = [
        "aaj kya hai", "what day", "what date", "aaj kaun sa din", "today's date", "kal kya hai",
        "are you a bot", "who are you", "hello", "hi", "namaste"
    ]

    # Match against categories
    if any(kw in message for kw in booking_keywords) and dt:
        return "book"

    if any(kw in message for kw in fetch_keywords):
        return "fetch"

    if any(kw in message for kw in general_keywords):
        return "general"

    return "none"  # fallback to LLM or default logic
