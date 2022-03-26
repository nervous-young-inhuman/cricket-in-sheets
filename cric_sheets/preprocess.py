import re
import zipfile
from datetime import timezone, timedelta, datetime
from . import teams

# todo: handle draw case
ACCEPTED_TEXTS = teams.TEAM_KEYS
MAX_ACCEPTED_TEXT_LENGTH = len(max(ACCEPTED_TEXTS, key=len))
CHAT_TEXT_RE = re.compile(
    r'\[(?P<date>\d?\d/\d?\d/\d?\d), (?P<time>\d?\d:\d?\d:\d?\d) (?P<time_period>[AP]M)\](?P<contact>[^:]+):(?P<text>.*)'
)

DEFAULT_TIMEZONE = timezone(timedelta(hours=5, minutes=30))

def parse_date(time_str, *, timezone=DEFAULT_TIMEZONE):
    format_str = '%d/%m/%y %I:%M:%S %p'
    return datetime.strptime(time_str, format_str).replace(tzinfo=timezone)

def parse_contact(contact_str):
    text, subs = re.subn(r'[^+0-9]', '', contact_str)
    return dict(type=('number' if subs else 'name'), text=text.strip())

def parse_message(raw_text):
    text = re.sub(r'[^ A-Za-z]', '', raw_text).strip()
    accept_text = (len(text) <= MAX_ACCEPTED_TEXT_LENGTH) and (text.lower() in ACCEPTED_TEXTS)
    return text.lower() if accept_text else ''

def preprocess_texts(all_text):
    lines = all_text.split(b'\r\n')

    for line in lines:
        line = line.decode('utf-8')
        match = re.search(CHAT_TEXT_RE, line)
        if match:
            date_str = ' '.join(match.group('date', 'time', 'time_period'))
            date = parse_date(date_str)
            contact_str = match.group('contact')
            contact = parse_contact(contact_str)
            message_str = match.group('text')
            message = parse_message(message_str)
            if message:
                yield dict(date=date, contact=contact, message=message)
