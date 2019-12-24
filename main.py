import numpy as np
import os
import io
import cv2
import wx

class MainFrame(wx.Frame):
    def __init__(self, parent, title, size=(640, 480), fps=30):
        wx.Frame.__init__(self, parent, id=-1, title=title)

        # sizers
        # mainSizer = wx.BoxSizer(wx.VERTICAL)

        # visual elements
        self.SetSize(size[0] * 2, size[1] * 1.2)
        self.SetBackgroundColour('white')

        # components in GUI
        self.streamWrapper = StreamWrapper(parent=self, id=-1, pos=(0,0), size=size, fps=fps)
        self.ctrlPanel = wx.Panel(self, -1, pos=(size[0] * .9, size[1]), size=(size[0] * .2, size[0] * .1))
        saveButton = wx.Button(self.ctrlPanel, label="Save Image")

        # bindings
        self.Bind(wx.EVT_BUTTON, self.onSaveImages, saveButton)

        self.Show()

    def onSaveImages(self, evt):
        images = self.streamWrapper.getImage()
        cwd = os.getcwd()

        try:
            # output = open(cwd, 'w')
            # output.write(images[0])
            images[0].SaveFile("raw_image.jpg", wx.BITMAP_TYPE_JPEG)
            images[1].SaveFile("filtered_image.jpg", wx.BITMAP_TYPE_JPEG)
        except IOError:
            wx.LogError("Cannot save current data in file '%s'." % cwd)

class StreamWrapper(wx.Panel):
    def __init__(self, parent, size, id=-1, pos=(0,0), fps=30):
        wx.Panel.__init__(self, parent=parent, id=id, pos=pos)

        self.SetBackgroundColour('white')

        # webcam stream stuff
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])

        ret, frame = self.capture.read()

        height, width = frame.shape[:2]
        size = (width, height)

        self.SetSize(width * 2, height)

        filtered = self.edgeDetection(frame)

        self.rawStream = StreamPanel(parent=self, id=-1, pos=pos, size=size, frame=frame)
        self.filteredStream = StreamPanel(parent=self, id=-1, pos=(pos[0] + width, pos[1]), size=size, frame=filtered)
        self.refreshTimer = wx.Timer(self)
        self.refreshTimer.Start(1000./fps)

        self.Bind(wx.EVT_TIMER, self.onNextFrame, self.refreshTimer)

    def onNextFrame(self, evt):
        ret, frame = self.capture.read()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.rawStream.bitmap.CopyFromBuffer(frame)

            filtered = self.edgeDetection(frame)
            self.filteredStream.bitmap.CopyFromBuffer(filtered)
            self.Refresh()

    def edgeDetection(self, frame, sigma=0.33):
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        med = np.median(grey)
        lower = int(max(0, (1.0 - sigma) * med))
        upper = int(min(255, (1.0 + sigma) * med))
        edges = cv2.Canny(grey, lower, upper)

        filtered = np.stack((edges, ) * 3, axis=-1)
        return filtered

    def getImage(self):
        return self.rawStream.getImage(), self.filteredStream.getImage()

class StreamPanel(wx.Panel):
    def __init__(self, parent, id, pos, size, frame):
        wx.Panel.__init__(self, parent=parent, id=id, pos=pos, size=size)
        self.SetDoubleBuffered(True)

        self.posX, self.posY = pos
        width, height = size
        # self.SetSize(width, height)

        self.bitmap = wx.Bitmap.FromBuffer(width, height, frame)

        self.Bind(wx.EVT_PAINT, self.getRegionInfo)
        self.Bind(wx.EVT_PAINT, self.paintRegion)

    def getRegionInfo(self, evt):
        upd = wx.RegionIterator(self.GetUpdateRegion())
        print('pos: {}, {}'.format(upd.GetX(), upd.GetY()))
        print('size: {}, {}'.format(upd.GetWidth(), upd.GetHeight()))

    def paintRegion(self, evt):
        if self.bitmap:
            dc = wx.BufferedPaintDC(self)
            dc.DrawBitmap(self.bitmap, 0, 0)

    def getImage(self):
        return self.bitmap.ConvertToImage()

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, title='Filter GUI')
    app.MainLoop()
