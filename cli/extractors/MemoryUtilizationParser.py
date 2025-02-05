import re

import pandas as pd

from data_analysis.CLI.extractors.Helper import Helper
from data_analysis.CLI.extractors.Parser import IndividualParser


class MemoryUtilizationParser(IndividualParser):
    @classmethod
    def extract(cls, file_path: str):
        timestamp_pattern = re.compile(r'^(\d{2}:\d{2}:\d{2} [APMapm]+)')
        param_pattern = re.compile(
            r'\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)$')

        date = Helper.get_start_date(file_path)
        memory_data = []

        with open(file_path, 'r') as file:
            for line in file:
                timestamp_match = timestamp_pattern.match(line)
                header_match = param_pattern.search(line)

                if timestamp_match:
                    timestamp_str = timestamp_match.group(1)
                    prev_date = memory_data[-1]['Timestamp'] if memory_data else None
                    timestamp, date = cls.get_next_timestamp(prev_date, date, timestamp_str)

                if header_match:
                    memory_info = header_match.groups()
                    memory_data.append(
                        {'Timestamp': timestamp.isoformat(), 'kbmemfree': int(memory_info[0]),
                         'kbavail': int(memory_info[1]),
                         'kbmemused': int(memory_info[2]), '%memused': float(memory_info[3]),
                         'kbbuffers': int(memory_info[4]), 'kbcached': int(memory_info[5]),
                         'kbcommit': int(memory_info[6]), '%commit': float(memory_info[7]),
                         'kbactive': int(memory_info[8]), 'kbinact': int(memory_info[9]),
                         'kbdirty': int(memory_info[10]), 'kbanonpg': int(memory_info[11]),
                         'kbslab': int(memory_info[12]), 'kbkstack': int(memory_info[13]),
                         'kbpgtbl': int(memory_info[14]), 'kbvmused': int(memory_info[15])})

        df = pd.DataFrame(memory_data)
        return df
