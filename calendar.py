#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
交易日历处理
"""
import os
from datetime import date, datetime
from typing import Union, List

import pandas as pd
import requests

rest_days_df = None
chinese_holidays_range = None

def _init_chinese_rest_days(headers=None):
    global rest_days_df, chinese_holidays_range
    if rest_days_df is None:
        url = os.getenv("TQ_CHINESE_HOLIDAY_URL", "https://files.shinnytech.com/shinny_chinese_holiday.json")
        rsp = requests.get(url, timeout=30, headers=headers)
        chinese_holidays = rsp.json()
        _first_day = date(int(chinese_holidays[0].split('-')[0]), 1, 1)  # 首个日期所在年份的第一天
        _last_day = date(int(chinese_holidays[-1].split('-')[0]), 12, 31)  # 截止日期所在年份的最后一天
        chinese_holidays_range = (_first_day, _last_day)
        rest_days_df = pd.DataFrame(data={'date': pd.Series(pd.to_datetime(chinese_holidays, format='%Y-%m-%d'))})
        rest_days_df['trading_restdays'] = False  # 节假日为 False
    return chinese_holidays_range


def _get_trading_calendar(start_dt: date, end_dt: date, headers=None):
    _init_chinese_rest_days(headers=headers)
    df = pd.DataFrame()
    df['date'] = pd.Series(pd.date_range(start=start_dt, end=end_dt, freq="D"))
    df['trading'] = df['date'].dt.dayofweek.lt(5)
    result = pd.merge(rest_days_df, df, sort=True, how="right", on="date")
    result.fillna(True, inplace=True)
    df['trading'] = result['trading'] & result['trading_restdays']
    return df


class ContCalendar(object):
    continuous = None

    def __init__(self, start_dt: date, end_dt: date, symbols: Union[List[str], None] = None, headers=None) -> None:
        self.df = _get_trading_calendar(start_dt=start_dt, end_dt=end_dt, headers=headers)
        self.df = self.df.loc[self.df.trading, ['date']]
        self.df.reset_index(inplace=True, drop=True)
        if ContCalendar.continuous is None:
            rsp = requests.get(os.getenv("TQ_CONT_TABLE_URL", "https://files.shinnytech.com/continuous_table.json"), headers=headers)  
            rsp.raise_for_status()
            ContCalendar.continuous = {f"KQ.m@{k}": v for k, v in rsp.json().items()}
        if symbols is not None:
            if not all([s in ContCalendar.continuous.keys() for s in symbols]):
                raise Exception(f"参数错误，symbols={symbols} 中应该全部都是主连合约代码")
        symbols = ContCalendar.continuous.keys() if symbols is None else symbols
        self.start_dt, self.end_dt = self.df.iloc[0].date, self.df.iloc[-1].date
        for s in symbols:
            self._ensure_cont_on_df(s)

    def _ensure_cont_on_df(self, cont):
        temp_df = pd.DataFrame(data=ContCalendar.continuous[cont], columns=['date', 'underlying'])
        temp_df['date'] = pd.Series(pd.to_datetime(temp_df['date'], format='%Y%m%d'))
        merge_result = pd.merge(temp_df, self.df, sort=True, how="outer", on="date")
        merge_result.fillna(method="ffill", inplace=True)
        merge_result.fillna(value="", inplace=True)
        s = merge_result.loc[merge_result.date.ge(self.start_dt) & merge_result.date.le(self.end_dt), 'underlying']
        self.df[cont] = pd.Series(s.values)

    def _get_cont_underlying_on_date(self, dt: datetime):
        df = self.df.loc[self.df.date.ge(dt), :]
        return df.iloc[0:1]
