#0311界面监控
import PySimpleGUI as sg
import matplotlib
import numpy as np
from scipy import stats
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import NullFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')

fig = matplotlib.figure.Figure(figsize=(17, 3), dpi=100)
#传入数据变量
t = np.arange(0, 3, .01)
t1 = 3 * t + 10
x = np.arange(1, 11)
y = 2 * x + 5
plt.ylabel("策略盈亏")
plt.xlabel("时间")
fig.add_subplot(121).plot(t, t1)
fig.add_subplot(122).plot(x,y)


def drawPlot():
    x = np.arange(1, 11)
    y = 2 * x + 5
    plt.plot(x, y)
    plt.show()


def drawFigure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def gui_func():
    data = pd.read_csv("example.csv")

    with open('config.json','r') as jsonFile:
        loaded = json.load(jsonFile)
        print(loaded["list"][0]["ticker1"])

    sg.ChangeLookAndFeel('GreenTan')

    # ------ Menu Definition ------ #

    menu_def = [['&系统', ['&Open', '&Save', 'E&xit', 'Properties']],
                ['&账户', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['&交易模型', '&About...'], ]

    # ------ Column Definition ------ #
    column1 = [[sg.Text('Column 1', background_color='lightblue', justification='center', size=(10, 1))],
            [sg.Spin(values=('Spin Box 1', '2', '3'), initial_value='Spin Box 1')],
            [sg.Spin(values=('Spin Box 1', '2', '3'), initial_value='Spin Box 2')],
            [sg.Spin(values=('Spin Box 1', '2', '3'), initial_value='Spin Box 3')]]

    layout = [
        [sg.Menu(menu_def, tearoff=False)],

        [sg.Text("动态权益", size=(22, 1), justification='center', font=("Helvetica", 12), relief=sg.RELIEF_RIDGE), 
        sg.Text("19002300", key= "账户权益", size= (22, 1), font=("Helvetica", 14), relief=sg.RELIEF_RIDGE),
        sg.Text("平仓盈亏", size= (22, 1), justification= "center", font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),
        sg.Text("20013", key = "风险度", size= (22, 1), font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),

        sg.Text("手续费", size= (22, 1), justification= "center", font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),
        sg.Text("8922", key = "总收益", size= (22, 1), font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),
        sg.Text("净盈亏", size= (22, 1), justification= "center", font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),
        sg.Text("11091", key = "总收益", size= (22, 1), font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),],

        [sg.Text('_' * 250)],

        [sg.Text("期货账号", size= (7, 1), justification='center'),
        sg.Text("价差自动", size= (7, 1), justification='center'),
        sg.Text("策略编号", size= (7, 1), justification='center'),
        sg.Text("合约代码", size= (7, 1), justification='center'),
        sg.Text("策略开关", size= (7, 1), justification='center'),
        sg.Text("信号开关", size= (7, 1), justification='center'),
        sg.Text("分配资金", size= (7, 1), justification='center'),
        sg.Text("持仓资金", size= (7, 1), justification='center'),
        sg.Text("分配仓位", size= (7, 1), justification='center'),
        sg.Text("总持仓", size= (7, 1), justification='center'),
        sg.Text("买持仓", size=(7,1), justification='center'), 
        sg.Text("卖持仓", size=(7,1), justification='center'), 
        sg.Text("买价", size=(7,1), justification='center'), 
        sg.Text("卖价", size=(7,1), justification='center'), 
        sg.Text("持仓盈亏", size= (7, 1), justification='center'),
        sg.Text("平仓盈亏", size= (7, 1), justification='center'),
        sg.Text("手续费", size= (7, 1), justification='center'),
        sg.Text("净盈亏", size= (7, 1), justification='center'),
        sg.Text("A成交率", size= (7, 1), justification='center'),
        sg.Text("B成交率", size= (7, 1), justification='center'),
        sg.Text("A撤单统计", size= (7, 1), justification='center'),
        sg.Text("A撤单限制", size= (7, 1), justification='center'),
        sg.Text("超价触发", size= (7, 1), justification='center'),
        sg.Text("A时效", size= (7, 1), justification='center'),
        sg.Text("AFAK次数", size=(7,1), justification='center'), 
        sg.Text("成交量", size=(7,1), justification='center'), 
        sg.Text("成交总额", size=(7,1), justification='center'),
        sg.Text("BFAK次数", size=(7,1), justification='center')],

        [sg.Text("1323", key= "期货账号1", size= (7, 1), auto_size_text=True, justification='center'),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号2", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号1", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号1", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号1", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号1", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号1", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号1", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号1", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号1", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        [sg.Text("77710191", key= "期货账号1", size= (7, 1)),
        sg.Text("true", key = "价差自动", size= (7, 1)),
        sg.Text("1", key= "策略编号", size =(7, 1)),
        sg.Text("cu2207/cu2204", key= "合约代码", size= (7, 1)),
        sg.Text("true", key= "策略开关", size= (7, 1)),
        sg.Text("true", key= "信号开关", size= (7, 1)),
        sg.Text("200000", key= "分配资金", size= (7, 1)),
        sg.Text("100000", key= "持仓资金", size= (7, 1)),
        sg.Text("20",key= "分配仓位", size= (7, 1)),
        sg.Text("20", key= "总持仓", size= (7, 1)),
        sg.Text("10", key = "买持仓", size=(7,1)), 
        sg.Text("0", key = "卖持仓", size=(7,1)), 
        sg.Text("10", key = "买价", size=(7,1)), 
        sg.Text("30", key = "卖价",size=(7,1)),
        sg.Text("1000", key= "持仓盈亏", size= (7, 1)),
        sg.Text("2000", key = "平仓盈亏", size= (7, 1)),
        sg.Text("1700", key= "手续费", size =(7, 1)),
        sg.Text("2000", key= "净盈亏", size= (7, 1)),
        sg.Text("0.20", key= "A成交率", size= (7, 1)),
        sg.Text("0.77", key= "B成交率", size= (7, 1)),
        sg.Text("470", key= "A撤单统计", size= (7, 1)),
        sg.Text("470", key= "B撤单限制", size= (7, 1)),
        sg.Text("2/2/0",key= "超价触发", size= (7, 1)),
        sg.Text("GFD", key= "A时效", size= (7, 1)),
        sg.Text("20000", key = "AFAK次数", size=(7,1)), 
        sg.Text("70", key = "成交量", size=(7,1)), 
        sg.Text("400000", key = "成交总额", size=(7,1)), 
        sg.Text("70000", key = "BFAK次数",size=(7,1))],

        # [sg.Slider(range=(1,500), size=(170,10), orientation='horizontal', font=('Helvetica', 12))],
        # [sg.ProgressBar(1, orientation='h', size=(170,20), key='progress')],
        [sg.Text('_' * 250)],

        [sg.InputText("子策略收益/单策略收益")],
        
        # [sg.Multiline(default_text="在该文本框下显示策略盈亏图表", size=(200, 14))],
        [sg.Canvas(key='-CANVAS-')],

        [sg.Text('_' * 250)],

        [sg.Submit(tooltip='Click to submit this form', size= (20, 1)), sg.Cancel(size= (20, 1)), sg.Cancel(size= (20, 1)), sg.Button('Plot')]]

    window = sg.Window("套利策略", layout, finalize=True, default_element_size=(40, 1), grab_anywhere=False)

    fig_canvas_agg = drawFigure(window['-CANVAS-'].TKCanvas, fig)

    while True:
        events, values = window.Read(timeout= 0)
        print(events[0])
        if events == sg.WIN_CLOSED or events == "Cancel":
            break
        elif events == 'Plot':
            drawPlot()

        window.Element("期货账号1").Update(data.loc[0, "期货账号"])
        window.Element("价差自动").Update(data.loc[0, "价差自动"])
        window.Element("策略编号").Update(data.loc[0, "策略编号"])
        window.Element("合约代码").Update(data.loc[0, "合约代码"])
        window.Element("策略开关").Update(data.loc[0, "策略开关"])
        window.Element("信号开关").Update(data.loc[0, "信号开关"])

        window.Element("分配资金").Update(data.loc[0, "分配资金"])
        window.Element("持仓资金").Update(data.loc[0, "持仓资金"])
        window.Element("分配仓位").Update(data.loc[0, "分配仓位"])
        window.Element("总持仓").Update(data.loc[0, "总持仓"])
        window.Element("买持仓").Update(data.loc[0, "买持仓"])
        window.Element("卖持仓").Update(data.loc[0, "卖持仓"])
        window.Element("买价").Update(data.loc[0, "买价"])
        window.Element("卖价").Update(data.loc[0, "卖价"])

        window.Element("持仓盈亏").Update(data.loc[0, "持仓盈亏"])
        window.Element("平仓盈亏").Update(data.loc[0, "平仓盈亏"])
        window.Element("手续费").Update(data.loc[0, "手续费"])
        window.Element("净盈亏").Update(data.loc[0, "手续费"])
        window.Element("A成交率").Update(data.loc[0, "A成交率"])
        window.Element("B成交率").Update(data.loc[0, "B成交率"])
        window.Element("A撤单统计").Update(data.loc[0, "撤单统计"])
        window.Element("B撤单限制").Update(data.loc[0, "撤单限制"])
        window.Element("超价触发").Update(data.loc[0, "超价触发"])

        window.Element("A时效").Update(data.loc[0, "A时效"])
        window.Element("AFAK次数").Update(data.loc[0, "AFAK次数"])
        window.Element("成交量").Update(data.loc[0, "成交量"])
        window.Element("成交总额").Update(data.loc[0, "成交总额"])
        window.Element("BFAK次数").Update(data.loc[0, "BFAK次数"])


gui_func()
