from datetime import timezone, timedelta, datetime
from pathlib import Path
from collections import defaultdict
from operator import itemgetter
from . import preprocess
from . import cricket
from . import teams

def get_all_text(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

def validate_match(match):
    required = ('date', 'winner', 'id', 'status')
    for field in required:
        if field not in match:
            raise cricket.CricketException(f'{field} not found in {match}.')


def main(match_id, start_time, chat_file_path):
    match = cricket.match(match_id)
    validate_match(match)
    stop_time = datetime.fromisoformat(match['date'])
    winning_team = teams.find_team(match['winner'])
    
    if winning_team:
        winning_team_keys = map(str.lower, itemgetter('name', 'abbr')(winning_team))
        acceptable_messages = tuple(winning_team_keys)
    elif draw:
        acceptable_messages = ('draw',)
    else:
        error_handle
    messages = get_all_text(chat_file_path)
    oldest_entry_by_contact = dict()

    for entry in preprocess.preprocess_texts(messages):
        contact = entry['contact']
        previous_entry = oldest_entry_by_contact.get(contact, None)
        if not previous_entry:
            previous_entry = {'date': timedelta.max}
        if (
                (entry['date'] < previous_entry['date'])
                and (start_time <= entry['date'] < stop_time)
                and (entry['message'] in acceptable_messages)
        ):
            entry['additonal_score'] = 1
            oldest_entry_by_contact[contact] = entry
    
            


# if __name__ == '__main__':
#     chat_file_path = str(Path('./data/_chat.txt').resolve())
#     match_id = ''
#     start_time = ''
#     main(match_id, start_time, chat_file_path)
