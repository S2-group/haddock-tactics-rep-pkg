import pandas as pd
import numpy as np
from scipy.stats import shapiro, kruskal
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from cliffs_delta import cliffs_delta

# ----- FUNCTIONS TO READ THE DATASET ----- # 
# Functions for parsing the files
def extract_workflow(df):
    # This function gets the entries referring to batches
    # and extracts the corresponding workflow from the job entry
    batches = df[df['JobID'].str.contains('batch', regex=True)]

    for i, row in batches.iterrows():
        jobid = row.JobID.split('.')[0] # extracts di ID
        # find the job entry in the dataframe including all the entries
        jobrow = df[df['JobID'] == jobid]
        # extract the workflow from job name
        workflow = jobrow['JobName'].item().split('-')[0]

        # substitute JobName with the workflow
        row['JobName'] = workflow
        row['JobID'] = jobid

    return batches.rename(columns={'JobName': 'Workflow'})

def parse(path):
    df = pd.read_csv(path, header=None, delimiter=r"\s+")
    df.columns =  list(df.loc[0]) # set headers
    ## gets completed entries
    df = df[(df['State'] == 'COMPLETED')]
    return extract_workflow(df)

def read_dataset(files):
    dfs = [parse(f) for f in files]
    return pd.concat(dfs, ignore_index=True)
# ----- FUNCTIONS TO FILTER THE DATASET ----- # 
def convert_to_hours(time_str):
    d = 0
    
    if '-' in time_str:
        d = time_str.split('-')
        time_str = d[1]
        d = int(d[0])
    
    time_str = time_str.replace('.', ':')
    time = time_str.split(':')

    if(len(time) == 4):
        h, m, s, ms = list(map(int, time_str.split(':')))
        total_hours = h + m / 60 + s / 3600 + ms / 360000
        return total_hours + (d * 24)

    h, m, s = list(map(int, time_str.split(':')))
    total_hours = h + m / 60 + s / 3600
    return total_hours + (d * 24)

def remove_unit(string):
    if 'M' in string:
        return string.replace('M', '')
    # elif 'K' in string:
    return string.replace('K', '')

def convert_to_gb(memory_str):
    return float(remove_unit(memory_str)) * (10**-6)

def convert_to_mega_joule(energy_str):
    return remove_unit(energy_str)

def get_data(data, workflow="daa"):
    output = data[data['Workflow'] == workflow][
        ['JobID', 'ConsumedEnergy', 'Elapsed', 'AveRSS', 'SystemCPU', 'UserCPU', 'NCPUS']
    ]

    output['ConsumedEnergy'] = output["ConsumedEnergy"].apply(convert_to_mega_joule)
    output['Elapsed'] = output["Elapsed"].apply(convert_to_hours)
    output['AveRSS'] = output["AveRSS"].apply(convert_to_gb)

    # calculate average CPU usage per JOB
    output["SystemCPU"] = output["SystemCPU"].apply(convert_to_hours)
    output["UserCPU"] = output["UserCPU"].apply(convert_to_hours)
    output['AveCPU'] = (output["UserCPU"] + output["SystemCPU"]) / output['Elapsed']

    # Convert Data
    return output.astype({
        'ConsumedEnergy': float, 'Elapsed': float, 'AveRSS': float, 'SystemCPU': float,
        'UserCPU': float, 'AveCPU':float, "NCPUS": int
    })

def get_group(data, workflow="daa", ncpus=4):
    return data[data["NCPUS"] == ncpus]

# remove outliers for each number of vCPUS
def remove_outliers_cpus(data, threshold=1, column='Elapsed'):
    # check if data contains 'NCPUS'
    if 'NCPUS' not in data.columns:
        return 'NCPUS not found'

    result = []
    for cpus in [4, 8, 16, 32]:
        # retreve the data chunk corresponding to cpus
        chunk = data[data['NCPUS'] == cpus]

        # remove outliers for the column related to ConsumedEnergy 
        filtered_chunk = remove_outliers(
            chunk,
            column,
            threshold=threshold
        ).reset_index(drop=True)

        # appends the filtered chunk to the dataframe
        # containing all the data
        result.append(filtered_chunk)

    return pd.concat(result, axis=0, ignore_index=True)

# remove outliers using the interquartile (IQR) method
def remove_outliers(data, column, threshold=1):
    threshold = threshold 
    z_scores = np.abs(
        (data[column] - data[column].mean()) / data[column].std()
    )
    # dataframe with data and the zscores
    data_with_zscores = pd.concat(
        [data, z_scores], axis=1, #keys=[data.name, 'zscores']
    )
    # filters the rows having z scores greater than the threshold 
    # returns a pd.Series with data filtered according to the z_scores
    return data[z_scores < threshold]


# ----- DATA ANALYSIS ----- # 

# test normality using the Shapiro-Wilk test
# requires a DataFrame having 2 columns: the dependent variable to test
# and NCPUS
def test_normality(data: pd.DataFrame, column="ConsumedEnergy"):
    result = [] 
    for cpus in [4, 8, 16, 32]:
        values = data[data['NCPUS'] == cpus][column].to_list()
        stat, p_value = shapiro(values)
        result.append({'NCPUS': cpus, 'STAT': stat, 'PVALUE': p_value})
    return pd.DataFrame(result) 

def generate_qq(data: pd.DataFrame, column="ConsumedEnergy"):
    for cpus in [4, 8, 16, 32]:
        values = data[data['NCPUS'] == cpus][column]
        sm.qqplot(values, line='45')
        plt.title('Q-Q Plot')
        plt.show()

# test hypothesis on non_normal using Kruskal-Wallis (KW) tests 
# requires a DataFrame having 2 columns: the dependent variable to test
# and NCPUS
def test_hypothesis_kruskal(data: pd.DataFrame, column="ConsumedEnergy"):
    result = []
    for cpus in [4, 8, 16, 32]:
        values = data[data['NCPUS'] == cpus][column]
        result.append(values)
    # apply the KW test on 4 independent groups 
    stat, p_value = kruskal(*result)
    return stat, p_value

def calc_cliffs_delta(data: pd.DataFrame, column="ConsumedEnergy"):
    result = []
    cpus = [4, 8, 16, 32]
    groups = [(cpus[i], cpus[i+1]) for i in range(len(cpus)-1)]

    for group in groups:
        chunk0 = data[data['NCPUS'] == group[0]][column]
        chunk1 = data[data['NCPUS'] == group[1]][column]

        d, res = cliffs_delta(chunk0, chunk1)

        result.append({'CPUS-GROUPS': group, 'Value': d, 'Result': res})
    
    return pd.DataFrame(result)

def calc_groups_improvement(data: pd.DataFrame, column="ConsumedEnergy"):
    result = []
    improv = lambda x,y: ((y - x) / x) * 100 
    delta = lambda x,y: (y - x)

    cpus = [4, 8, 16, 32]
    groups = [(cpus[i], cpus[i+1]) for i in range(len(cpus)-1)]
    groups.append((4, 32))

    for group in groups:
        chunk0 = data[data['NCPUS'] == group[0]][column]
        chunk1 = data[data['NCPUS'] == group[1]][column]

        mean_improv = improv(
            chunk1.mean(), chunk0.mean()
        )

        median_improv = improv(
            chunk1.median(), chunk0.median()
        )

        mean_delta = delta(
            chunk1.mean(), chunk0.mean()
        )

        median_delta = delta(
            chunk1.median(), chunk0.median()
        )

        result.append({
            'CPU-GROUPS' : group, 
            'Mean Improvement': mean_improv,
            'Median Improvement': median_improv,
            'Mean Delta': mean_delta,
            'Median Delta': median_delta
        })

    return pd.DataFrame(result)
