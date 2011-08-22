'''A simple cache simulator.

See 'python ./cache_simulator.py --help' for information on how to run.

@author: Jens Rantil <jens.rantil@telavox.se>
'''
import sys
import itertools
from optparse import OptionParser
import datetime
from time import mktime
import time
import string


DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_SEPARATOR = None
DEFAULT_TTL = 60 # in seconds


class CacheKeyValue:
    def __init__(self, key, current_time, ttl):
        self.key = key
        destruction_time = current_time + ttl
        self.time_to_destruct = destruction_time
        self.last_updated = current_time
        self.insert_time = current_time
        

class Cache(object):
    """A simple cache simulator."""
    keyvalues = {}
    current_time = None
    
    def __init__(self, ttl=0):
        """Constructor.

        ttl - number of seconds each cached value shall live
        """
        self.ttl = datetime.timedelta(seconds=ttl)
        
    def put(self, key, value=None):
        """Put a key-value in the cache.
        
        key -- the key.
        value -- the value.
        
        >>> c = Cache(60)
        >>> import datetime
        >>> c.current_time = datetime.datetime(2011, 8, 22, 22, 20, 4, 837005)
        >>> c.ttl
        datetime.timedelta(0, 60)
        >>> c.put("key")
        >>> c.put("key", "avalue")
        >>> c.put(5, "anothervalue")
        >>> c.put(5, "a third value")
        """
        if self.current_time is None:
            raise RuntimeError("current_time has not been set. I don't know"
                               " when this value should be removed from the"
                               " cache.")
        self.keyvalues.setdefault(key, CacheKeyValue(key, self.current_time,
                                                  self.ttl))
        self.keyvalues[key].value = value
    
    def is_cached(self, key):
        self._expire_old_keys()
        #print self.keyvalues.keys()
        return self.keyvalues.has_key(key)
    
    def get(self, key):
        """Put a key-value in the cache.
        
        key -- the key.
        value -- the value.
        
        >>> c = Cache(60)
        >>> import datetime
        >>> c.current_time = datetime.datetime.now()
        >>> c.get("key")
        Traceback (most recent call last):
          File "/usr/lib/python2.6/doctest.py", line 1248, in __run
            compileflags, 1) in test.globs
          File "<doctest cache_simulator.Cache.get[3]>", line 1, in <module>
            c.get("key")
          File "cache_simulator.py", line 80, in get
            return self.keyvalues[key]
        KeyError: 'key'
        >>> c.put("key")
        >>> c.put("key", "avalue")
        >>> c.put(5, "anothervalue")
        >>> c.put(5, "a third value")
        >>> c.get(5).value
        'a third value'
        """
        self._expire_old_keys()
        return self.keyvalues[key]
    
    def _expire_old_keys(self):
        """Expire keys that are no longer valid.
        
        This method could be made way faster by utilizing an ordered list of key
        for when they are to be expired. However, this method works for now.
        """
        for key in self.keyvalues.keys():
            if self.keyvalues[key].time_to_destruct < self.current_time:
                #print "Deleting expired key: %s" % key
                del self.keyvalues[key]
         
                
    def _get_size(self):
        self._expire_old_keys()
        return len(self.keyvalues)
    size = property(_get_size)


class CacheStatistics:
    """Responsible for keeping track of cache statistics.

    Example:
    >>> cs = CacheStatistics()
    >>> cs.register_hit()
    >>> cs.register_get()
    >>> cs.register_get()
    >>> cs.register_get()
    >>> cs.register_size(4)
    >>> cs.register_size(6)
    >>> cs.register_size(5)
    >>> cs.print_stats()
    FINAL STATISTICS:
    ==============================
    Total gets: 3
          Hits: 1
        Misses: 2
      Max size: 6
    ==============================
    """
    def __init__(self):
        self.hits = 0
        self.gets = 0
        self.maxsize = None
        
    def register_size(self, new_size):
        """Register the current size of the cache."""
        self.maxsize = max(self.maxsize, new_size)
        
    def register_hit(self):
        """Register a cache hit."""
        self.hits += 1

    def register_get(self):
        """Register a cache get."""
        self.gets += 1
        
    def print_stats(self):
        WIDTH = 30
        print "FINAL STATISTICS:"
        print "=" * WIDTH
        for key, value in (("Total gets", self.gets),
                           ("Hits", self.hits),
                           ("Misses", self.gets-self.hits),
                           ("Max size", self.maxsize)):
            print "%10s: %s" % (key, value)
        print "=" * WIDTH

        
def my_open(filename):
    """A file opener that can handle stdin."""
    if filename=='-':
        return sys.stdin
    else:
        return open(filename)


def parse_line(options, line):
    """Parse a line.

    >>> class Dummy: pass
    >>> options = Dummy()
    >>> options.separator = None
    >>> options.dateformat = '%d/%b/%Y:%H:%M:%S'
    >>> parse_line(options, '17/Apr/2011:07:23:20 /home/login.jsp')
    (datetime.datetime(2011, 4, 17, 7, 23, 20), '/home/login.jsp')
    """
    pieces = line.rstrip("\r\n").split(options.separator)
    parsed_date = time.strptime(pieces[0], options.dateformat)
    timestamp = datetime.datetime.fromtimestamp(mktime(parsed_date))
    key = string.join(pieces[1:], options.separator if options.separator else " ")
    return timestamp, key


def lines(openfiles):
    """Step through the lines of open files.
    
    Example:
    >>> f = open('test.txt', 'w')
    >>> f.write('hej\\n')
    >>> f.write('pek\\n')
    >>> f.close()
    >>> [line for line in lines([open('test.txt', 'r')])]
    ['hej\\n', 'pek\\n']
    """
    for file in openfiles:
        for line in file:
            yield line


def run(options):
    """Run the application."""
    if not options.inputfiles:
        options.inputfiles.append('-')
        
    cache = Cache(options.ttl)
    stats = CacheStatistics()
    inputfiles = []

    try:
        inputfiles = map(my_open, options.inputfiles)
        for line in lines(inputfiles):
            timestamp, key = parse_line(options, line)
            cache.current_time = timestamp
            stats.register_get()
            if not cache.is_cached(key):
                cache.put(key)
            else:
                stats.register_hit()
            stats.register_size(cache.size)
    except IOError, e:
        print "Could not open a file: %s", e.message
        return 1
    finally:
        for f in inputfiles:
            f.close()
            
    stats.print_stats()
    
    return 0


def command_line_parser():
    """Construct the command line parser.
    
    >>> a = command_line_parser()
    """
    USAGE = "%prog [options] -f <infile1> -f <infile2> ... -f <infileN>"
    DESCRIPTION = "A simple cache simulator."
    parser = OptionParser(usage=USAGE, description=DESCRIPTION)
    parser.add_option('-t', '--ttl', default=DEFAULT_TTL, type='int',
                      help="Time to live before a cached value is expired (in"
                           " seconds). Default is %d." % DEFAULT_TTL)
    parser.add_option('-f', '--inputfile', dest="inputfiles", action="append",
                      help="An input file consisting of one event per line."
                           " Each line starts with a date, followed by a"
                           " separator and a cache key. If no input file is"
                           " specified stdin is expected.")
    parser.add_option('-s', '--separator', default=DEFAULT_SEPARATOR,
                      help="The separator to use between the date and the key."
                           " Defaults to '%s'." % DEFAULT_SEPARATOR)
    parser.add_option('-d', '--dateformat', default=DEFAULT_DATE_FORMAT,
                      help="Date format (default=%s). See"
                           " http://docs.python.org/library/datetime.html for"
                           " information about the date format markup"
                           " language." % DEFAULT_DATE_FORMAT)
    return parser


def main(argv):
    """Parse the input to the cache simulator and executes the program.
    
    >>> main(['./cache_simulator.py', '-d', '%d/%b/%Y:%H:%M:%S', '-f', '../resources/sample_log.txt'])
    FINAL STATISTICS:
    ==============================
    Total gets: 29
          Hits: 12
        Misses: 17
      Max size: 6
    ==============================
    0
    """
    options, args = command_line_parser().parse_args(argv)
    if not options.inputfiles:
        options.inputfiles = ['-']
    if args[1:]:
        print args
        parser.print_help()
        return 1
    return run(options)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
