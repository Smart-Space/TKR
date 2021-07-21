import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename,asksaveasfilename
import re

tkr_ver=1

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
menubar.add_command(label='另存为',command=save_as)

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