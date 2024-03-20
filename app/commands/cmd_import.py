# from dependency_injector.wiring import Provide, inject
import rich_click as click
from actions import ImportTransactions, ListAvailableExports

@click.group("import")
@click.pass_context
# @inject
def cli(ctx):
    """Command to import transactions
    """
    pass

@click.command('from_csv')
@click.option('-f', "file_name", required=False, type=click.STRING)
@click.option('-o', "folder_name", required=False, type=click.STRING)
@click.pass_context
# @inject
def import_transactions(ctx, file_name: str, folder_name: str):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    importer = ImportTransactions()
    importer.import_transactions(file_name, folder_name)

@click.command('list_exports')
@click.argument("folder_name", type=click.STRING)
@click.pass_context
# @inject
def list_exports(ctx, folder_name: str):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    importer = ListAvailableExports()
    importer.list_exports_in_directory(folder_name)

cli.add_command(import_transactions)
cli.add_command(list_exports)
