import rich_click as click
from dependency_injector.wiring import Provide, inject
from actions import (CodeTransactions,
                     DumpSheetToCSV, 
                     GroupPayees, 
                     ListByCategory, 
                     GetWeeklyTransactions, 
                     CleanupExports, 
                     GetSpendAtPayee)

@click.group("import")
@click.pass_context
@inject
def cli(ctx):
    """Command to import transactions
    """
    if ctx.obj.load_container: 
        ctx.obj.load_container(ctx)

@click.command('from_csv')
@click.option('-f', "file_name", required=False, type=click.STRING)
@click.option('-o', "folder_name", required=False, type=click.STRING)
@click.pass_context
@inject
def import_transactions(ctx, file_name: str, folder_name: str, action = Provide["IImportTransactions"]):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    action.import_transactions(file_name, folder_name)

@click.command('list_exports')
@click.argument("folder_name", type=click.STRING)
@click.pass_context
@inject
def list_exports(ctx, folder_name: str, action = Provide["IListAvailableExports"]):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    action.list_exports_in_directory(folder_name)

@click.command('code')
@click.pass_context
# @inject
def code_transactions(ctx):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    coder = CodeTransactions()
    coder.code_transactions()

@click.command('dump')
@click.argument('destination', type=click.STRING)
@click.pass_context
# @inject
def dump(ctx, destination):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    dump = DumpSheetToCSV()
    dump.to_csv(destination=destination)

@click.command('group_payees')
@click.pass_context
# @inject
def group_payees(ctx):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    grouper = GroupPayees()
    grouper.group()

@click.command('list_by_category')
@click.pass_context
@inject
def list_by_category(ctx, action = Provide("IListSpendByCategory")):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    action.list_by_category()

@click.command('weekly_transactions')
@click.option('-r', 'rweek', type=click.INT, help='Specify the relative week you want to list')
@click.option('-y', 'year', type=click.INT, help='Specify the year you want to list')
@click.pass_context
# @inject
def weekly_transactions(ctx, year: int = 0, rweek: int = 0):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    grouper = GetWeeklyTransactions()
    grouper.list_weekly_transactions(year, rweek)

@click.command('cleanup_exports')
@click.argument("folder_name", type=click.STRING)
@click.pass_context
# @inject
def cleanup_exports(ctx, folder_name: str):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    importer = CleanupExports()
    importer.remove_export_files_from_folder(folder_name)

@click.command('list_payee_spend')
@click.pass_context
# @inject
def list_payee_spend(ctx):
    '''
    Import transactions to the spreadsheet from a CSV dump of transactions
    '''
    get_spend = GetSpendAtPayee()
    get_spend.list_spend_at_payee()



cli.add_command(import_transactions)
cli.add_command(list_exports)
cli.add_command(code_transactions)
cli.add_command(dump)
cli.add_command(group_payees)
cli.add_command(list_by_category)
cli.add_command(weekly_transactions)
cli.add_command(cleanup_exports)
cli.add_command(list_payee_spend)
