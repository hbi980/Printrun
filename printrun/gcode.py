import wx
from collections import namedtuple
from math import sin,cos,asin,radians,degrees

LinesInput = namedtuple('Lines',['start','end','offset','FE','count','layer'])

linesInput = LinesInput(
         {'name':u"     第一条线起点",'value':complex(20,10)},
         {'name':u"     第一条线终点",'value':complex(10,50)},
         {'name':u"   最后一条线起点",'value':complex(50,15)},
         {'name':u"F(速度)/E(挤出量)",'value':complex(1800,22.4)},
         {'name':u"         打印线数",'value':5},
         {'name':u"         打印层数",'value':3},
         )

ArcsInput = namedtuple('Arcs',['center','radius','start_end','step','FE','count','layer'])
arcsInput = ArcsInput(
         {'name':u"    圆心(X/Y坐标)",'value':complex(45,35)},
         {'name':u"最大半径/最小半径",'value':complex(26.7,8)},
         {'name':u"起始角度/终止角度",'value':complex(-76.0,104)},
         {'name':u"   圆弧精度(长度)",'value':1},
         {'name':u"F(速度)/E(挤出量)",'value':complex(1800,22.4)},
         {'name':u"             线数",'value':3},
         {'name':u"             层数",'value':3},
         )

class Lines:
  @staticmethod  
  def GetLines(input):
    '''生成多线数据'''
    lines = []
    #offsetEnd = input.offset['value'] * (input.end['value'] / input.start['value'])
    offset = (input.offset['value'] - input.start['value']) / (input.count['value'] - 1)
    #offset = (offsetEnd - input.start['value']) / input.count['value']
    for i in range(input.count['value']):
      #起点
      start = input.start['value'] + offset * i
      #终点
      end = input.end['value'] + offset * i

      #每两次起点与终点翻转，打印走最短距离
      if i % 2 == 0:
        lines.append((start, end))
      else:
        lines.append((end, start))
      
    return lines
  
  @staticmethod  
  def GetCode1(lines,layer,FE):
    code = ''
    e = 0
    #按层数打印
    for l in range(layer):
      code += ';LAYER:%d\n' % l
      #e = 0

      #打印每层
      for line in lines:
        e += FE.imag
        #起点
        code += 'G0 F9000 X%.2f Y%.2f E0\r\n' % (line[0].real,line[0].imag)
        #划线
        code += 'G1 F%.2f X%.2f Y%.2f E%.2f\r\n' % (FE.real,line[1].real,line[1].imag,e)
    return code

  @staticmethod  
  def GetCode(input):
    return Lines.GetCode1(Lines.GetLines(input),input.layer['value'],input.FE['value'])


class Arcs:
  @staticmethod  
  def GetArcs(input):
    '''生成圆弧代码'''
    code = ''

    center = input.center['value'] #圆心
    start = min(input.start_end['value'].real,input.start_end['value'].imag)#最小角度
    end = max(input.start_end['value'].real,input.start_end['value'].imag)#最大角度
    minradius = min(input.radius['value'].real,input.radius['value'].imag) #最小半径
    maxradius = max(input.radius['value'].real,input.radius['value'].imag) #最大半径

    #从里向外依次画圆弧
    for arc in range(0,input.count['value']):
      radius = minradius + (maxradius - minradius) / input.count['value'] * arc #本次半径      
      
      #定位到起点
      x = center.real + radius * cos(radians(start))
      y = center.imag + radius * sin(radians(start))
      code += 'G0  F9000 X%.2f Y%.2f E0\r\n' % (x,y)

      anstep = degrees(asin((input.step['value'] / 2.0) / radius)) * 2.0 #把圆弧精度（长度）转换为角度

      #画小圆弧组成完整圆弧
      angle = start #起始角度
      for astep in range(1,int((end - start) / anstep)):
        angle = radians(start + astep * anstep) #小圆弧终点角度
        x = center.real + radius * cos(angle)
        y = center.imag + radius * sin(angle)
        code += 'G1  F%.2f X%.2f Y%.2f E%.2f\r\n' % (input.FE['value'].real,x,y,input.FE['value'].imag * astep)

      #画最后小圆弧
      if angle < end:
        x = center.real + radius * cos(radians(end))
        y = center.imag + radius * sin(radians(end))
        code += 'G1  F%.2f X%.2f Y%.2f E%.2f\r\n' % (input.FE['value'].real,x,y,input.FE['value'].imag * (astep + 1) )      

      code += '\r\n'

    return code
  
  @staticmethod  
  def GetCode1(input):
    code = Arcs.GetArcs(input)
    layer = input.layer['value']
    #按层数打印
    result = ''
    for l in range(layer):
      result += ';LAYER:%d\r\n' % (l + 1)
      result += code
            
    return result

  @staticmethod  
  def GetCode(input):
    return Arcs.GetCode1(input)


class InputWindow(wx.Dialog):
  def __init__(self, parent, title, data,Code):
    wx.Dialog.__init__(self, parent, title=title, size=(400, 450))
    self.data = data
    self.Code = Code
    self.InitUI()  
    self.ShowModal()

  def InitUI(self):  
    panel = wx.Panel(self)  
          
    vbox = wx.BoxSizer(wx.VERTICAL)
    #增加输入框
    for it in self.data:      
      hbox1 = wx.BoxSizer(wx.HORIZONTAL)
      st1 = wx.StaticText(panel,label=it['name'])
      hbox1.Add(st1,flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,border=12)
      if type(it['value']) == complex:
        tc1 = wx.TextCtrl(panel,value = str(it['value'].real))
        hbox1.Add(tc1,proportion=1)      
        tc2 = wx.TextCtrl(panel,value = str(it['value'].imag))
        hbox1.Add(tc2,proportion=1)
        it['ctrl'] = (tc1,tc2)
      else:
        tc = wx.TextCtrl(panel,value = str(it['value']))
        hbox1.Add(tc,proportion=1)  
        it['ctrl'] = tc

      vbox.Add(hbox1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP | wx.ALIGN_CENTER_VERTICAL,border=10)
      vbox.Add((-1,10))
          
    #增加代码框    
    hbox3 = wx.BoxSizer(wx.HORIZONTAL)  
    self.txtCode = wx.TextCtrl(panel, style=wx.TE_MULTILINE, value = u'显示Gcode')
    hbox3.Add(self.txtCode, proportion=1, flag=wx.EXPAND)  
    vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND,border=10)    
    vbox.Add((-1, 25))  
  
    #增加按钮栏
    hbox5 = wx.BoxSizer(wx.HORIZONTAL) 
    btnCode = wx.Button(panel, label=u'代码', size=(70, 30))  
    hbox5.Add(btnCode)       
    btnOk = wx.Button(panel, label=u'确认', size=(70, 30))  
    hbox5.Add(btnOk, flag=wx.LEFT|wx.BOTTOM, border=5)  
    btnClose = wx.Button(panel, label=u'关闭', size=(70, 30))  
    hbox5.Add(btnClose, flag=wx.LEFT|wx.BOTTOM, border=5)  
    vbox.Add(hbox5, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10) 

    #绑定事件
    self.Bind(wx.EVT_BUTTON, self.OnCode, btnCode)
    self.Bind(wx.EVT_BUTTON, self.OnOk, btnOk)
    self.Bind(wx.EVT_BUTTON, self.OnClose, btnClose)
          
    panel.SetSizer(vbox)

  def getGCode(self):
    for it in self.data:
      if type(it['value']) == complex:
        it['value'] = complex(float(it['ctrl'][0].GetValue()),float(it['ctrl'][1].GetValue()))
      else:
        it['value'] = int(it['ctrl'].GetValue())  
    
    #生成多线数据
    #self.gcode = Lines.GetCode(self.data)
    self.gcode = self.Code.GetCode(self.data)
    return self.gcode

  #生成代码
  def OnCode(self, event):  
    self.txtCode.SetValue(self.getGCode())
              

  def OnOk(self, event): 
    self.getGCode()
    self.Destroy()



  def OnClose(self,event):
    self.gcode = ''
    self.Destroy()

def LinesCode():
    dialog = InputWindow(None, u'画直线', linesInput,Lines)
    return dialog.gcode.splitlines()



def ArcsCode():
    dialog = InputWindow(None, u'画弧线',arcsInput,Arcs)
    return dialog.gcode.splitlines()



class InputCount(wx.Dialog):
  def __init__(self, parent, title):
    wx.Dialog.__init__(self, parent, title=title, size=(200, 100))
    self.InitUI()  
    self.ShowModal()

  def InitUI(self):  
    panel = wx.Panel(self)  
          
    vbox = wx.BoxSizer(wx.VERTICAL)
    #增加输入框
    hbox1 = wx.BoxSizer(wx.HORIZONTAL)
    st1 = wx.StaticText(panel,label=u'次数')
    hbox1.Add(st1,flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,border=12)
    tc = wx.TextCtrl(panel,value = '1')
    hbox1.Add(tc,proportion=1)  
    self.tc = tc

    vbox.Add(hbox1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP | wx.ALIGN_CENTER_VERTICAL,border=10)
    vbox.Add((-1,10))
  
    #增加按钮栏
    hbox5 = wx.BoxSizer(wx.HORIZONTAL) 
    btnOk = wx.Button(panel, label=u'确认', size=(70, 30))  
    hbox5.Add(btnOk, flag=wx.LEFT|wx.BOTTOM, border=5)  
    btnClose = wx.Button(panel, label=u'关闭', size=(70, 30))  
    hbox5.Add(btnClose, flag=wx.LEFT|wx.BOTTOM, border=5)  
    vbox.Add(hbox5, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10) 

    #绑定事件
    self.Bind(wx.EVT_BUTTON, self.OnOk, btnOk)
    self.Bind(wx.EVT_BUTTON, self.OnClose, btnClose)
          
    panel.SetSizer(vbox)

  def getGCode(self):
    for it in self.data:
      if type(it['value']) == complex:
        it['value'] = complex(float(it['ctrl'][0].GetValue()),float(it['ctrl'][1].GetValue()))
      else:
        it['value'] = int(it['ctrl'].GetValue())  
    
    #生成多线数据
    #self.gcode = Lines.GetCode(self.data)
    self.gcode = self.Code.GetCode(self.data)
    return self.gcode
              

  def OnOk(self, event): 
    self.count = int(self.tc.GetValue())
    self.Destroy()



  def OnClose(self,event):
    self.count = 0
    self.Destroy()

def CodeCount():
    dialog = InputCount(None, u'输入次数')
    return dialog.count


class MainWindow(wx.Frame):
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title, size=(300, 300))
    panel = wx.Panel(self, -1)
    self.button = wx.Button(panel, -1, u"按钮", pos=(50, 20))
    self.Bind(wx.EVT_BUTTON, self.OnClick, self.button) 
    
    self.Show(True)

  def OnClick(self, event):  
      dialog = InputWindow(None, 'Small Editor',linesInput,0)
        #self.button.SetLabel("Clicked")  

if __name__ == '__main__':
  app = wx.App(False)
  frame = MainWindow(None, 'Small Editor')
  app.MainLoop() 