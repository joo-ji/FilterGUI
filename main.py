import numpy as np
import cv2
import wx

class StreamPanel(wx.Panel):

    def __init__(self, parent, fps=30):
        wx.Panel.__init__(self, parent, -1)

        self.capture = cv2.VideoCapture(0)
        ret, frame = self.capture.read()
        height, width = frame.shape[:2]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        self.SetSize(width, height)
        self.displayPanel = wx.Panel(self, -1)

        self.bmp = wx.Bitmap.FromBuffer(width, height, frame)
        self.Bind(wx.EVT_PAINT, self.onPaint)

        self.timer = wx.Timer(self)
        self.timer.Start(1000/fps)

        self.Show()

    def onPaint(self, evt):
        if self.bmp:
            dc = wx.BufferedPaintDC(self.displayPanel, self.bmp)

        evt.Skip()
        
    def onNextFrame(self, evt):
        ret, frame = self.capture.read()
        
        if ret:
            frame = cv2.cvtColor(frame, cv2.color_BGR2RGB)
            self.bmp.CopyFromBuffer(frame)
            self.Refresh()

app = wx.App()
frame = wx.Frame(None)
panel = StreamPanel(frame)
frame.Show()
app.MainLoop()
