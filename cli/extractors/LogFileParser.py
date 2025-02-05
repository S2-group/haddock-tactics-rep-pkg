import re
from datetime import datetime

import pandas as pd

from data_analysis.CLI.extractors.Parser import IndividualParser


class LogFileParser(IndividualParser):
    @staticmethod
    def extract(file_path: str):
        start_pattern = re.compile(r'\[([\d-]+ [\d:]+),\d+ .+?\] Running \[(.+?)\] module')
        finish_pattern = re.compile(r'\[([\d-]+ [\d:]+),\d+ .+?\] Module \[(.+?)\] finished')

        events = []

        with open(file_path, 'r') as file:
            for line in file:
                start_match = start_pattern.search(line)
                finish_match = finish_pattern.search(line)

                if start_match:
                    timestamp_str, module = start_match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    events.append({'timestamp': timestamp.isoformat(), 'module': module, 'event': 'start'})

                if finish_match:
                    timestamp_str, module = finish_match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    events.append({'timestamp': timestamp.isoformat(), 'module': module, 'event': 'finish'})

        df = pd.DataFrame(events)
        df = df.sort_values(by='timestamp')
        return df
