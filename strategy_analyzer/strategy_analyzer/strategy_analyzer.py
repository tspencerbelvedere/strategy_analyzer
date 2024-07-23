"""
This module contains a class to produce a summary report of strategy performance
"""
import pandas as pd
import numpy as np

class Period():
    """
    Get Number of days for a given period
    or number of instances per year
    """
    ANNUAL = 252
    MONTHLY = 20
    WEEKLY = 5
    DAILY = 1
    TRADING_DAYS_PER_YEAR = 252.
    CALENDAR_DAYS_PER_YEAR = 365.
    def __init__(self):
        pass

    @staticmethod
    def get_instances_per_year(period):
        """
        Returns the number of instances per year
        """
        return int(Period.TRADING_DAYS_PER_YEAR / float(period))

class StrategyAnalyzer():
    """
    Class to produce a summary report of strategy performance
    """
    def __init__(self, returns, target_return=None, interest_rate=None):
        """
        returns: pd.DataFrame or pd.Series of returns (pct changes by day)
        target_return: float, target return for levered returns
        interest_rate: float, interest rate for levered returns
        """

        self.clean_returns = self.clean_returns_first(returns)
        self.levered_returns = self.get_levered_returns(target_return, interest_rate)
        #1 by default, overriden if possible
        self.leverage = 1
    @staticmethod
    def clean_returns_first(returns):
        """
        Clean up returns by ensuring they are a pd.Series
        and that the index is a datetime
        and that there are no NaN values
        """
        if isinstance(returns, pd.Series):
            returns = returns.to_frame('Strategy')
        returns.index = pd.to_datetime(returns.index)

        #Drop all blank columns
        returns = returns.dropna(how='all', axis=1)

        #fill remaining (row-wise)NaN values with 0 so we don't drop them
        returns = returns.fillna(0)

        return returns.copy().astype(float)
    
    def get_levered_returns(self, target_return=None, interest_rate=None):
        """
        Calculate levered returns of a series
        """
        clean_returns = self.clean_returns
        if target_return and interest_rate:
            annualized_return = self.get_annualized_return()
            time_in_market = self.get_time_in_market()
            interest_cost = interest_rate * time_in_market
            leverage = target_return / (annualized_return - interest_cost)
            leverage = leverage.clip(lower=0.0)
            self.leverage = leverage
            levered_returns = clean_returns * leverage
            return levered_returns
        return clean_returns

    def cumprod(self, start_point=0.0, levered=False):
        """
        Calculate cumulative returns of a series
        by adding 1 to a series of returns,
        calculating the cumulative product,
         ex:
            if start_point is 0, the cumulative returns begin at 0
            if start_point is 1, the cumulative returns begin at 1
        """
        if levered:
            clean_returns = self.levered_returns
        else:
            clean_returns = self.clean_returns
        zero_start_point = clean_returns.add(1).cumprod() - 1
        return zero_start_point + start_point

    def get_returns_period(self, period=Period.DAILY, levered=False):
        """
        Calculates the expected return for a given period
        based on the total return of the series
        """
        cumulative_returns = self.cumprod(start_point=1.0, levered=levered)
        int_period = int(period)
        total_return = cumulative_returns.iloc[-1]
        years = self.get_returns_length_in_years()
        periods_per_year = Period.get_instances_per_year(int_period)
        return np.log(total_return) / (years * periods_per_year)

    def get_returns_length_in_years(self):
        """
        Calculates the number of years in a return series
        """
        clean_returns = self.clean_returns
        days = (clean_returns.index.max() - clean_returns.index.min()).days
        years = days / Period.CALENDAR_DAYS_PER_YEAR
        return years

    def get_cumulative_returns(self, levered=False):
        """
        Calculates cumulative returns of a return series
        """
        return self.cumprod(start_point=0.0, levered=levered)

    def get_cumulative_return(self, levered=False):
        """
        Calculates the cumulative return of a return series
        """
        cumulative = self.get_cumulative_returns(levered=levered)
        return cumulative.dropna().iloc[-1]

    def get_annualized_return(self, levered=False):
        """
        calculates the annualized rate of return for a returns series
        """
        cumulative = self.get_cumulative_return(levered=levered) + 1
        return np.log(cumulative) / self.get_returns_length_in_years()

    def get_volatility(self, annualized=True, period=Period.ANNUAL, levered=False):
        """
        Calculates the volatility of a
        return series depending on the period length
        """
        int_period = int(period)
        cumulative_returns = self.get_cumulative_returns(levered=levered) + 1
        period_returns = cumulative_returns.pct_change(int_period).dropna()
        sqrt_t = np.sqrt(Period.get_instances_per_year(int_period))
        period_volatility = period_returns.std()
        annualized_volatility = period_volatility * sqrt_t
        if annualized:
            return annualized_volatility
        return period_volatility

    def get_max_drawdown(self, period=None, levered=False):
        """
        Calculates the maximum drawdown of a return series
        """
        cumulative = self.get_cumulative_returns(levered=levered) + 1
        if period:
            return (cumulative / cumulative.rolling(period).max()).min() - 1
        #Use cummax to get the maximum drawdown of the whole series
        return (cumulative / cumulative.cummax()).min() - 1

    def get_max_drawdown_date(self, levered=False):
        """
        Calculates the maximum drawdown of a return series
        """
        cumulative = self.get_cumulative_returns(levered=levered) + 1
        drawdown = (cumulative / cumulative.cummax()).sort_values()
        return drawdown.index[0]

    def get_sharpe_ratio(self, period=Period.DAILY, levered=False):
        """
        Calculates the Sharpe ratio of a return series
        given a period length
        """
        int_period = int(period)
        cumulative_returns = self.get_cumulative_returns(levered=levered) + 1
        periods_per_year = Period.get_instances_per_year(int_period)
        rolling_returns = cumulative_returns.pct_change(int_period).dropna()
        return_mean = rolling_returns.mean()
        return_std = rolling_returns.std()
        annualized_adjustment = np.sqrt(periods_per_year)
        return (return_mean / return_std) * annualized_adjustment

    def get_win_rate(self, period=Period.DAILY):
        """
        Calculates the win rate of a return series
        given a period length
        """
        int_period = int(period)
        cumprod = self.cumprod(start_point=1.0)
        period_returns = cumprod.pct_change(int_period).dropna()
        winners = period_returns[period_returns > 0].count()
        losers = period_returns[period_returns < 0].count()
        total = winners / (winners + losers)

        return total

    def get_sortino_ratio(self, period=Period.DAILY, levered=False):
        """
        Calculates the Sortino ratio of a return series
        given a period length
        """
        int_period = int(period)
        cumulative_returns = self.get_cumulative_returns(levered=levered) + 1
        periods_per_year = Period.get_instances_per_year(int_period)
        rolling_returns = cumulative_returns.pct_change(int_period).dropna()
        return_mean = rolling_returns.mean()
        return_std = rolling_returns[rolling_returns < 0].std()
        annualized_adjustment = np.sqrt(periods_per_year)
        return (return_mean / return_std) * annualized_adjustment

    def get_time_in_market(self):
        """
        Calculates the time in market of a return series
        """
        clean_returns = self.clean_returns
        return (clean_returns!= 0).sum() / len(clean_returns)

    def get_calmar_ratio(self, levered=False):
        """
        Calculates the Calmar ratio of a return series
        """
        annualized_return = self.get_annualized_return(levered=levered)
        maxdd = abs(self.get_max_drawdown(levered=levered))
        return annualized_return / maxdd
    
    def get_underwater(self, levered=False):
        """
        Calculates the underwater plot of a return series
        """
        cumulative = self.get_cumulative_returns(levered=levered) + 1
        return (cumulative / cumulative.cummax() - 1)

    def get_rolling_returns(self, period=Period.ANNUAL, levered=False):
        """
        Calculates the rolling returns of a return series
        """
        int_period = int(period)
        if levered:
            returns = self.levered_returns
        else:
            returns = self.clean_returns
        return (returns + 1).rolling(int_period).apply(lambda x: x.prod() - 1)
 
    def get_summary(self, levered=False):
        """
        Returns a dataframe of statistics for all metrics in this class
        for a given set of return streams (self.clean_returns)
        """
        annualized_return = self.get_annualized_return(levered=levered)
        annual_vol = self.get_volatility(period=Period.ANNUAL, levered=levered)
        daily_vol = self.get_volatility(period=Period.DAILY, levered=levered)
        weekly_vol = self.get_volatility(period=Period.WEEKLY, levered=levered)
        monthly_vol = self.get_volatility(period=Period.MONTHLY, levered=levered)
        maxdd = self.get_max_drawdown(levered=levered)
        maxdd_month = self.get_max_drawdown(period=Period.MONTHLY, levered=levered)
        maxxdd_week = self.get_max_drawdown(period=Period.WEEKLY, levered=levered)
        sharpe = self.get_sharpe_ratio(levered=levered)
        calmar = self.get_calmar_ratio(levered=levered)
        sortino = self.get_sortino_ratio(levered=levered)
        daily_win_rate = self.get_win_rate(period=Period.DAILY)
        monthly_win_rate = self.get_win_rate(period=Period.MONTHLY)
        time_in_market = self.get_time_in_market()
        # num_trades = self.get_num_trades()

        summary = pd.DataFrame(index=self.clean_returns.columns)
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
        summary['Leverage'] = self.leverage
        return summary.T

