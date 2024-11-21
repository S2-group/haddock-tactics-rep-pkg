import re
from datetime import datetime

import pandas as pd

from data_analysis.CLI.extractors.Parser import IndividualParser


class CPUFrequencyParser(IndividualParser):
    timestamp_pattern = re.compile(r'^([^cpu]\S+\s.+)\s\w{3}(\s\d+)?$')

    @staticmethod
    def extract_timestamp(timestamp_match):
        """Handles multiple timestamp formats"""
        timestamp_str = timestamp_match.group(1)
        try:
            timestamp = datetime.strptime(timestamp_str, '%a %d %b %Y %I:%M:%S %p')
        except ValueError:
            timestamp = datetime.strptime(f"{timestamp_str} {timestamp_match.group(2)}",
                                          '%a %b %d %I:%M:%S %p %Y')
        return timestamp

    @staticmethod
    def extract(file_path: str):
        cpu_frequency_pattern = re.compile(r'^cpu MHz\s+:\s+(\d+\.\d+)')

        timestamp = None
        cpu_frequency_data = []
        cpu_idx = 0

        with open(file_path, 'r') as file:
            for line in file:
                timestamp_match = CPUFrequencyParser.timestamp_pattern.match(line)
                cpu_frequency_match = cpu_frequency_pattern.match(line)

                if timestamp_match:
                    timestamp = CPUFrequencyParser.extract_timestamp(timestamp_match)
                    cpu_idx = 0

                if cpu_frequency_match:
                    cpu_frequency_info = cpu_frequency_match.groups()
                    cpu_frequency_data.append(
                        {'Timestamp': timestamp.isoformat(), 'CPU': cpu_idx,
                         'CPU MHz': float(cpu_frequency_info[0])})
                    cpu_idx += 1

        df = pd.DataFrame(cpu_frequency_data)
        return df
