"""
Class to calculate various portfolio metrics used for performance evaluation
"""


from typing import Union

from strategy_analyzer.time_helpers import TimeHelper, CalendarConvention

import pandas as pd
import numpy as np


class PortfolioMetrics:
    """
    Calculated various Portfolio Metrics used for performance evaluation
    """
    def __init__(self):
        pass

    @staticmethod
    def get_returns_length_in_years(returns_series: Union[pd.Series, pd.DataFrame]) -> pd.Series:
        """
        Calculates the number of years in a return series
        """
        start_date = returns_series.index[0]
        end_date = returns_series.index[-1]
        years = (end_date - start_date).days / 365.25
        return years

    @staticmethod
    def get_cumulative_returns(returns_series: Union[pd.Series, pd.DataFrame],
                               start_point: Union[float, int] = 1.0) -> pd.DataFrame:
        """
        Calculates cumulative returns of a return series.

        Parameters:
        - returns_series: The return series to calculate the cumulative returns of.
        - start_point: The starting point for the cumulative returns calculation.

        Returns:
        - cumulative_returns: The cumulative returns of the return series.

        """
        zero_start_point = returns_series.add(1).cumprod() - 1
        return zero_start_point + start_point


    @staticmethod
    def get_annualized_return(returns_series: Union[pd.Series, pd.DataFrame]) -> pd.DataFrame:
        """
        calculates the annualized rate of return for a returns series
        """
        cumulative_returns = PortfolioMetrics.get_cumulative_returns(returns_series,
                                                                    start_point=1.0)

        years = PortfolioMetrics.get_returns_length_in_years(returns_series)
        return np.log(cumulative_returns.iloc[-1]) / years

    @staticmethod
    def get_annualized_volatility(returns_series: Union[pd.Series, pd.DataFrame],
                                        sharpe_time_frequency: Union[None, pd.Timedelta] = None,
                                        calendar_convention: CalendarConvention \
                                            = CalendarConvention.TRADING_DAYS):
        """
        Calculates the volatility of a return series depending on the period length.

        Args:
        - returns_series: The return series to calculate the volatility of.
        - time_frequency: The frequency of the return series.
        - sharpe_time_frequency: The frequency of the Sharpe ratio.
        Returns:
        - annualized_volatility (float): The annualized volatility of the return series.
        """

        series_time_frequency = TimeHelper.infer_frequency(returns_series.index)
        series_periods_per_year = TimeHelper.get_num_periods_per_year(series_time_frequency,
                                                                    calendar_convention)
        if sharpe_time_frequency:
            sharpe_periods_per_year = TimeHelper.get_num_periods_per_year(sharpe_time_frequency,
                                                                    calendar_convention)
        else:
            sharpe_periods_per_year = TimeHelper.get_num_periods_per_year(series_time_frequency,
                                                                    calendar_convention)

        rolling_window = int(sharpe_periods_per_year / series_periods_per_year)
        cumulative_returns = PortfolioMetrics.get_cumulative_returns(returns_series,
                                                                        start_point=1.0) + 1
        period_returns = cumulative_returns.pct_change(rolling_window).dropna()
        sqrt_t = np.sqrt(sharpe_periods_per_year)
        period_volatility = period_returns.std()
        annualized_volatility = period_volatility * sqrt_t

        return annualized_volatility

    @staticmethod
    def get_underwater(returns_series: Union[pd.Series, pd.DataFrame]):
        """
        Calculates the underwater plot of a return series
        """
        cumulative = PortfolioMetrics.get_cumulative_returns(returns_series,
                                                             start_point=1.0)
        return (cumulative / cumulative.cummax() - 1)

    @staticmethod
    def get_max_drawdown(returns_series: Union[pd.Series, pd.DataFrame]):
        """
        Calculates the maximum drawdown of a return series
        """
        underwater = PortfolioMetrics.get_underwater(returns_series)

        return underwater.min()

    @staticmethod
    def get_max_drawdown_date(returns_series: Union[pd.Series, pd.DataFrame]):
        """
        Calculates the maximum drawdown of a return series
        """
        under_water = PortfolioMetrics.get_underwater(returns_series)

        return under_water.idxmin()

    @staticmethod
    def get_sharpe_ratio(returns_series: Union[pd.Series, pd.DataFrame],
                         time_frequency: Union[None, pd.Timedelta] = None):
        """
        Calculates the Sharpe ratio of a return series
        given a period length
        """

        return_means = returns_series.mean()
        return_stds = returns_series.std()
        periods_per_year = TimeHelper.get_num_periods_per_year(time_frequency)

        annualized_adjustment = np.sqrt(periods_per_year)

        return (return_means / return_stds) * annualized_adjustment

    @staticmethod
    def get_sortino_ratio(returns_series: Union[pd.Series, pd.DataFrame],
                          time_frequency: Union[None, pd.Timedelta] = None):
        """
        Calculates the Sortino ratio of a return series
        given a period length
        """
        positive_returns = returns_series[returns_series > 0]
        return_means = returns_series.mean()
        return__negative_stds = positive_returns.std()
        periods_per_year = TimeHelper.get_num_periods_per_year(time_frequency)
        annualized_adjustment = np.sqrt(periods_per_year)

        return (return_means / return__negative_stds) * annualized_adjustment

    @staticmethod
    def get_calmar_ratio(returns_series: Union[pd.Series, pd.DataFrame]):
        """
        Calculates the Calmar ratio of a return series
        """
        annualized_return = PortfolioMetrics.get_annualized_return(returns_series)
        maxdd = abs(PortfolioMetrics.get_max_drawdown(returns_series))
        return annualized_return / maxdd

    @staticmethod
    def get_time_in_market(returns_series: Union[pd.Series, pd.DataFrame]):
        """
        Calculates the percentage of time in market of a return series
        Assumes no-position means a 0 return in the series
        """

        return (returns_series != 0).sum() / len(returns_series)

    @staticmethod
    def resample_returns(returns_series: Union[pd.Series, pd.DataFrame],
                         time_frequency: pd.Timedelta) -> pd.DataFrame:
        """
        Resamples a return series to a given time frequency.
        """
        cumulative_returns = PortfolioMetrics.get_cumulative_returns(returns_series,
                                                                    start_point=1.0)
        return cumulative_returns.resample(time_frequency).last().pct_change().dropna()
