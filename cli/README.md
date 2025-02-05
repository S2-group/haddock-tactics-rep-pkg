# CLI tool guide

## Description

The developed CLI tool provides a comprehensive set of commands for managing and monitoring experiments
efficiently.Users can check directory space availability, create new experiments, retrieve experiment information data
such asconsumed energy, and generate detailed diagrams depicting individual run metrics like memory and CPU
utilization.Additionally, the tool offers functionality for generating overview diagrams summarizing experiment data.
With commandsfor accessing Slurm cluster information, checking queue status, querying the Slurm accountant for
experiment data, andcancelling running or pending jobs, this tool streamlines experiment management tasks, making it a
valuable asset forresearchers and practitioners in need of a robust experiment management solution.

## Commands

```
commands:
    get_exp_data (get-data)
                        Get experiment data
    get_log_files (get-logs)
                        Get log files
    clean_experiment_dir (clean)
                        Clean experiment directory
    run_experiment (run-exp)
                        Run experiment
    execute (exec)      Execute a custom command
    check_space (space)
                        Check space of the cluster
    check_dir_space (dir-space)
                        Check experiment directory space
    create_experiment (create-exp)
                        Create experiment
    start_gl3_logger (start-gl3-logger)
                        Start additional gl3 logger for cpu data
    stop_gl3_logger (stop-gl3-logger)
                        Stop additional gl3 logger for cpu data
    get_info_data (get-info)
                        Get experiment info data (consumed energy from perf module)
    generate_run_diagrams (gen-run-diagrams)
                        Generate individual run diagrams (mem and cpu utilization, cpu frequency)
    generate_diagrams (gen-diagrams)
                        Generate overview diagrams
    sinfo               Slurm node information
    squeue              Check slurm queue
    sacct               Query slurm accountant to get experiment data
    scancel             Cancel all running and pending jobs

options:
  -h, --help            show this help message and exit

```

## Workflow

The provided Python code snippet outlines the definition of a class within thecontext
of a Command Line Interface (CLI) tool designed for managing experiments. The class, named _GL6_4_ (_GL6_
corresponding to a server node name and _4_ to the generation, i.e. generation 4 produces trialsranging from 41
to 50 inclusive), inherits from a base class _LocalExperiment_, suggesting specialization withinthe experiment
management framework - in this case, indicating local mode execution. Within this class, two methods aredefined:
_create_configs_ and _create_warmup_config_. The _create_configs_ method generates alist of
experiment configurations based on various parameters such as workflow types, trial numbers, and core counts,while the
_create_warmup_config_ method produces a single configuration designated for warm-up purposes. Thecode employs
type annotations for enhancing code clarity and readability, specifying expected types for variables andreturn values.
This snippet illustrates a foundational component of the CLI tool, demonstrating its ability todynamically generate and
manage experiment configurations, crucial for efficient and flexible experimentation workflows.

```python
class GL6_4(LocalExperiment):

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "gl6", trial, ncores)
            for workflow in ["dpp", "daa"]
            for ncores in [2, 4, 8, 16, 32]
            for trial in range(31, 41)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl6", 31, 32, True)
```

In the typical sequence of steps for an experiment, the process begins with the creation of the experiment directory and
configuration, followed by the execution of the experiment itself.

```bash
python experiment.py create-exp -d exp-local -c GL6_4
python experiment.py run-exp -d exp-local -c GL6_4 -n GL6
```

Subsequently, the progress of the experiment and its associated data are tracked and updated. Various commands are used
to perform these tasks, including retrieving data and logs, cleaning up the
experiment directory, obtaining information about the experiment, and generating diagrams for visualization. These
commands are executed sequentially to ensure the systematic execution and analysis of the experiment within the
experimentation framework.

```bash
python experiment.py get-data -d exp-local -c GL6_4
python experiment.py get-logs -d exp-local
python experiment.py clean -d exp-local
python experiment.py get-info -d exp-local -c GL6_4
python experiment.py gen-diagrams
python experiment.py gen-run-diagrams -d exp-local
```