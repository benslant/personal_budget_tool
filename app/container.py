from actions import *
from actions.import_action import ImportTransactions
from services import ConfigurationService, get_logger, TransactionCodeService
from services.google.sheets import GoogleSheetClient, GoogleSheetCredentials
from structlog import BoundLogger
from dependency_injector import containers, providers
from dependency_injector.providers import Singleton
from load_transactions_from_spreadsheet import SheetsTransactionImporter
from gspread import authorize, Client
from oauth2client.service_account import ServiceAccountCredentials


class DynamicContainer(containers.DynamicContainer):

    def __init__(self, verbose: bool = False) -> None:
        super().__init__()
        self.verbose = verbose
        self.ILogger: Singleton[BoundLogger] = providers.Singleton(get_logger, self.verbose)
        self.IConfigurationProvider: Singleton[ConfigurationService] = providers.Singleton(ConfigurationService , 
                                                                                           app_name = 'budgettool', 
                                                                                           logger=self.ILogger)    
        self.IConfigurationProvider().load()
        sheet = self.IConfigurationProvider().get_value_by_key('google_sheet')
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/ben.caldwell/Downloads/budgetspreadshe-f6204ad0981b.json', scope)
        self.gc: Client = authorize(credentials)
        self.sheets_importer = SheetsTransactionImporter(self.gc)
        self.ITransactionCodeService: Singleton[TransactionCodeService] = providers.Singleton(TransactionCodeService,
                                                                                              google_sheets_client=self.gc)
        self.IGoogleSheetCredentials: Singleton[GoogleSheetCredentials] = providers.Singleton(GoogleSheetCredentials,
                                                                                               configuration = self.IConfigurationProvider)
        self.IGoogleSheetClient: Singleton[GoogleSheetClient] = providers.Singleton(GoogleSheetClient,
                                                                                     credentials = self.IGoogleSheetCredentials)
        self.IImportTransactions: Singleton[ImportTransactions] = providers.Singleton(ImportTransactions,
                                                                                      sheets_importer = self.sheets_importer,
                                                                                      configuration=self.IConfigurationProvider)
        self.IListAvailableExports: Singleton[ListAvailableExports] = providers.Singleton(ListAvailableExports,
                                                                                          configuration=self.IConfigurationProvider)
        self.IListSpendByCategory: Singleton[ListByCategory] = providers.Singleton(ListByCategory,
                                                                                   sheets_importer = self.sheets_importer,
                                                                                   configuration=self.IConfigurationProvider)
        self.IGetWeeklyTransactions: Singleton[GetWeeklyTransactions] = providers.Singleton(GetWeeklyTransactions,
                                                                                   sheets_importer = self.sheets_importer,
                                                                                   configuration=self.IConfigurationProvider) 
        self.ICodeTransactions: Singleton[CodeTransactions] = providers.Singleton(CodeTransactions,
                                                                                  transaction_code_service=self.ITransactionCodeService,
                                                                                  sheets_importer=self.sheets_importer,
                                                                                  configuration=self.IConfigurationProvider)