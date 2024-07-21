import sys
from typing import List, Optional


def load_container(packages: Optional[List[str]] = None, verbose: bool = False):
    from container import DynamicContainer
    container = DynamicContainer(verbose)
    if not packages: packages = ['commands']
    container.wire(modules=[__name__], packages=packages)
    container.IConfigurationProvider().load()
    return container

def load_container_to_context(ctx, packages: Optional[List[str]] = None):
    if ('--help' not in sys.argv) and ('-h' not in sys.argv):
        ctx.obj.container = load_container(packages, ctx.obj.verbose)