from typing import List, Tuple

import pandas as pd

from data_analysis.CLI.extractors.Parser import CombinedParser


class CPUAvgFrequencyParser(CombinedParser):
    """Extracts average CPU frequency from multiple files and stores it in a single file.
    !important: Make sure to run CPUFrequencyParser first"""

    @staticmethod
    def extract(file_path: str):
        data = pd.read_csv(file_path)
        data = data.groupby(['CPU']).mean('CPU MHz').mean()
        return float(data['CPU MHz'])

    # TODO: make dynamic by instantiating in constructor and making methods non-static
    DATA_PATH = 'cpu.csv'

    @classmethod
    def extract_into_file(cls, src: List[Tuple[str, str]], destination_path: str):
        avg_freq = []
        for job_name, file in src:
            try:
                avg_freq.append({"JobName": job_name, "AVG_CPU_freq_MHz": cls.extract(file)})
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"Failed to extract data from file {file}", e)

        pd.DataFrame(avg_freq).to_csv(destination_path, index=False)
