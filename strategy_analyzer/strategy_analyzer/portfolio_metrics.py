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

    # def get_win_rate(PortfolioMetrics, period=Period.DAILY):
    #     """
    #     Calculates the win rate of a return series
    #     given a period length
    #     """
    #     int_period = int(period)
    #     cumprod = PortfolioMetrics.cumprod(start_point=1.0)
    #     period_returns = cumprod.pct_change(int_period).dropna()
    #     winners = period_returns[period_returns > 0].count()
    #     losers = period_returns[period_returns < 0].count()
    #     total = winners / (winners + losers)

    #     return total









    # def get_rolling_returns(PortfolioMetrics, period=Period.ANNUAL, levered=False):
    #     """
    #     Calculates the rolling returns of a return series
    #     """
    #     int_period = int(period)
    #     if levered:
    #         returns = PortfolioMetrics.levered_returns
    #     else:
    #         returns = returns_series
    #     return (returns + 1).rolling(int_period).apply(lambda x: x.prod() - 1)

    # def get_summary(PortfolioMetrics, levered=False):
    #     """
    #     Returns a dataframe of statistics for all metrics in this class
    #     for a given set of return streams (returns_series)
    #     """
    #     annualized_return = PortfolioMetrics.get_annualized_return(levered=levered)
    #     annual_vol = PortfolioMetrics.get_volatility(period=Period.ANNUAL, levered=levered)
    #     daily_vol = PortfolioMetrics.get_volatility(period=Period.DAILY, levered=levered)
    #     weekly_vol = PortfolioMetrics.get_volatility(period=Period.WEEKLY, levered=levered)
    #     monthly_vol = PortfolioMetrics.get_volatility(period=Period.MONTHLY, levered=levered)
    #     maxdd = PortfolioMetrics.get_max_drawdown(levered=levered)
    #     maxdd_month = PortfolioMetrics.get_max_drawdown(period=Period.MONTHLY, levered=levered)
    #     maxxdd_week = PortfolioMetrics.get_max_drawdown(period=Period.WEEKLY, levered=levered)
    #     sharpe = PortfolioMetrics.get_sharpe_ratio(levered=levered)
    #     calmar = PortfolioMetrics.get_calmar_ratio(levered=levered)
    #     sortino = PortfolioMetrics.get_sortino_ratio(levered=levered)
    #     daily_win_rate = PortfolioMetrics.get_win_rate(period=Period.DAILY)
    #     monthly_win_rate = PortfolioMetrics.get_win_rate(period=Period.MONTHLY)
    #     time_in_market = PortfolioMetrics.get_time_in_market()
        # num_trades = PortfolioMetrics.get_num_trades()

        summary = pd.DataFrame(index=returns_series.columns)
        summary['IRR'] = annualized_return
        summary['Maxdd'] = maxdd
        summary['Maxdd 1 Month'] = maxdd_month
        summary['Maxdd 1 Week'] = maxxdd_week
        summary['Daily WinRate'] = daily_win_rate
        summary['TimeInMarket'] = time_in_market
        # summary['NumTrades'] = num_trades
        summary['Monthly WinRate'] = monthly_win_rate
        summary['Sortino'] = sortino
        summary['Sharpe'] = sharpe
        summary['Calmar'] = calmar
        summary['Daily Vol'] = daily_vol
        summary['Weekly Vol'] = weekly_vol
        summary['Monthly Vol'] = monthly_vol
        summary['Annual Vol'] = annual_vol
        summary['Leverage'] = PortfolioMetrics.leverage
        return summary.T