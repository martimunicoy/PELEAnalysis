# -*- coding: utf-8 -*-


# Imports
import os
import pickle
import numpy as np


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


# Functions
def isThereAFile(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False


def fromDictValuesToList(input_dict):
    output_list = []
    for key, value in input_dict.items():
        if type(value) is dict:
            value = fromDictValuesToList(value)
        for element in value:
            output_list.append(element)
    return output_list


class Logger(object):
    """
    It contains all the required methods to handle logging messages.
    """
    import logging
    DEFAULT_LEVEL = logging.INFO

    def __init__(self):
        """It initializes a Logger object"""
        import logging

        # Get peleffy logger and set level only the first time
        if 'peleanalysis_log' not in logging.root.manager.loggerDict:
            self._logger = logging.getLogger('peleanalysis_log')
            self._logger.setLevel(self.DEFAULT_LEVEL)
        else:
            self._logger = logging.getLogger('peleanalysis_log')

        # If no handler is found add stream handler
        if not len(self._logger.handlers):
            ch = logging.StreamHandler()
            ch.setLevel(self.DEFAULT_LEVEL)
            formatter = logging.Formatter('%(message)s')
            ch.setFormatter(formatter)
            self._logger.addHandler(ch)

    def set_level(self, level):
        """
        It sets the logging level.

        Parameters
        ----------
        level : str
            The logging level to set. One of [DEBUG, INFO, WARNING, ERROR,
            CRITICAL]
        """
        import logging

        if level.upper() == 'DEBUG':
            logging_level = logging.DEBUG
        elif level.upper() == 'INFO':
            logging_level = logging.INFO
        elif level.upper() == 'WARNING':
            logging_level = logging.WARNING
        elif level.upper() == 'ERROR':
            logging_level = logging.ERROR
        elif level.upper() == 'CRITICAL':
            logging_level = logging.CRITICAL
        else:
            raise ValueError('Invalid level type')

        self._logger.setLevel(logging_level)
        for handler in self._logger.handlers:
            handler.setLevel(logging_level)

    def debug(self, *messages):
        """
        It pulls a debug message.

        Parameters
        ----------
        messages : list[str]
            The list of messages to print
        """
        if len(messages) > 1:
            self._logger.debug(' '.join(map(str, messages)))
        else:
            self._logger.debug(messages[0])

    def info(self, *messages):
        """
        It pulls an info message.

        Parameters
        ----------
        messages : list[str]
            The list of messages to print
        """
        if len(messages) > 1:
            self._logger.info(' '.join(map(str, messages)))
        else:
            self._logger.info(messages[0])

    def warning(self, *messages):
        """
        It pulls a warning message.

        Parameters
        ----------
        messages : list[str]
            The list of messages to print
        """
        if len(messages) > 1:
            self._logger.warning(' '.join(map(str, messages)))
        else:
            self._logger.warning(messages[0])

    def error(self, *messages):
        """
        It pulls a error message.

        Parameters
        ----------
        messages : list[str]
            The list of messages to print
        """
        if len(messages) > 1:
            self._logger.error(' '.join(map(str, messages)))
        else:
            self._logger.error(messages[0])

    def critical(self, *messages):
        """
        It pulls a critical message.

        Parameters
        ----------
        messages : list[str]
            The list of messages to print
        """
        if len(messages) > 1:
            self._logger.critical(' '.join(map(str, messages)))
        else:
            self._logger.critical(messages[0])


def unpickle(binary_file):
    with open(binary_file, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def checkFile(file_path):
    file_path = str(file_path)
    if (not os.path.exists(file_path)):
        raise NameError("Invalid path to file: " + file_path)


def normalize(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2 == 0] = 1
    return a / np.expand_dims(l2, axis)


def norm(a, axis=-1, order=2):
    return np.atleast_1d(np.linalg.norm(a, order, axis))


def calculate_Boltzmann_probability(energy, temperature=300):
    return np.exp(-energy / 0.0019872041 / temperature)

