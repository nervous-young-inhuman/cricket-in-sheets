import logging
from functools import lru_cache
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .helpers import first
from .shhhhhh import google_creds

def get_service(*build_args):
    creds = google_creds
    if not creds or not creds.valid:
        pass
    try:
        service = build(*build_args, credentials=creds)
        return service
    except HttpError as err:
        pass

def get_sheets_service():
    service = get_service('sheets', 'v4')
    if not service:
        return
    return service.spreadsheets()


class SheetsException(Exception):
    pass


class Sheets(object):
    def __init__(self, *, spreadsheet_id):
        self._service = get_sheets_service()
        self._id = spreadsheet_id

        if not self._service:
            raise SheetsException('Failed to get sheets service')

    def set_spreadsheet_id(self, id):
        self._id = id

    def get(self, *,
        spreadsheet_id=None,
        fields='spreadsheetId,spreadsheetUrl,properties(title,timeZone),sheets(properties(sheetId,title,index))',
    ):
        if not spreadsheet_id:
            spreadsheet_id = self._id
        try:
            response = self._service.get(
                spreadsheetId=spreadsheet_id,
                fields=fields
            ).execute()
        except HttpError as err:
            logging.error(err)
            raise SheetsException(f'Failed to get fetch spreadsheet {spreadsheet_id}')

        if not response:
            raise SheetsException(f'Failed to get fetch spreadsheet {spreadsheet_id}')
        return response

    def values(self, *, range, spreadsheet_id=None, dimension='ROWS', fields='values'):
        if not spreadsheet_id:
            spreadsheet_id = self._id

        try:
            response = self._service.values().get(
                spreadsheetId=spreadsheet_id,
                range=range,
                majorDimension=dimension,
                fields=fields,
            ).execute()
            if fields == 'values':
                return response.get('values', [])
            return response
        except HttpError as err:
            logging.error(err)
            raise SheetsException(f'Failed to get fetch spreadsheet range = "{range}"')

    def clear(self, *, range, spreadsheet_id=None):
        if not spreadsheet_id:
            spreadsheet_id = self._id

        try:
            response = self._service.values().clear(
                spreadsheetId=spreadsheet_id,
                range=range,
            ).execute()
            return response
        except HttpError as err:
            logging.error(err)
            raise SheetsException(f'Failed to get clear spreadsheet range = "{range}"')

    def append(self, *, range, values, dimension='ROWS', spreadsheet_id=None):
        if not spreadsheet_id:
            spreadsheet_id = self._id

        value_range = {
            "range": range,
            "majorDimension": dimension,
            "values": values,
        }
        try:
            response = self._service.values().append(
                spreadsheetId=spreadsheet_id,
                range=range,
                valueInputOption='RAW',
                insertDataOption='OVERWRITE',
                includeValuesInResponse=False,
                body=value_range,
            ).execute()
            return response
        except HttpError as err:
            logging.error(err)
            raise SheetsException(f'Failed to append values to spreadsheet range = "{range}"')

    def sheets(self):
            fields = 'sheets(properties(sheetId,title,index))'
            return self.get(fields=fields).get('sheets', [])

    def sheet_properties(self, *, sheet_name, sheet_id, sheets=None):
            if not sheet_name and (sheet_id is None):
                raise SheetsException('sheet_name and sheet_id one of them is expected to be non empty.')

            if not sheets:
                sheets = self.sheets()

            sheet_properties = first(
                dict(id=sp.get('sheetId'), name=sp.get('title'))
                for sheet in sheets
                if (sp := sheet.get('properties')) and
                ((sp.get('sheetId', {}) == sheet_id)
                 or (sp.get('title', {}) == sheet_name))
            )
            if not sheet_properties:
                # ye it may look weird when one of them is None. In which case ignore :)
                raise SheetsException(f'No sheet found by {sheet_name=} or {sheet_id=}')

            return sheet_properties


    def duplicate(self, *, spreadsheet_id=None, source_sheet_id, new_sheet_name=None, new_sheet_idx=86):
        if spreadsheet_id is None:
            spreadsheet_id = self._id
        if not new_sheet_name:
            new_sheet_name = datetime.datetime.now().strftime('%d %b, %H:%M')

        requests = [
            {
                "duplicateSheet": {
                    "sourceSheetId": source_sheet_id,
                    "insertSheetIndex": new_sheet_idx,
                    "newSheetName": new_sheet_name,
                },
            },
        ]
        body = dict(requests=requests, includeSpreadsheetInResponse=False)
        try:
            response = self._service.batchUpdate(spreadsheetId=spreadsheet_id, body=body,).execute()
            return response
        except HttpError as err:
            logging.error(err)
            raise SheetsException(f'Failed to duplicate spreadsheet page')
