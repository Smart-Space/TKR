import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename,asksaveasfilename
import re
from PIL import Image,ImageTk,Image,ImageGrab
import ctypes

tkr_ver=1

class Text2PDF:
    '''将tkinter文本组件内容从图片转为pdf'''

    def __init__(self,text_widget,master):
        #text_widget::tkinter的文本框组件
        #master::tkinter文本框所在的窗口
        self.text=text_widget
        self.master=master
        self.retop=self.master.attributes('-topmost')
        self.textstyle=self.text['relief']

    def pdf(self,pdfname='textpdf',path=''):
        #pdfname::pdf文件名称
        #path::生成的pdf路径，默认当前目录
        self.text.yview('moveto',0.0)
        self.text.update()
        _,ys,_,ye=self.text.bbox(1.0)
        chh=ye-ys#获取单字符高度
        startx=self.text.winfo_rootx()
        starty=self.text.winfo_rooty()
        width=self.text.winfo_width()
        height=self.text.winfo_height()
        #填充最后一页字符
        num=height//chh+1
        self.text.insert('end','\n'*num)
        #开始截屏
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        endx=startx+width
        endy=starty+height
        self.master.attributes('-topmost',1)
        self.text['relief']='flat'
        imgs=[]
        all_height=0
        while True:
            img=ImageGrab.grab((startx,starty,endx,endy))
            imgs.append(img)
            if self.text.yview()[1]>=1:
                break
            self.text.yview("scroll",height,'pixels')
            self.text.update()
            all_height+=height
        pdfimg=Image.new('RGB',(width,all_height),255)
        x=y=0#拼接起始点
        for img in imgs:
            pdfimg.paste(img,(x,y))
            y+=height
        pdfimg.save(path+pdfname+'.pdf',resolution=100.0)
        self.master.attributes('-topmost',int(self.retop))
        self.text['relief']=self.textstyle


def open_file():
    _f=askopenfilename(title='打开tkr文件',filetype=[('tkinter富文本文件','*.tkr')],initialdir='G:/')
    if _f=='':
        return
    f=open(_f,mode='r',encoding='utf-8')
    tkr=f.read()
    f.close()
    render(text,tkr)

def save_as():
    _f=asksaveasfilename(title='选择tkr文件生成位置',filetype=[('tkinter富文本文件','*.tkr')])
    if _f=='':
        return
    fname=_f+'.tkr'
    text2tkr(text,fname)

def save_pdf():
    _f=asksaveasfilename(title='选择tkr文件生成位置',filetype=[('tkinter富文本文件','*.pdf')])
    if _f=='':
        return
    fname=_f+'.tkr'
    Text2PDF(text,root).pdf(fname)

#渲染部分
def render(tkrt:tk.Text,tkr:str):
    tags=re.findall( r'=tagon=\n(.*?)\n=tagoff',tkr,re.S)[0]
    #在文本框中注册每一个标记
    for i in tags.split('\n'):
        if i=='':
            continue
        tagform=re.findall(r'^(.*?) (.*)$',i)[0]
        tag_dict=eval(tagform[1])
        exec("tkrt.tag_config('"+tagform[0]+"',**tag_dict)")
    words=eval(re.findall(r'=texton=\n(.*?)\n=textoff=',tkr,re.S)[0])
    #渲染
    nowtag=[]#当前的tag样式
    for mark,u,end in words:
        if mark=='tagon':
            nowtag.append(u)
        elif mark=='tagoff':
            nowtag.remove(u)
        elif mark=='text':
            tkrt.insert(end,u,tuple(nowtag))
    return True

#解析导出
def text2tkr(tkrt:tk.Text,fname):
    def get_tag_dict(tagname):
        new_dict={}
        old_dict=tkrt.tag_config(tagname)
        for item in old_dict.keys():
            new_dict[item]=old_dict[item][4]
        return new_dict
    tkr_ver=1
    #开始格式化数据
    acon=tkrt.dump(1.0,'end',text=True,tag=True)
    tag_on='\n=tagon=\n'
    tag_name_list=[]
    #第一部分
    for i in acon:
        tag_name=i[1]
        if i[0]=='tagon' and tag_name not in tag_name_list:
            tag_name_list.append(tag_name)
            tag_dict=get_tag_dict(tag_name)
            tag_on+=tag_name+' '+str(tag_dict)+'\n'
    tag_on+='\n=tagoff=\n'
    #第二部分完成
    text_on='\n=texton=\n'+str(acon)+'\n=textoff=\n'
    with open(fname,mode='w',encoding='utf-8') as tkrf:
        tkrf.write(tag_on)
        tkrf.write(text_on)
    return True



root = tk.Tk()
root.geometry("1200x750+5+5")
root.title('TKR Reader')

menubar = tk.Menu(root,font="TkMenuFont")
root.configure(menu = menubar)

menubar.add_command(label="文件",command=open_file)
menubar.add_command(label='另存为tkr',command=save_as)
menubar.add_command(label='另存为pdf',command=save_pdf)

text = ScrolledText(root,font=('微软雅黑',13))
text.place(relx=0.15, rely=0.0, relheight=0.999, relwidth=0.687)
text.configure(background="white")
text.configure(foreground="black")
text.configure(highlightbackground="#d9d9d9")
text.configure(highlightcolor="black")
text.configure(insertbackground="black")
text.configure(selectbackground="blue")
text.configure(selectforeground="white")
text.configure(wrap="word")

root.mainloop()