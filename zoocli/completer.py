import readline

from zoocli.paths import SEPARATOR, ROOT_PATH


class Completer(object):

    def __init__(self, cli):
        self._cli = cli
        self._completions = {}

    def complete(self, text, state):
        completions = []

        buffer = readline.get_line_buffer()

        if ' ' in buffer.lstrip():
            command, kwargs = self._cli.parse(*buffer.split())

            method = self._completions.get(command, self.ls)
            completions = method(**kwargs)
        else:
            completions = [command.name for command in self._cli.args.commands]

        completions = [c for c in completions
                       if c.startswith(text)]

        if state < len(completions):
            return completions[state]
        else:
            return None

    def ls(self, path=None, **kwargs):
        if path and not path.endswith(SEPARATOR):
            # List one level up
            absolute = path.startswith(ROOT_PATH)
            path = SEPARATOR.join(path.split(SEPARATOR)[:-1])
            if absolute:
                path = ROOT_PATH + path

        return self._cli.commands.ls(path=path).split()
