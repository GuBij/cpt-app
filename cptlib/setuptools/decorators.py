import functools
from collections.abc import Callable
from typing import Any

func_type = Callable[[Any],list[dict]]

def filter(field: str) -> Callable[[func_type], func_type]:
  def decorator(read_func: func_type) -> func_type:
    """
    Return a function that cleans the output of *read_func* such that all the records (read by *read_func*) for which *field* is unavailable are removed.

    *read_func* must return a list of dictionaries.
    """    
    @functools.wraps(read_func)
    def remove_NoneTypes(*args, **kwargs) -> list[dict]:
      records: list[dict] = read_func(*args, **kwargs)
      records_filtered: list[dict] = []
      LEN_RECORDS: int = len(records)
      for record in records:
        if record[field] is not None:
          records_filtered.append(record)
      
      LEN_FILTERED_RECORDS: int = len(records_filtered)
      if LEN_RECORDS-LEN_FILTERED_RECORDS:
        print(f"\nRemoved {LEN_RECORDS-LEN_FILTERED_RECORDS} records "\
              f"of which the field '{field}' is unavailable.")
      
      return records_filtered
    return remove_NoneTypes
  return decorator
