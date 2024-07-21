import os
from typing import Any, Callable, List
import rich_click as click
from commands.load_container import load_container_to_context
from commands import command_list


click.rich_click.USE_RICH_MARKUP = True
CONTEXT_SETTINGS = dict(auto_envvar_prefix="COMPLEX")

class CLIContext(object):

    def __init__(self) -> None:
        self.load_container: Callable[..., None]
        self.container = None

context = click.make_pass_decorator(CLIContext)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))

class ComplexCLI(click.MultiCommand):

    def __init__(self, name: str | None = None, 
                 invoke_without_command: bool = False, 
                 no_args_is_help: bool | None = None, 
                 subcommand_metavar: str | None = None, 
                 chain: bool = False, 
                 result_callback: Callable[..., Any] | None = None, 
                 **attrs: Any) -> None:
        super().__init__(name, invoke_without_command, no_args_is_help, subcommand_metavar, chain, result_callback, **attrs)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter):
        click.rich_click.rich_format_help(self, ctx, formatter)

    def list_commands(self, ctx) -> List[str]:
        result = sorted(command_list)
        return result

    def get_command(self, ctx, name):
        try:
            # print(name)
            mod = __import__(f"commands.cmd_{name}", None, None, ["cli"])
        except ImportError as e:
            raise Exception(e.args)
        return mod.cli


@click.group(cls=ComplexCLI, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    """[black on blue]reporttool[/] is a commandline tool
    """
    # console = Console()
    try:
        ctx.obj = CLIContext()
        ctx.obj.verbose = False
        ctx.obj.load_container = load_container_to_context
    except Exception as e:
        pass

if __name__ == '__main__':
    cli()
