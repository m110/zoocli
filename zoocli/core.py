from climb import Climb
from functools import partial

from zoocli.args import ZooArgs
from zoocli.commands import ZooCommands
from zoocli.completer import ZooCompleter


ZooCLI = partial(Climb,
                 'zoocli',
                 args=ZooArgs,
                 commands=ZooCommands,
                 completer=ZooCompleter)
