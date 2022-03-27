from datetime import datetime
from pathlib import Path
from functools import partial

from . import cricket
from . import scoring
from .sheets import Sheets
from .shhhhhh import DEFAULT_SPREADSHEET

def get_all_text(file_path):
    with open(file_path, 'rb') as f:
        return f.read()
def dummy_messages():
    messages = (
        '[24/03/22, 8:13:20 PM] Khader: CSK',
        '[25/03/22, 4:10:10 AM] Darth Vader: CSK',
        '[25/03/22, 5:20:20 AM] Khader: Kolkata Bannathe Bisiyo Riders',
        '[25/03/22, 5:20:25 AM] Khader: Kolkata Knight Riders',
        '[25/03/22, 8:15:20 PM] Darth Vader: KKR',
        '[25/03/22, 9:33:44 PM] Ellie: Wunder land',
        '[25/03/22, 9:33:44 PM] Denzel: Belliyo land',
        '[25/03/22, 9:33:44 PM] Denzel: just land',
        '[26/03/22, 7:33:15 PM] Ellie: KKR',
    )
    return b'\r\n'.join(map(partial(bytes, encoding='utf-8'), messages))

def validate_match(match):
    required = ('date', 'winner', 'teams', 'id', 'status')
    for field in required:
        if field not in match:
            raise cricket.CricketException(f'{field} not found in {match}.')

def main():
    spreadsheet_id = DEFAULT_SPREADSHEET.ID
    sheets_obj = Sheets(spreadsheet_id=spreadsheet_id)

    sheets_cache = sheets_obj.sheets()
    sheet_properties = sheets_obj.sheet_properties(
        sheet_id=DEFAULT_SPREADSHEET.SHEET_ID,
        sheet_name=DEFAULT_SPREADSHEET.SHEET_NAME,
        sheets=sheets_cache,
    )
    old_scores = scoring.get_existing_scores(
        sheet_obj=sheets_obj,
        sheet_name=sheet_properties['name'],
    )

    match_id = "341e6690-ece0-4dce-83fc-91effbb28eb3"
    match = cricket.match(match_id)
    validate_match(match)

    start_time = datetime.fromisoformat('2022-03-24T14:00:00+00:00')
    # chat_file_path = ''

    # messages = get_all_text(chat_file_path)
    messages = dummy_messages()
    new_entries = scoring.score(match, start_time, messages)

    rows = scoring.merge_old_and_new_entries_to_rows(new_entries=new_entries, old_scores=old_scores)
    new_sheet_name = scoring.generate_new_sheet_name(match=match)
    sheets_obj.duplicate(
        source_sheet_id=sheet_properties['id'],
        new_sheet_name=new_sheet_name
    )
    sheets_obj.clear(range=sheet_properties['name'])
    sheets_obj.append(range=sheet_properties['name'], values=rows)

    new_scores =  get_existing_scores(
        sheet_obj=sheets_obj,
        sheet_name=sheet_properties['name'],
    )

    print(f"{new_sheet_name=} {sheet_properties=}")
    print(old_scores, '\n'*4, new_scores)


if __name__ == '__main__':
    main()
