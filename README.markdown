Simple Log Analysis Tools
=========================
A set of small useful tools for various log analysis in the command
line.

The toolset
-----------
### histogram.py
Generates an ASCII histogram based on row frequency.

Example:

```bash
$ cat > tmpfile                                                                                                                                          [21:24:30]
a
b
a
a
c
$ cat tmpfile| python histogram.py                                                                                                                     [21:24:57]
a: ################################################################################ (3)
b: ########################## (1)
c: ########################## (1)
```

### cache_simulator.py
Used to simulate how a cache could improve performance given a list of
`<timestamp, requests>` pairs from a text file. The cached key-values are
expired TTL seconds after last usage.

Usage:

```bash
python cache_simulator.py --help                                                                                                                     [21:54:46]
usage: cache_simulator.py [-h] [-t TTL] [-s SEPARATOR] [-d DATEFORMAT]
                          [inputfiles [inputfiles ...]]

A simple cache simulator.

positional arguments:
  inputfiles            An input file consisting of one event per line. Each
                        line starts with a date, followed by a separator and a
                        cache key. If no input file is specified stdin is
                        expected.

optional arguments:
  -h, --help            show this help message and exit
  -t TTL, --ttl TTL     Time to live before a cached value is expired (in
                        seconds). Default is 60.
  -s SEPARATOR, --separator SEPARATOR
                        The separator to use between the date and the key.
                        Defaults to 'None'.
  -d DATEFORMAT, --dateformat DATEFORMAT
                        Date format (default=%Y-%m-%d). See
                        http://docs.python.org/library/datetime.html for
                        information about the date format markup language.
```

Author
------
Jens Rantil, <jens.rantil@gmail.com>.
