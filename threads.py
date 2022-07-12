import csv
import time
import threading
import pandas as pd
import PySimpleGUI as sg

def createDate():
    f = open('argin.csv','w', newline='')
    csvWrite = csv.writer(f)
    csvWrite.writerow(["time","profit"])
    for i in range(100):
        list.append(i)
        print("输入的值为:%d"%list[i])
        csvWrite.writerow(str(list[i]))
        f.flush()
        # await asyncio.sleep(1)
        time.sleep(4)

def readDate():
    l = None
    l2 = 0
    while True:
        time.sleep(4)
        data2 = pd.read_csv('argin.csv')
        l = len(data2)
        if l2 > l:
            time.sleep(1)
            continue
        # for i in range(l2, l):
        a = int(data2.iloc[-1, 0])
        print("读取的值为：%d" % a)
        l2 = l + 1

list = []
def a():
    while True:
        print(list)
        time.sleep(4)

def Gui():
    layout = [[sg.Text("init1",key= "分配仓位", size=(7,1))],
            [sg.Text("init2",key= "分配资金", size=(7,1))]],
            
    window = sg.Window('PySimpleGUI', layout)
    print("暂停")
    time.sleep(2)
    print("暂停2")
    while True:
        print(888,list)
        event, values = window.read()
        window.refresh()
        print(values[0])

        # window.Element("分配仓位").update(temp[-1])

t1 = threading.Thread(target=createDate, name='thread1')
t2 = threading.Thread(target=readDate, name='thread2')
t3 = threading.Thread(target=Gui, name='thread3')
# t4 = threading.Thread(target=a, name='thread4')
t1.start()
t2.start()
t3.start()
# t4.start()
a()
