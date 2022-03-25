import json
from itertools import chain
from functools import lru_cache
from helpers import first

@lru_cache
def teams():
    with open('./data/teams.json') as f:
        return json.load(f)

def teams_as_text_keys():
    return chain.from_iterable(
        (team['name'].lower(), team['abbr'].lower())
        for team in teams()
    )

def find_teams(raw_team_names):
    team_names = [team_name.lower() for team_name in raw_team_names]
    return (
        team
        for team in teams()
        if (team['abbr'].lower() in team_names) or (team['name'].lower() in team_names)
    )

def find_team(team_name):
    return first(find_teams([team_name.lower()]))

TEAM_KEYS = tuple(teams_as_text_keys())
