from services.configuration_service import ConfigurationService
from load_transactions_from_csv import CSVTransactionImporter 
from rich.console import Console
from rich.table import Table


class ListAvailableExports():

  def __init__(self,
               configuration: ConfigurationService) -> None:
    self.configuration = configuration

  def list_exports_in_directory(self, folder_name: str):
    console = Console()
    csv_importer = CSVTransactionImporter()

    sheet = self.configuration.get_value_by_key('google_sheet')
    sheet_id = sheet['spreadsheet_id']

    export_files = csv_importer.list_export_files_in_folder(folder_name)
    table = Table(title="Export Files", show_lines=True)
    table.add_column("File Name")
    table.add_column("Account Name")
    table.add_column("Account Number")
    table.add_column("From")
    table.add_column("To")
    table.add_column("Exported On")
    sorted_files = sorted(export_files, key=lambda e: e.to_date, reverse=True)
    for file in sorted_files:
        table.add_row(f'{file.folder_name}/{file.file_name}',
                      file.account.label,
                      str(file.account),
                      file.from_date.strftime('%d-%m-%Y'),
                      file.to_date.strftime('%d-%m-%Y'),
                      file.export_date.strftime('%d-%m-%Y'))

    console.print(table)

