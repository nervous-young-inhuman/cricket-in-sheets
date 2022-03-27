from datetime import timedelta, datetime, MAXYEAR
from itertools import chain
from operator import itemgetter

from . import preprocess
from . import teams
from .helpers import first

def team_as_keys(team):
    return map(str.lower, itemgetter('name', 'abbr')(team))

def get_existing_scores(*, sheet_obj, sheet_name):
    rows = sheet_obj.values(range=sheet_name)

    scores = {}
    for (raw_contact, raw_score, *_) in rows:
        try:
            contact = preprocess.parse_contact(raw_contact)['text']
            score = int(raw_score)
            scores[contact] = score
        except (KeyError, ValueError):
            logging.error(f'skipping {raw_contact=} {raw_score=}')

    return scores

def score(match, start_time, messages, *, closing_time=timedelta(minutes=15)):
    stop_time = datetime.fromisoformat(match['date'])
    played_teams = tuple(teams.find_teams(match['teams']))
    winning_team = first(team for team in played_teams if match['winner'].lower() == team['name'].lower())
    draw = True

    if winning_team:
        winning_team_keys = team_as_keys(winning_team)
    elif draw:
        winning_team_keys = chain.from_iterable(map(team_as_keys, played_teams))
    else:
        error_handle

    acceptable_messages = tuple(winning_team_keys)

    oldest_entry_by_contact = dict()

    for entry in preprocess.preprocess_texts(messages):
        contact = entry['contact']['text']
        previous_entry = oldest_entry_by_contact.get(contact, None)
        if not previous_entry:
            # go, keep going
            max_datetime = datetime(
                day=31, month=12, year=MAXYEAR,
                hour=23, minute=59, second=59,
                tzinfo=entry['date'].tzinfo
            )
            previous_entry = {'date': max_datetime}

        if (
                (entry['date'] < previous_entry['date'])
                and (start_time <= entry['date'] < stop_time)
        ):
            entry['additonal_score'] = int(entry['message'] in acceptable_messages)
            oldest_entry_by_contact[contact] = entry

    return oldest_entry_by_contact


def merge_old_and_new_entries_to_rows(*, new_entries, old_scores):
    existing_scores_by_contact = old_scores
    entries_by_contact = new_entries

    rows = []
    for (contact, entry) in entries_by_contact.items():
        try:
            existing_score = existing_scores_by_contact[contact]
            del existing_scores_by_contact[contact]
        except KeyError:
            existing_score = 0
        new_score = existing_score + entry['additonal_score']
        guess = entry['message']

        rows.append((contact, new_score, guess))

    leftover = existing_scores_by_contact
    for (contact, score) in leftover.items():
        rows.append((contact, score, ''))

    return rows

def generate_new_sheet_name(*, match):
    match_time = datetime.fromisoformat(match['date']).strftime("%d %b, %H:%M")
    team_abbrs = ' vs '.join(team['abbr'] for team in teams.find_teams(match['teams']))

    return f"{team_abbrs} -- {match_time}"
    return sheet_name
