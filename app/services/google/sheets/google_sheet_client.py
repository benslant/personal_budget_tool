from services.google.sheets.google_sheet_credentials import GoogleSheetCredentials
from gspread import authorize, Client


class GoogleSheetClient():

    def __init__(self,
                 credentials: GoogleSheetCredentials) -> None:
        self.credentials = credentials

    def get_client(self) -> Client:
        return authorize(self.credentials.get_credentials())