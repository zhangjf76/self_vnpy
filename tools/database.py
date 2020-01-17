# -*- coding:utf-8 -*-
import sqlite3
import csv
import pandas as pd
import numpy as np

from tools.wapper import run_time


class DatabaseSqlite(object):
    """
    sqlite 数据库操作类
    调用示例：
    from tools.database import DatabaseSqlite

    queryset = DatabaseSqlite()
    result = queryset.query_future(symbol='rb2001', begin_date='2019-11-11', end_date='2019-11-11')
    """
    database_path = "C:\\self_vnpy\\.vntrader\\database.db"
    db_connect = object
    cursor = object

    def __init__(self, database_path=""):
        if database_path:
            self.database_path = database_path
        self.connect()

    def query_future(self, symbol='', interval='1m', begin_date=None,
                     end_date=None, fields=None, used_close=False):
        """
        @param: interval ('1m', 'd')
        """
        if fields is None:
            fields = ['symbol', 'datetime', 'interval', 'volume', 'open_price', 'high_price', 'close_price']
        fields_str = '' if len(fields) == 0 else ', '.join(fields)

        sql_base = f"SELECT {fields_str} FROM dbbardata"
        sql_order = " ORDER BY datetime ASC"
        sql_filter = f" WHERE interval='{interval}'"
        if symbol:
            sql_filter += f" AND symbol='{symbol}'"
        if begin_date:
            sql_filter += f" AND datetime>='{begin_date}'"
        if end_date:
            end_date += ' 23:59:59'
            sql_filter += f" AND datetime<='{end_date}'"

        self.cursor.execute(sql_base + sql_filter + sql_order)
        result = self.cursor.fetchall()

        if used_close:
            self.close()

        return result

    def import_csv_single(self, csv_file_path, symbol, exchange, interval="1m"):
        """通过csv插入/更新数据库数据"""
        data_frame = pd.read_csv(csv_file_path)
        data_frame.sort_values(by="Datetime", ascending=True, inplace=True)

        for index, row in data_frame.iterrows():
            query_sql = """
            SELECT COUNT(*) FROM dbbardata WHERE symbol='%s' AND interval='%s' AND datetime='%s'
            """ % (symbol, interval, row["Datetime"])
            self.cursor.execute(query_sql)
            count = self.cursor.fetchone()[0]

            if count > 0:
                update_sql = """
                UPDATE dbbardata 
                SET 
                    volume='%s', open_price='%s', high_price='%s', low_price='%s', close_price='%s' 
                WHERE 
                    symbol='%s' AND interval='%s' AND datetime='%s'
                """ % (
                    row["Volume"],
                    row["Open"],
                    row["High"],
                    row["Low"],
                    row["Close"],
                    symbol,
                    interval,
                    row["Datetime"]
                )
                self.cursor.execute(update_sql)
            else:
                insert_sql = """
                insert into 
                    dbbardata(symbol, exchange, datetime, interval, volume, open_interest, open_price, high_price, low_price, close_price)
                values 
                    ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
                """ % (
                    symbol,
                    exchange,
                    row["Datetime"],
                    interval,
                    row["Volume"],
                    "",
                    row["Open"],
                    row["High"],
                    row["Low"],
                    row["Close"],
                )
                self.cursor.execute(insert_sql)

        self.db_connect.commit()

    def connect(self):
        self.db_connect = sqlite3.connect(self.database_path)
        self.cursor = self.db_connect.cursor()

    def close(self):
        self.cursor.close()
        self.db_connect.close()

