"""
Helper classes for determing the frequency of a datetime index
particularly when the index does not have a constant frequency
such as stock returns which do not include weekends and holidays
"""

from typing import Union

import pandas as pd
import numpy as np

class CalendarConvention():
    """
    Class for Calendar Conventions (365 calendar days per year, 252 trading days)
    """
    TRADING_DAYS = pd.Timedelta('252D')
    CALENDAR_DAYS = pd.Timedelta('365D')


class TimeHelper:
    """
    Class to help with time-related operations.
    """
    def __init__(self) -> None:
        pass

    @staticmethod
    def _convert_to_datetime_index(datetimes: Union[list, np.array, pd.DatetimeIndex]) \
                                    -> pd.DatetimeIndex:
        """
        Convert a list, numpy array, or pandas DatetimeIndex to a pandas DatetimeIndex.

        Parameters:
        datetimes (Union[list, np.array, pd.DatetimeIndex]): The input datetimes to be converted.

        Returns:
        pd.DatetimeIndex: The converted pandas DatetimeIndex.
        """
        return pd.to_datetime(datetimes)

    @staticmethod
    def _get_time_diffs_seconds(datetimes: pd.DatetimeIndex) -> np.ndarray:
        """
        Calculate the time differences in seconds between consecutive datetimes.

        Parameters:
        datetimes (pd.DatetimeIndex): A pandas DatetimeIndex containing the datetimes.

        Returns:
        np.ndarray: An array of time differences in seconds.
        """
        return np.diff(datetimes).astype('timedelta64[D]')

    @staticmethod
    def _get_most_common_time_diff(time_diffs: pd.DatetimeIndex,
                                   minimum_mode_percentage: float = 0.6) -> pd.Timedelta:
        """
        Calculate the most common time difference in a given list of time differences.

        Args:
            time_diffs (pd.DatetimeIndex): A pandas DatetimeIndex containing the time differences.
            minimum_mode_percentage (float, optional): The minimum percentage of the mode required to consider it valid.
                Defaults to 0.6.

        Returns:
            pd.Timedelta: The most common time difference.

        Raises:
            ValueError: If the mode percentage is less than the minimum mode percentage.

        """
        time_diff_counts = pd.Series(time_diffs).value_counts()
        time_diff_distribution = time_diff_counts / len(time_diffs)
        mode_percentage = time_diff_distribution.max()
        time_diff_mode = time_diff_distribution.index[0]

        if mode_percentage < minimum_mode_percentage:
            raise ValueError('Mode percentage less than minimum mode percentage')
        return time_diff_mode

    @staticmethod
    def infer_frequency(datetimes: Union[list, np.array, pd.DatetimeIndex],
                        minimum_mode_percentage: float = 0.6) -> pd.Timedelta:
        """
        Infers the frequency of the time series based on the most common
        time difference between the datetimes.

        Args:
            datetimes (Union[list, np.array, pd.DatetimeIndex]):
                A list, numpy array, or pandas DatetimeIndex
                containing datetime objects to infer the frequency from.

            minimum_mode_percentage (float, optional):
                The minimum percentage the most common time difference
                must have to be considered valid. Defaults to 0.6.

        Returns:
            pd.Timedelta: The most common time difference between consecutive datetime objects
                in `datetimes`, if it meets or exceeds the `minimum_mode_percentage`.

        Raises:
            ValueError: If the mode percentage of the most common time difference is less than
                `minimum_mode_percentage`.
        """
        datetimes = TimeHelper._convert_to_datetime_index(datetimes)
        time_diffs = TimeHelper._get_time_diffs_seconds(datetimes)
        most_common_time_diff = TimeHelper._get_most_common_time_diff(time_diffs,
                                                                      minimum_mode_percentage)
        return most_common_time_diff


    @staticmethod
    def get_num_periods_per_year(time_delta: pd.Timedelta,
                                 calendar_convention: CalendarConvention = \
                                 CalendarConvention.TRADING_DAYS) -> float:
        """
        Calculate the number of periods per year given a time delta.

        Args:
            time_delta (pd.Timedelta): The time delta to calculate the number
            of periods per year from.

        Returns:
            float: The number of periods per year.
        """
        if time_delta == pd.Timedelta('1D'):
            return  calendar_convention / time_delta
        elif time_delta == pd.Timedelta('1W'):
            return 52
        elif time_delta == pd.Timedelta('1M'):
            return 12
        elif time_delta == pd.Timedelta('1Y'):
            return 1
        else:
            raise ValueError(f'Time delta must be in (1D, 1W, 1M, 1Y): {time_delta}')
