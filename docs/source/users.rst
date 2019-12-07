==========
For Users
==========

If you just want to use some of the controllers to connect your computer
to your devices, this is the place to start.

First, make sure you install the package correctly, following the
instructions in the readme file of the project.

A nice place to start looking for examples on how to use
the package is the examples folder.

Features
--------
Here we enumerate a few of the features we included in the package and how to use them.

Logging
~~~~~~~

When we deal with projects tha have different layers and levels of complexity,
it is quite easy to loose track of who does what, specifically, when debugging or looking
for some unwanted behaviour. Additionally, even if the code works as expected, it is handy
to have some feedback of what is going on and when. For this, Python has the
logging module. Here we simply implemented the use of this module so the messages
any developer though to be pertinent are printed to the screen and also saved on a file.
This way, you can have immediate feedback and also a file where you can search for specific
information and post-process.

Since we want to use the same 'logger' in the project, we defined it in the init where
we called it 'log'. To use it in your classes, you need to do:

>>> from hyperion import log
>>> logger = log.getLogger(__name__)
>>> logger.info('An info message')
>>> logger.debug('A debug message')
16:54:49 |                              hyperion | <module>()            |    INFO | An info message
16:54:49 |                              __main__ | <module>()            |   DEBUG | A debug message

At the same time, it will save the same message in a folder called *logs* next to the
root folder containing the hyperion package in a file called hyperion.log

You may notice that in many of our classes we import the package with
the name 'logging' which can generate problems if you also use the
python standard logging package. We did this for backwards compatibility
of our code, for new code we recommend to follow the example above.

The default level for the log in the file and the screen is DEBUG.
in order to change it to any other option on the standard logging package,
for example, INFO, you have to do:

>>> from hyperion import log
>>> log.stream_level = logging.INFO
>>> logger = log.getLogger(__name__)
>>> logger.info('An info message')
>>> logger.debug('A debug message')
16:54:49 |                              hyperion | <module>()            |    INFO | An info message

so you only see the level INFO.










