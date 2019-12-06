import os
import logging
from time import time
import datetime
from lantz.core import UnitRegistry, Q_
__version__ = 0.2

# units
ur = UnitRegistry()
# logger format

# new
package_path = os.path.dirname(__file__)            #   ###/###/hyperion/hyperion/
repository_path = os.path.dirname(package_path)     #   ###/###/hyperion/
parent_path = os.path.dirname(repository_path)      #   ###/###/
log_path = os.path.join(parent_path, 'logs')        #   ###/###/logs/

# make log dir if it doesn't exist:
if not os.path.isdir(log_path):
    os.makedirs(log_path)

# keep root_dir for backward compatability
root_dir = os.path.dirname(__file__)

ls = os.pardir


# define a list of colors to plot
_colors = ['#1f77b4','#aec7e8','#ff7f0e','#ffbb78', '#2ca02c','#98df8a', '#d62728','#ff9896','#9467bd','#c5b0d5',
            '#8c564b','#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']


# Setting up logging =================================================

# Not strictly necessary for the logger
class Singleton(type):
    """
    Metaclass to use for classes of which you only want one instance to exist.
    use like: class MyClass(ParentClass, metaclass=Singleton):
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DuplicateFilter(logging.Filter):
    """Adding this filter to a logging handler will reduce repeated """

    def filter(self, record):
        # Note to self. It appears the message from one handler is passed to the next one.
        # This means that if one handler modifies the message, the next one gets the modified version.
        self.repeat_message = ' > Logger message is being repeated...'
        # First strip the repeat_message from the message if it is there:
        replen = len(self.repeat_message)
        if len(record.msg) > replen and record.msg[-replen:] == self.repeat_message:
            record.msg = record.msg[:-replen]
        # Combine filename, linenumber and (corrected) message to create a record to compare
        current_record = (record.module, record.lineno, record.msg)
        # Compare it to the last record stored (if that variable exists)
        if current_record != getattr(self, "last_record", None):
            self.last_record = current_record  # store the current record in last_record, to be able to compare it on the next call
            self.last_unique_time = time()  # store the time of this message
            self.repeating = False  # set repeating flag to False
            return True  # Allow this record to be printed
        else:
            if not self.repeating:
                self.repeating = True  # set repeating flag True
            elif time() > self.last_unique_time + 20:  # if repeting==True AND 20 seconds have passed reset "timer"
                self.last_unique_time = time()  # reset the last_unique_time to in order repeat occasionally
            else:
                return False  # prevent message from being printed during those 20 seconds
            record.msg += self.repeat_message  # append repeat message
            return True  # allow the message to be printed


class CustomFormatter(logging.Formatter):
    # length = ['compact', 'medium', 'full']
    def __init__(self, compact=False):
        self.compact = compact
        super(CustomFormatter, self).__init__()

    def format(self, record):
        module = record.name
        func = record.funcName
        if self.compact:
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            # module = '.'.join(module.split('.')[1:])  # strip off the first word before '.'(i.e. hyperion)
            if len(module) > 38:
                module = '...' + module[-35:]  # truncate from the left to 38 characters
                msg = '{:.30}'.format(record.msg)  # truncate to 30 characters
            if len(func) > 20:
                func = func[:17] + '...'
            message = '{} |{:>38} | {:22}|{:>8} | {}'.format(timestamp, module, func + '()', record.levelname,
                                                             record.msg)
        else:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[
                        :-3]  # show 3 out of 6 digits (i.e. milliseconds)
            # module = module[-min(len(module), 50):]       # truncate from the left to 50 characters
            # msg = '{:.200}'.format(record.msg)            # truncate to 200 characters
            # if len(func)>30:
            #     func = func[:27]+'...'
            message = '{} |{:>50} | {:32}|{:>8} | {}'.format(timestamp, module, func + '()', record.levelname,
                                                             record.msg)
        return message


class LoggingManager:

    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG

    _level_2_number = {'CRITICAL': CRITICAL, 'ERROR': ERROR, 'WARNING': WARNING, 'WARN': WARN, 'INFO': INFO,
                       'DEBUG': DEBUG}
    _number_2_level = {CRITICAL: 'CRITICAL', ERROR: 'ERROR', WARNING: 'WARNING', INFO: 'INFO', DEBUG: 'DEBUG'}

    def __init__(self, name=None, filename=None):
        #        if name is None:
        #            name = __name__
        #        super().__init__(name)

        self._logger_format_long = '%(asctime)s |%(name)+50s | %(funcName)+30s() |%(levelname)+7s | %(message)s'
        self._logger_format_short = '%(asctime)s |%(module)+22s | %(funcName)+22s()|%(levelname)+7s | %(message).40s'
        # _logger_format_short = '%(asctime)s.%(msecs).3d |%(module)+22s | %(funcName)+22s()|%(levelname)+7s | %(message).40s'
        # note: by adding ,'%H:%M:%S' to the Formatter (asctime) will turn into HH:MM:SS

        # create handler for stream logging:
        self.stream_handler = logging.StreamHandler()

        # stream_logger.setFormatter(logging.Formatter(_logger_format_short, '%H:%M:%S')) # adding the ,'%H:%M:%S' changes the timestamp to the short version
        self.stream_handler.setFormatter(CustomFormatter(compact=True))
        self.stream_handler.setLevel(self.DEBUG)  # default level for stream handler
        self.stream_handler.addFilter(DuplicateFilter())

        if filename is not None:
            self._log_path = os.path.dirname(filename)
            fname = os.path.base(filename)
        else:
            self._log_path = log_path
            fname = 'hyperion.log'

            # make log dir if it doesn't exist:
        if not os.path.isdir(log_path):
            os.makedirs(log_path)

        # create handler for file logging:
        self._default_log_filename = os.path.join(self._log_path, fname)
        self.file_handler = logging.handlers.RotatingFileHandler(filename=self._default_log_filename,
                                                                 maxBytes=(5 * 1024 * 1024), backupCount=9)
        # file_logger.setFormatter(logging.Formatter(_logger_format_long))
        self.file_handler.setFormatter(CustomFormatter())
        self.file_handler.setLevel(self.DEBUG)  # default level for file handler
        self.file_handler.addFilter(DuplicateFilter())

    @property
    def stream_level(self):
        return self._number_2_level[self.stream_handler.level]

    @stream_level.setter
    def stream_level(self, number_or_string):
        self.stream_handler.setLevel(number_or_string)

    @property
    def file_level(self):
        return self._number_2_level[self.file_handler.level]

    @file_level.setter
    def file_level(self, number_or_string):
        self.file_handler.setLevel(number_or_string)

    #    @property
    #    def stream_enable(self):
    #        return self.stream_handler in self.handlers
    #
    #    @stream_enable.setter
    #    def stream_enable(self, boolean):
    #        self._enable(boolean, self.stream_handler)
    #
    #    @property
    #    def file_enable(self):
    #        return self.file_handler in self.handlers
    #
    #    @file_enable.setter
    #    def file_enable(self, boolean):
    #        self._enable(boolean, self.file_handler)

    def _enable(self, boolean, handler):
        # Helper function
        state = handler in self.handlers
        if boolean is not state:
            if boolean:
                self.addHandler(handler)
            else:
                self.removeHandler(handler)

    def getLogger(self, name=None):
        if name is None:
            name = __name__

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.handlers = []
        logger.addHandler(self.stream_handler)
        logger.addHandler(self.file_handler)
        return logger

# Initialize logger object. Import this in other modules inside this package.
log = LoggingManager()

# HOW TO USE THE LOGGING
# At the beginning of a file use: import hyperion
# Also import logging (or otherwise type hyperion.logging.X everywhere you would type logging.X)
# After that use this anywhere: self.logger = logging.getLogger(__name__)
# To change the logging file use this anywhere:
# hyperion.set_logfile('new_name')
# hyperion.set_logfile('new_name', 'my_folder')
# To modify the levels use this anywhere :
# hyperion.file_logger.setLevel( logging.INFO )
# hyperion.stream_logger.setLevel( logging.WARNING )