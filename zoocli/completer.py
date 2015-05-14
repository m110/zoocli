import readline

from zoocli.paths import SEPARATOR, ROOT_PATH


class Completer(object):

    def __init__(self, cli):
        self._cli = cli
        self._completions = {
            'ls': self.ls,
            'cd': self.ls,
        }

    def complete(self, text, state):
        completions = []

        buffer = readline.get_line_buffer()

        if ' ' in buffer.lstrip():
            command, kwargs = self._cli.parse(buffer.split())

            if command in self._completions:
                method = self._completions[command]
                completions = method(**kwargs)
        else:
            completions = [command.name for command in self._cli.commands]

        completions = [c for c in completions
                       if c.startswith(text)]

        if state < len(completions):
            return completions[state]
        else:
            return None

    def ls(self, path=None):
        if path and not path.endswith(SEPARATOR):
            # List one level up
            absolute = path.startswith(ROOT_PATH)
            path = SEPARATOR.join(path.split(SEPARATOR)[:-1])
            if absolute:
                path = ROOT_PATH + path

        return self._cli.ls(path).split()
