import structlog
import logging
from structlog import BoundLogger

def get_logger(verbose: bool = True) -> BoundLogger:
    if verbose:
        structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG))
    else:
        structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))

    return structlog.get_logger()