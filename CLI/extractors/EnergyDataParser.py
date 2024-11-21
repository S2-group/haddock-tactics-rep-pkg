from typing import List, Tuple

import pandas as pd
import regex as re

from data_analysis.CLI.extractors.Parser import CombinedParser


class EnergyDataParser(CombinedParser):
    @staticmethod
    def extract(file_path: str):
        """Extracts power_energy_pkg, power_energy_ram, perf_elapsed from a file"""
        with open(file_path, 'r') as file:
            content = file.read()
            numbers = re.findall(r"(?:\d+,?)+\.\d+", content)
            return [float(num.replace(',', '')) for num in numbers]

    @classmethod
    def extract_into_file(cls, src: List[Tuple[str, str]], destination_path):
        job_data = []
        for job_name, file in src:
            try:
                power_energy_pkg, power_energy_ram, perf_elapsed = cls.extract(file)
                job_data.append(
                    {"JobName": job_name, "power_energy_pkg": power_energy_pkg, "power_energy_ram": power_energy_ram,
                     "perf_elapsed": perf_elapsed})
            except FileNotFoundError as e:
                pass
            except Exception as e:
                print(f"Failed to extract data from file {file}", e)
        df = pd.DataFrame(job_data)
        df.to_csv(destination_path, index=False)
