### How does Parallelism impact the Energy Efficiency and Performance of High-Performance Scientific Software? The Case of Haddock
Replication Package of the study:

**Title**: *"How does Parallelism impact the Energy Efficiency and Performance of High-Performance Scientific Software? The Case of Haddock"* \
**Authors**: Vincenzo Stoico • Dmitrijs Voronovs • Ivano Malavolta • Patricia Lago \
**Paper**: preprint_to_publish

### Structure of the Repository
- `cli`: Folder containing the command-line tool. The tool can orchestrate the experiment and query SLURM to retrieve job measurements and data.
- `data`: Folder including the measurements of our experiment. The files follow different naming conventions. The files called `[machine_names]_[file.id].txt` contain the measurements sorted per machine, while those named `data_[daa|dpp].csv` include data per workflow. The `Focus Group - HADDOCK.csv` file contain the results of the focus group.
- `notebooks`: Folder containing the Jupyter notebooks to replicate the data analysis. 
- `runs`: Folder including the logs of each run of our experiment.
- `requirements.txt`: File including the list of packages required for data analysis.  


#### Install Data Analysis packages

##### Install Jupyter Notebook and required libraries
`pip install jupyter`\
`pip install -r requirements.txt`

##### Launch Jupyter Notebook from the upmost folder of this repository (./haddock-tactics-rep-pkg)
`jupyter notebook`
