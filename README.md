# zoocli
Interactive command line tool for [Apache ZooKeeper](https://zookeeper.apache.org/).

**Note that this is still WIP and features described here may be not implemented at the moment.**

## Featuring:

* Basic and advanced operations.
* Clear interface.
* Better nodes listing.
* In-place edit of node's data.
* Full readline support with tab completions and searchable history.
* ...and more!

## Why?

Because I couldn't find interactive CLI that would suit my needs.

## Requirements

* [Python 3](http://python.org)
* [kazoo](https://github.com/python-zk/kazoo/)

## Installation

Get the source and run:

```
python3 setup.py install
cp /etc/zoocli/zoocli.example.conf /etc/zoocli/zoocli.conf
```

Then update config file to match your preferences.

# Usage

## Navigation

Use `cd` and `ls` commands to list nodes and move around.

```
[/]> cd zookeeper
[/zookeeper]> ls
one two three
[/zookeeper]> ls -l one
foo
bar
baz
```

## Management

* `cd <path>` - change current directory
* `ls [-l] <path>` - list child nodes
* `get <path>` - display node's data
* `set <path> <data>` - set node's data
* `$EDITOR <path>` - edit node's data in-place with your favorite editor
* `create [-eps] <path> [data]` - create new node
* `rm [-r] <path>` - remove node
* `stat <path>` - get detailed information about node
* `getacl <path>` - get node's ACL
* `setacl <path> <acl>` - set ACL on node

# Configuration

zoocli will attempt to read `./zoocli.conf`, `~/.zoocli.conf` and `/etc/zoocli/zoocli.conf` in that order.

Here is the configuration file explained.
```ini
[zoocli]
# Your favorite editor - this name will act as a command!
editor = vim
# Commands history file. Leave empty to disable.
history = ~/.zoocli_history
# Additional verbosity, if needed.
verbose = off

[zookeeper]
# In case of more hosts, use comma-separated values.
hosts = zk1:2181,zk2:2181
```

# Tips

## Batch mode

Any command can be passed directly as arguments to zoocli, which will exit just after after executing it. If you run it without arguments, you will get to interactive mode (preferable choice in most cases).
