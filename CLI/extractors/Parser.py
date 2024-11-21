import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Tuple, Callable


class Parser(ABC):
    @staticmethod
    @abstractmethod
    def extract(file_path: str):
        pass


class CombinedParser(Parser, ABC):
    @staticmethod
    @abstractmethod
    def extract_into_file(src: List[Tuple[str, str]], destination_path: str):
        """Extracts data from multiple files and writes to a single file
        Args:
            src: List of tuples of job_name and file_path
            destination_path: path to write the extracted data to
        """
        pass


class IndividualParser(Parser, ABC):
    @classmethod
    def extract_into_file(cls, src: List[Tuple[str, str]], get_destination_path: Callable[[Tuple[str, str]], str]):
        for job_name, file in src:
            try:
                df = cls.extract(file)
                dest_path = get_destination_path((job_name, file))
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                df.to_csv(dest_path, index=False)
            except FileNotFoundError as e:
                pass
            except Exception as e:
                print(f"{cls.__name__}: Failed to extract data from file {file}", e)

    @staticmethod
    def get_next_timestamp(prev_date, date, timestamp_str):
        time = datetime.strptime(timestamp_str, '%I:%M:%S %p').time()
        timestamp = datetime.combine(date, time)

        new_date = date
        # Check if day has changed
        if prev_date and timestamp < datetime.fromisoformat(prev_date):
            new_date += timedelta(days=1)
            timestamp = datetime.combine(new_date, time)
        return timestamp, new_date
