from enum import Enum
from typing import Dict

from examples import PathRegistry

class Mode(Enum):
    LOCAL = "local"
    HPC = "hpc"
    MPI = "mpi"


class Workflow(Enum):
    DAA = "daa"
    DPP = "dpp"


class Node(Enum):
    gl2 = "gl2"
    gl4 = "gl4"
    gl5 = "gl5"
    gl6 = "gl6"


SHARED_DIR = PathRegistry.SHARED_DIR
HOST_EXPERIMENT_FOLDER = PathRegistry.HOST_EXPERIMENT_FOLDER


class ExperimentDir(Enum):
    LOCAL = "exp-local"
    HPC = "exp-hpc"
    MPI = "exp-mpi"

    @staticmethod
    def value_to_enum(value):
        try:
            return next(member for member in ExperimentDir if member.value == value)
        except StopIteration:
            all_values = [member.value for member in ExperimentDir]
            raise ValueError(
                f"{value} is not a valid value in ExperimentType, should be one of {all_values}")

    @staticmethod
    def dir(exp: 'ExperimentDir', *path: str):
        return ExperimentDir.__get_dir(exp, SHARED_DIR, *path)

    @staticmethod
    def host_dir(exp: 'ExperimentDir', *path: str):
        return ExperimentDir.__get_dir(exp, HOST_EXPERIMENT_FOLDER, *path)

    @staticmethod
    def analysis_dir(exp: 'ExperimentDir', *path: str):
        return ExperimentDir.__get_dir(exp, ".", *path)

    @staticmethod
    def __get_dir(exp: 'ExperimentDir', base_dir_path=SHARED_DIR, *path: str):
        if path is None:
            path = []
        return f"{base_dir_path}/{exp.value}/{'/'.join(path)}"


EXPERIMENT_DIR_TO_MODE_MAP: Dict[ExperimentDir, Mode] = {
    ExperimentDir.LOCAL: Mode.LOCAL,
    ExperimentDir.HPC: Mode.HPC,
    ExperimentDir.MPI: Mode.MPI,
}
