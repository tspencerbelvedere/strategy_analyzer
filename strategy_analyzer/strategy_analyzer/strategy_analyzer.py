"""
This module contains a class to produce a summary report of strategy performance
"""
from typing import Union

from strategy_analyzer.time_helpers import TimeHelper, CalendarConvention
from strategy_analyzer.portfolio_metrics import PortfolioMetrics

import pandas as pd


class StrategyAnalyzer():
    """
    Class to produce a summary report of strategy performance
    """
    def __init__(self,
                 returns_series: pd.Series,
                 risk_free_rate: float = 0.0,
                 strategy_name='Strategy',
                 days_per_year: Union[int, CalendarConvention] \
                     = CalendarConvention.TRADING_DAYS,
                ):
        """
        Initialize the StrategyAnalyzer object.

        Parameters:
        - returns_series: pd.DataFrame or pd.Series of returns (pct changes by period)
        - risk_free_rate: float, interest rate for levered returns
        - calendar_convention: CalendarConvention, the calendar convention to use
        """
        #Set The Strategy Name
        self._strategy_name = strategy_name
        #Set the risk free rate
        self._interest_rate = risk_free_rate
        #Set the calendar convention (default is trading days = 252)
        self._days_per_year = days_per_year
        # Clean up returns Series
        self.clean_returns = self._clean_returns(returns_series)
        # Infer time frequency of the returns_series (daily, weekly, monthly, etc..)
        self.time_frequency = TimeHelper.infer_frequency(self.clean_returns.index)


    @staticmethod
    def _clean_returns(returns: Union[pd.Series, pd.DataFrame]) -> pd.DataFrame:
        """
        Clean up returns by ensuring they are a pd.Series
        and that the index is a datetime
        and that there are no NaN values

        Parameters:
            returns (pd.Series|pd.DataFrame): The returns data to be cleaned.

        Returns:
            pd.DataFrame: The cleaned returns data as a DataFrame
            column with the strategy name as the column name.
        """
        if isinstance(returns, pd.Series):
            returns = returns.to_frame('Strategy')

        returns.index = pd.to_datetime(returns.index)

        # Drop all blank columns
        returns = returns.dropna(how='all', axis=1)

        # Fill remaining (row-wise) NaN values with 0 so we don't drop them
        # Assuming if there's no value, the return is 0
        returns = returns.fillna(0)

        # Ensure all values are floats
        returns = returns.copy().astype(float)

        return returns

    def get_summary(self):
        """
        Returns a dataframe of statistics for all metrics in this class
        for a given set of return streams (self.clean_returns)
        """

        annualized_return = PortfolioMetrics.get_annualized_return(self.clean_returns)
        annual_vol = PortfolioMetrics.get_annualized_volatility(self.clean_returns)
        sharpe = PortfolioMetrics.get_sharpe_ratio(self.clean_returns, self.time_frequency)
        sortino = PortfolioMetrics.get_sortino_ratio(self.clean_returns, self.time_frequency)
        calmar = PortfolioMetrics.get_calmar_ratio(self.clean_returns)
        maxdd = PortfolioMetrics.get_max_drawdown(self.clean_returns)
        time_in_market = PortfolioMetrics.get_time_in_market(self.clean_returns)
        # daily_vol = self.get_volatility(period=Period.DAILY, levered=levered)
        # weekly_vol = self.get_volatility(period=Period.WEEKLY, levered=levered)
        # monthly_vol = self.get_volatility(period=Period.MONTHLY, levered=levered)

        # maxdd_month = self.get_max_drawdown(period=Period.MONTHLY, levered=levered)
        # maxxdd_week = self.get_max_drawdown(period=Period.WEEKLY, levered=levered)
        # sharpe = self.get_sharpe_ratio(levered=levered)

        # daily_win_rate = self.get_win_rate(period=Period.DAILY)
        # monthly_win_rate = self.get_win_rate(period=Period.MONTHLY)

        # num_trades = self.get_num_trades()

        summary = pd.DataFrame(index=self.clean_returns.columns)
        summary['IRR'] = annualized_return
        summary['Maxdd'] = maxdd
        summary['TimeInMarket'] = time_in_market
        # # summary['NumTrades'] = num_trades
        # summary['Monthly WinRate'] = monthly_win_rate
        summary['Sortino'] = sortino
        summary['Sharpe'] = sharpe
        summary['Calmar'] = calmar
        # summary['Daily Vol'] = daily_vol
        # summary['Weekly Vol'] = weekly_vol
        # summary['Monthly Vol'] = monthly_vol
        summary['Annual Vol'] = annual_vol
        return summary.T
