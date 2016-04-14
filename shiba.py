import wx
import threading
import time
import doge

class OrderBookList(wx.ListCtrl):
    exitFlag = False
    api = doge.HitBTC()
    data = []
    numEntries = 20
    columns=['Bid', 'BidQty', 'AskQty', 'Ask']

    def __init__(self, parent, id, size):
        wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_HRULES | wx.LC_VRULES | wx.LC_VIRTUAL, size=desiredSize)

        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.SetFont(font)

        for i in xrange(0, len(columns)):
            self.InsertColumn(i, columns[i])
            self.SetColumnWidth(i, 100)

        for i in xrange(0, self.numEntries):
            self.data.append(['', '', '', ''])

        self.SetItemCount(self.numEntries)

        self.UpdateTimer()

    def OnGetItemText(self, item, column):
        return self.data[item][column]

    def SetExitFlag(self, value):
        self.exitFlag = value

    def WaitForExit(self):
        while self.exitFlag is True:
            time.sleep(0.1)

    def UpdateTimer(self):
        orderbook = self.api.get_order_books()['BTCUSD']
        bids = orderbook['bids']
        asks = orderbook['asks']

        for i in xrange(0, self.numEntries):
            bid = bids[i]
            ask = asks[i]
            self.data[i] = [bid[0], bid[1], ask[1], ask[0]]

        self.RefreshItems(0, self.numEntries)

        if self.exitFlag:
            self.exitFlag = False
        else:
            threading.Timer(10, self.UpdateTimer).start()


class MyFrame(wx.Frame):
    def __init__(self, parent, id ,size):
        wx.Frame.__init__(self, parent, id, size=desiredSize, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.book = OrderBookList(self, 0, size)
        sizer.Add(self.book, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.book.SetExitFlag(True)
        self.book.WaitForExit()
        event.Skip()

if __name__ == '__main__':
    ''' Simple main program to display this panel. '''
    # Create a simple wxFrame to insert the panel into
    desiredSize = wx.Size(400,515)
    app = wx.PySimpleApp()
    frame = MyFrame(None, -1, size=desiredSize)    
    frame.Show()
    app.MainLoop()
