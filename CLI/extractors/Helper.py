from pathlib import Path

from data_analysis.CLI.extractors.CPUFrequencyParser import CPUFrequencyParser


class Helper:
    @staticmethod
    def get_start_date(file_path):
        timestamp_file = Path(file_path).parent / 'cpu_frequency.log'
        with open(timestamp_file, 'r') as file:
            timestamp_line = file.readline()
            timestamp_match = CPUFrequencyParser.timestamp_pattern.match(timestamp_line)
            timestamp = CPUFrequencyParser.extract_timestamp(timestamp_match)
            return timestamp.date()
