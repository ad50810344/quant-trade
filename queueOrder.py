from matplotlib import dates
import pandas as pd

def orderAnalyse():
    import os
    # flog = os.getcwd() + "/logs"
    # if os.path.isfile(flog) != True:
    #     p = Path(flog)
    #     p.mkdir(exist_ok=True)
    file = "/home/du/2018-2022/futureQuantity/DuShuai/projectTqsdk/analyseTrade01/trade01/order_queue.csv"
    datas = pd.read_csv(file)
    insertOrders = datas[(datas["type"] == "insert")]
    sortInsertOrders = insertOrders.sort_values("time", ignore_index=True)
    #交易次数/盈亏比/胜率/单次最大亏损/单次最大盈利/A腿成交前价差/B腿成交时价差
    print(sortInsertOrders)
    tradeNums = sortInsertOrders["order_id"].iloc[-1]
    print(tradeNums)




orderAnalyse()