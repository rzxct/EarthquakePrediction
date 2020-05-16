from tkinter import Tk, Frame, Label, Button, Entry, LEFT, RIGHT, TOP, DoubleVar, StringVar
from tkinter.ttk import Combobox
from tkinter.messagebox import showinfo
from datetime import datetime
from 地震分区 import 地震分区
from 地震预报库 import SB

def 生成输入窗口(父窗口, 地震分区):
    范围 = {'南': DoubleVar(), '北': DoubleVar(), '西': DoubleVar(), '东': DoubleVar()}
    def 设置经纬度(*args):
        范围['南'].set(地震分区[cb.get()][0])
        范围['北'].set(地震分区[cb.get()][1])
        范围['西'].set(地震分区[cb.get()][2])
        范围['东'].set(地震分区[cb.get()][3])       
    frame = Frame(父窗口)
    frame.pack(side=TOP)
    Label(frame, text='地震分区:').pack(side=LEFT)
    cb = Combobox(frame, values=list(地震分区.keys()))
    cb.pack(side=LEFT)
    cb.bind('<<ComboboxSelected>>', 设置经纬度)
    for key, value in 范围.items():
        frame = Frame(父窗口)
        frame.pack(side=TOP)
        Label(frame, text=key).pack(side=LEFT)
        Entry(frame, textvariable=value).pack(side=RIGHT)
    Button(父窗口, text='确定', command=lambda: 运算(范围)).pack(side=RIGHT)


def 运算(范围):  
    中位数震级 = SB([范围['南'].get(),范围['北'].get(),范围['西'].get(),范围['东'].get()], 表名="华北")
    showinfo(title='预报结论', message= ('%3.1f - %3.1f' % (中位数震级-0.5, 中位数震级+0.5)))


if __name__ == '__main__':     
    win = Tk()
    win.title("地震预报4中学生")
    win.geometry("270x150")
    生成输入窗口(win, 地震分区)
    win.mainloop()
