from climb.args import Args
from climb.config import config


class ZooArgs(Args):

    def _load_commands(self):
        ls = self._add_command("ls", "list resources")
        ls.add_argument("-l", action="store_true", help="long listing", dest="long")
        ls.add_argument("path", nargs="?", default=None,  help="node path (defaults to current)")

        cd = self._add_command("cd", "change current path")
        cd.add_argument("path", nargs="?", default=None,  help="node path (defaults to /)")

        get = self._add_command("get", "get node's data")
        get.add_argument("path", nargs="?", default=None,  help="node path (defaults to current")

        set = self._add_command("set", "set node's data")
        set.add_argument("path", nargs="?", default=None,  help="node path")
        set.add_argument("data", nargs="?", default=None,  help="data to set")

        editor = self._add_command(config['zoocli']['editor'], "edit node's data in the best editor possible")
        editor.add_argument("path", nargs="?", help="node to be edited")
        editor.set_defaults(command='editor')

        create = self._add_command("create", "create new node")
        create.add_argument("path", nargs="?", default=None,  help="node path")
        create.add_argument("-e", action="store_true", help="ephemeral", dest="ephemeral")
        create.add_argument("-p", action="store_true", help="create parent nodes if needed", dest="makepath")
        create.add_argument("-s", action="store_true", help="sequence", dest="sequence")
        create.add_argument("data", nargs="?", default=None,  help="data to set")

        rm = self._add_command("rm", "remove node")
        rm.add_argument("-r", action="store_true", help="recursive", dest="recursive")
        rm.add_argument("path", nargs="?", default=None,  help="node path")

        stat = self._add_command("stat", "get node's details")
        stat.add_argument("path", nargs="?", default=None,  help="node path (defaults to current")

        getacl = self._add_command("getacl", "show node's ACL")
        getacl.add_argument("path", nargs="?", default=None,  help="node path (defaults to current")

        addacl = self._add_command("addacl", "add new ACL for node")
        addacl.add_argument("path", nargs="?", default=None,  help="node path")
        addacl.add_argument("permissions", nargs="?", default=None,  help="ACL permissions")
        addacl.add_argument("scheme", nargs="?", default=None,  help="ACL scheme")
        addacl.add_argument("id", nargs="?", default=None,  help="ACL id")

        rmacl = self._add_command("rmacl", "remove node's ACL")
        rmacl.add_argument("path", nargs="?", default=None,  help="node path")
        rmacl.add_argument("index", nargs="?", default=None, help="ACL index")

        find = self._add_command("find", "find all sub-nodes")
        find.add_argument("path", nargs="?", default=None,  help="node path")
        find.add_argument("-name", nargs="?", default=None, help="name pattern", dest="name_filter")
        find.add_argument("-mindepth", nargs="?", default=None, help="min depth")
        find.add_argument("-maxdepth", nargs="?", default=None, help="max depth")
