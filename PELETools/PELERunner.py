# -*- coding: utf-8 -*-


# Python imports
import sys
from subprocess import check_output, CalledProcessError, STDOUT


# FEP_PELE imports
from . import PELEConstants as pele_co
from FEP_PELE.Utils.InOut import checkFile


# Script information
__author__ = "Marti Municoy"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marti Municoy"
__email__ = "marti.municoy@bsc.es"


class PELERunner(object):
    def __init__(self, executable_path, number_of_processors=1,
                 executable_type=pele_co.PELE_SERIAL_EXEC_TYPE):
        try:
            checkFile(executable_path)
        except NameError as exception:
            print("PELERunner error: " + str(exception))
            sys.exit(1)

        if (executable_type not in pele_co.PELE_EXECUTABLE_TYPES):
            print("PELERunner error: invalid executable type " +
                  "\'{}\'".format(executable_type) +
                  ". Valid types are " + str(pele_co.PELE_EXECUTABLE_TYPES))
            sys.exit(1)

        self.__srun = self.checkSRun()

        self.__executable_path = executable_path
        self.__number_of_processors = number_of_processors
        self.__executable_type = executable_type

        if (number_of_processors > 1):
            self.__executable_type = pele_co.PELE_MPI_EXEC_TYPE

    @property
    def srun(self):
        return self.__srun

    def checkSRun(self):
        try:
            output = check_output(["which", "srun"],
                                  stderr=STDOUT).decode('utf-8')
        except Exception as e:
            output = str(e.output)

        if ('which: no srun in' in output):
            return False
        else:
            return True

    def run(self, control_file_path):
        if (self.__executable_type == pele_co.PELE_SERIAL_EXEC_TYPE):
            return self._serial_run(control_file_path)
        if (self.__executable_type == pele_co.PELE_MPI_EXEC_TYPE):
            return self._mpi_run(control_file_path)

    def _serial_run(self, control_file_path):
        try:
            output = check_output([self.__executable_path,
                                   control_file_path])

        except CalledProcessError as exception:
            print(exception.output.decode('utf-8').strip())
            raise SystemExit(
                "Error while running PELE: \'" + self.__executable_path + ' ' +
                control_file_path + '\'')

        return output.decode('utf-8').strip()

    def _mpi_run(self, control_file_path):
        if (self.srun):
            args = ["srun", "-n", str(self.__number_of_processors),
                    self.__executable_path, control_file_path]
        else:
            args = ["mpirun", "-n", str(self.__number_of_processors),
                    self.__executable_path, control_file_path]

        try:
            output = check_output(args, stderr=STDOUT)

        except CalledProcessError as exception:
            print(exception.output.decode('utf-8').strip())
            raise SystemExit(
                "Error while running PELE: \'" + "mpirun -n " +
                str(self.__number_of_processors) + " " +
                self.__executable_path + control_file_path + '\'')

        return output.decode('utf-8').strip()
