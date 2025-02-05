import parse_slurm as ps
import glob

files = glob.glob('./data/data.*.txt')
data = ps.read_dataset(files)
