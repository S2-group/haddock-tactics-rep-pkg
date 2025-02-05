import argparse
import os
import shutil
import subprocess
import sys
from importlib import import_module
from multiprocessing import Pool
from pathlib import Path

sys.path.append(os.path.pardir)

from .extractors.CPUAvgFrequencyParser import CPUAvgFrequencyParser
from .extractors.CPUUtilizationParser import CPUUtilizationParser
from .extractors.EnergyDataParser import EnergyDataParser
from .extractors.LogFileParser import LogFileParser
from .extractors.MemoryUtilizationParser import MemoryUtilizationParser
from .extractors.CPUFrequencyParser import CPUFrequencyParser

from examples.domain.experiment.Experiment import Experiment
from examples import PathRegistry
from .Constants import ExperimentDir, EXPERIMENT_DIR_TO_MODE_MAP
from .CredentialManager import CredentialManager, DEFAULT_NODE
from .RemoteSSHClient import RemoteSSHClient


class CLICommandHandler:
    def __init__(self, client):
        self.client: 'RemoteSSHClient' = client

    def execute_cli_command(self):
        parser = argparse.ArgumentParser(description='Remote SSH Client')
        subparsers = parser.add_subparsers(dest='command')
        get_data_parser = subparsers.add_parser('get_exp_data', aliases=["get-data"], help='Get experiment data')
        self.add_dir_arg(get_data_parser)
        self.add_cls_arg(get_data_parser, multiple=True)
        get_log_files_parser = subparsers.add_parser('get_log_files', aliases=["get-logs"], help='Get log files')
        self.add_dir_arg(get_log_files_parser)
        clean_experiment_dir_parser = subparsers.add_parser('clean_experiment_dir', aliases=["clean"],
                                                            help='Clean experiment directory')
        self.add_dir_arg(clean_experiment_dir_parser)
        clean_experiment_dir_parser.add_argument('--full', action='store_true', default=False,
                                                 help='Clean the entire directory')
        run_experiment_parser = subparsers.add_parser('run_experiment', aliases=["run-exp"], help='Run experiment')
        self.add_node_arg(run_experiment_parser)
        self.add_dir_arg(run_experiment_parser)
        self.add_cls_arg(run_experiment_parser)

        execute_parser = subparsers.add_parser('execute', aliases=['exec'], help='Execute a custom command')
        execute_parser.add_argument('cmd', nargs=argparse.REMAINDER, help='The command to execute')

        subparsers.add_parser('check_space', aliases=["space"], help='Check space of the cluster')
        check_dir_space = subparsers.add_parser('check_dir_space', aliases=["dir-space"],
                                                help='Check experiment directory space')
        self.add_dir_arg(check_dir_space)

        create_experiment_parser = subparsers.add_parser('create_experiment', aliases=["create-exp"],
                                                         help='Create experiment')
        self.add_dir_arg(create_experiment_parser)
        self.add_cls_arg(create_experiment_parser)

        start_gl3_logger_parser = subparsers.add_parser('start_gl3_logger', aliases=["start-gl3-logger"],
                                                        help='Start additional gl3 logger for cpu data')
        self.add_cls_arg(start_gl3_logger_parser)

        stop_gl3_logger_parser = subparsers.add_parser('stop_gl3_logger', aliases=["stop-gl3-logger"],
                                                       help='Stop additional gl3 logger for cpu data')
        self.add_cls_arg(stop_gl3_logger_parser)

        get_info_data_parser = subparsers.add_parser('get_info_data', aliases=["get-info"],
                                                     help='Get experiment info data (consumed energy from perf module)')
        self.add_dir_arg(get_info_data_parser)
        self.add_cls_arg(get_info_data_parser)

        generate_run_diagrams_parser = subparsers.add_parser('generate_run_diagrams', aliases=["gen-run-diagrams"],
                                                             help='Generate individual run diagrams (mem and cpu utilization, cpu frequency)')
        self.add_dir_arg(generate_run_diagrams_parser)

        subparsers.add_parser('generate_diagrams', aliases=['gen-diagrams'], help='Generate overview diagrams')

        subparsers.add_parser('sinfo', help='Slurm node information')
        subparsers.add_parser('squeue', help='Check slurm queue')
        subparsers.add_parser('sacct', help='Query slurm accountant to get experiment data')
        subparsers.add_parser('scancel', help='Cancel all running and pending jobs')

        args = parser.parse_args()
        if args.command in ['get_exp_data', "get-data"]:
            self.get_exp_data(ExperimentDir.value_to_enum(args.dir), args.cls)
        elif args.command in ['check_space', "space"]:
            self.check_space()
        elif args.command in ['check_dir_space', "dir-space"]:
            self.check_dir_space(ExperimentDir.value_to_enum(args.dir))
        elif args.command == 'sinfo':
            self.client.execute_commands(["sinfo"])
        elif args.command == 'squeue':
            self.client.execute_commands(['squeue -o "%7A %50j %3t %N"'])
        elif args.command == 'sacct':
            self.client.execute_commands([f"sacct -o {Experiment.get_sacct_output_format(main_fields_only=True)}"])
        elif args.command == 'scancel':
            self.client.execute_commands(["scancel -t R", "scancel -t PD", "squeue"])
        elif args.command in ['get_log_files', "get-logs"]:
            self.get_log_files(ExperimentDir.value_to_enum(args.dir))
        elif args.command in ['execute', 'exec']:
            self.client.execute_commands([' '.join(args.cmd)])
        elif args.command in ['clean_experiment_dir', "clean"]:
            self.clean_experiment_dir(ExperimentDir.value_to_enum(args.dir), args.full)
        elif args.command in ['create_experiment', "create-exp"]:
            self.create_experiment(ExperimentDir.value_to_enum(args.dir), args.cls)
        elif args.command in ['get_info_data', "get-info"]:
            self.get_info_data(ExperimentDir.value_to_enum(args.dir), args.cls)
        elif args.command in ['generate_run_diagrams', "gen-run-diagrams"]:
            self.generate_run_diagrams(ExperimentDir.value_to_enum(args.dir))
        elif args.command in ['generate_diagrams', "gen-diagrams"]:
            self.generate_diagrams()
        elif args.command in ['run_experiment', "run-exp"]:
            exp_dir = ExperimentDir.value_to_enum(args.dir)
            if args.node == DEFAULT_NODE:
                CLICommandHandler(self.client).run_experiment(exp_dir, args.cls)
            else:
                node_client = RemoteSSHClient(*CredentialManager.get_credentials_for_node(args.node))
                CLICommandHandler(node_client).run_experiment(exp_dir, args.cls)
        elif args.command in ['start_gl3_logger', "start-gl3-logger"]:
            node_client = RemoteSSHClient(*CredentialManager.get_credentials_for_node("gl3"))
            CLICommandHandler(node_client).start_gl3_logger(args.cls)
        elif args.command in ['stop_gl3_logger', "stop-gl3-logger"]:
            node_client = RemoteSSHClient(*CredentialManager.get_credentials_for_node("gl3"))
            CLICommandHandler(node_client).stop_gl3_logger(args.cls)

    def add_node_arg(self, run_experiment_parser):
        run_experiment_parser.add_argument('-n', '--node', type=str, required=True, help='Node [example: "gl2", "gl5"]')

    def add_dir_arg(self, parser):
        parser.add_argument('-d', '--dir', type=str, required=True, help='Experiment directory')

    def add_cls_arg(self, parser, multiple=False):
        if multiple:
            parser.add_argument('-c', '--cls', nargs='*', required=True,
                                help='Experiment classnames [example: "Test GL2_3"]')
        else:
            parser.add_argument('-c', '--cls', type=str, required=True,
                                help='Experiment classname [example: "Test", "GL2_3"]')

    def get_exp_data(self, exp: 'ExperimentDir', experiment_ids):
        exp_dir = ExperimentDir.dir(exp)
        self.client.execute_commands(
            [f'cd {exp_dir}'] + [f'sh {PathRegistry.check_job_script(eid)}' for eid in experiment_ids] + [
                f'sh {PathRegistry.check_job_script(eid, full=True)}' for eid in experiment_ids])
        self.client.get_files(
            [ExperimentDir.dir(exp, PathRegistry.experiment_data_filename(eid)) for eid in experiment_ids],
            ExperimentDir.analysis_dir(exp, 'data'))
        self.client.get_files(
            [ExperimentDir.dir(exp, PathRegistry.experiment_data_filename(eid, full=True)) for eid in experiment_ids],
            ExperimentDir.analysis_dir(exp, 'full', 'data'))

    def clean_experiment_dir(self, exp: 'ExperimentDir', full: bool):
        exp_dir = ExperimentDir.dir(exp)
        self.client.put_files([PathRegistry.clean_script()], exp_dir)
        if full:
            print("Full directory cleanup")
            self.client.execute_commands(
                [f'cd {exp_dir}', 'rm -rf run.*', 'rm -rf *.info', 'rm -rf *.cfg', 'rm -rf slurm-*'])
        else:
            self.client.execute_commands([f'cd {exp_dir}', 'sh clean.sh'])

    def get_haddock_log_files(self, exp: 'ExperimentDir', subdir='runs'):
        all_directories = self.client.execute_commands([f'cd {ExperimentDir.dir(exp)}', 'ls -d run.*/', ]).splitlines()

        for directory in all_directories:
            directory = directory.strip("/")
            destination_dir = ExperimentDir.host_dir(exp, subdir, directory)
            remote_dir = ExperimentDir.dir(exp, directory)

            if Path(destination_dir).exists():
                print(f"\n{destination_dir=} exists. Calculating size...")
                if self.equal_dir_sizes(destination_dir, remote_dir):
                    continue

            print(f"\nDownloading...{destination_dir=}")

            files = self.client.execute_commands([f'cd {remote_dir}', 'ls -p | grep -v /', ]).splitlines()
            files_abs_path = [f"{remote_dir}/{file}" for file in files]

            if Path(destination_dir).exists():
                for file in Path(destination_dir).glob("**/*"):
                    if file.is_file():
                        file.unlink()
                Path(destination_dir).rmdir()

            Path(destination_dir).mkdir(exist_ok=True)
            self.client.get_files(files_abs_path, destination_dir)

    def equal_dir_sizes(self, local_dir, remote_dir):
        local_dir_size = sum(
            f.stat().st_size for f in Path(local_dir).glob("**/*") if f.is_file() and not f.name.startswith('pid.'))
        try:
            if '.info' in remote_dir:
                remote_dir_size = int(self.client.execute_commands([f"du -sb {remote_dir}"]).split()[0])
            else:
                remote_dir_size = int(self.client.execute_commands([f"du -sb {remote_dir}/log"]).split()[0])
        except:
            remote_dir_size = -1
        same_size = remote_dir_size == local_dir_size
        print(f"same size: {same_size}, {remote_dir_size=}, {local_dir_size=}")
        return same_size

    def get_slurm_files(self, exp: 'ExperimentDir', subdir='slurm'):
        exp_dir = ExperimentDir.dir(exp)
        slurm_files = self.client.execute_commands([f'cd {exp_dir}', 'ls -p slurm-* | grep -v /', ]).splitlines()

        destination_dir = ExperimentDir.host_dir(exp, subdir)
        new_slurm_files = [f"{exp_dir}/{file}" for file in slurm_files if
                           not Path(f"{destination_dir}/{file}").exists()]

        self.client.get_files(new_slurm_files, destination_dir)

    def get_log_files(self, exp: 'ExperimentDir'):
        self.get_haddock_log_files(exp)
        self.get_slurm_files(exp)

    def check_space(self):
        self.client.execute_commands(["df -h"])

    def check_dir_space(self, exp: 'ExperimentDir'):
        exp_dir = ExperimentDir.dir(exp)
        self.client.execute_commands([f"cd {exp_dir}", "pwd", "du -h --max-depth=1 | sort -h"])

    # TODO: adjust later
    def prepare_experiment_dir(self, exp: 'ExperimentDir'):
        self.client.put_directory(ExperimentDir.host_dir(exp, 'data'), ExperimentDir.dir(exp, 'data'))
        self.client.put_directory(ExperimentDir.host_dir(exp, 'template'), ExperimentDir.dir(exp, 'template'))
        self.client.put_files(
            [ExperimentDir.host_dir(exp, PathRegistry.create_job_script())] + PathRegistry.info_scripts(),
            ExperimentDir.dir(exp))

    def run_experiment(self, exp: 'ExperimentDir', exp_id: str):
        self.prepare_experiment_dir(exp)

        exp_dir = ExperimentDir.dir(exp)

        create_jobs_script = PathRegistry.create_jobs_script(exp_id)
        run_experiment_script = PathRegistry.run_experiment_script(exp_id)
        scripts_for_transfer = [create_jobs_script, run_experiment_script]
        self.client.put_files([ExperimentDir.host_dir(exp, file) for file in scripts_for_transfer], exp_dir)

        self.client.execute_commands(
            [f"echo running experiment '{exp_id}' on $(hostname)", f"cd {exp_dir}", "pwd", f"sh {create_jobs_script}",
             "echo activate conda", "source $HOME/anaconda3/bin/activate", "conda activate haddock3",
             "echo run experiment", f"sh {run_experiment_script}", "sinfo"])

    def start_gl3_logger(self, exp_id: str):
        self.client.put_files([PathRegistry.gl3_collect_info_before()], '.')
        self.client.execute_commands_with_sudo([f"sh {PathRegistry.GL3_COLLECT_INFO_BEFORE_SH} {exp_id}"])

    def stop_gl3_logger(self, exp_id: str):
        self.client.put_files([PathRegistry.gl3_collect_info_after()], '.')
        self.client.execute_commands_with_sudo([f"sh {PathRegistry.GL3_COLLECT_INFO_AFTER_SH} {exp_id}"])

    def create_experiment_class(self, cls: str, exp: 'ExperimentDir'):
        mode = EXPERIMENT_DIR_TO_MODE_MAP[exp]
        module_name = f"examples.domain.experiment.{mode.value.lower()}.{cls}"
        return getattr(import_module(module_name), cls)

    def create_experiment(self, exp: 'ExperimentDir', cls: str):
        Experiment_Class: 'Experiment' = self.create_experiment_class(cls, exp)(ExperimentDir.host_dir(exp))
        Experiment_Class.generate_create_job_script().generate_runner()

    def get_info_data(self, exp: 'ExperimentDir', cls: str):
        ExperimentClass: 'Experiment' = self.create_experiment_class(cls, exp)()

        def source_files_config(name, suffix="info"):
            return [(cfg.name, ExperimentDir.host_dir(exp, 'runs', f"{cfg.run_dir}.{suffix}", name)) for cfg in
                    ExperimentClass.configs]

        os.makedirs(ExperimentDir.analysis_dir(exp, 'data', 'info'), exist_ok=True)
        destination_filename_perf = ExperimentDir.analysis_dir(exp, 'data', 'info', f'perf.{cls}.csv')
        destination_filename_avg_cpu_freq = ExperimentDir.analysis_dir(exp, 'data', 'info', f'cpu_freq_avg.{cls}.csv')
        get_destination_path = lambda file_name: lambda cfg: ExperimentDir.host_dir(exp, 'runs', f"run.{cfg[0]}.parsed",
                                                                                    file_name)

        CPUUtilizationParser.extract_into_file(source_files_config("proc_utilization.log"),
                                               get_destination_path('cpu_utilization.csv'))
        EnergyDataParser.extract_into_file(source_files_config("perf_stat.txt"), destination_filename_perf)
        LogFileParser.extract_into_file(source_files_config("haddock.output.log"), get_destination_path('steps.csv'))
        MemoryUtilizationParser.extract_into_file(source_files_config("mem_utilization.log"),
                                                  get_destination_path('memory.csv'))
        CPUFrequencyParser.extract_into_file(source_files_config("cpu_frequency.log"), get_destination_path('cpu.csv'))
        CPUAvgFrequencyParser.extract_into_file(source_files_config("cpu.csv", "parsed"),
                                                destination_filename_avg_cpu_freq)

    @staticmethod
    def generate_run_diagram(parsed_data_dir):
        print(f"Generating run diagrams for: {parsed_data_dir}")
        script_file = PathRegistry.execution_analysis_script()
        script_destination = Path(parsed_data_dir) / PathRegistry.EXECUTION_ANALYSIS_SCRIPT_FILENAME
        shutil.copy(script_file, script_destination)
        try:
            subprocess.run(['python', PathRegistry.EXECUTION_ANALYSIS_SCRIPT_FILENAME], cwd=parsed_data_dir)
        except Exception as e:
            print(f"Error while generating run diagrams for: {parsed_data_dir} \n {e}")
        finally:
            os.remove(script_destination)

    @staticmethod
    def generate_run_diagrams(exp: 'ExperimentDir'):
        exp_dir = Path(ExperimentDir.host_dir(exp)) / 'runs'
        parsed_data_dirs = list(exp_dir.glob('run.*.parsed'))
        # Create a multiprocessing Pool
        try:
            with Pool() as p:
                p.map(CLICommandHandler.generate_run_diagram, parsed_data_dirs)
        except KeyboardInterrupt:
            print("KeyboardInterrupt, terminating...")
            p.terminate()
            p.join()

        subprocess.call(["jupyter", "nbconvert", "--to", "python", "RunComparisonAnalysis.ipynb"])
        subprocess.call(["python", "RunComparisonAnalysis.py", exp.value])

    @classmethod
    def generate_diagrams(cls):
        subprocess.call(["jupyter", "nbconvert", "--to", "python", "OverallAnalysis.ipynb"])
        subprocess.call(["python", "OverallAnalysis.py"])
        subprocess.call(["jupyter", "nbconvert", "--to", "python", "EnergyAnalysis.ipynb"])
        subprocess.call(["python", "EnergyAnalysis.py"])
