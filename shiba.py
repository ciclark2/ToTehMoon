import wx
import threading
import time
import doge
import sys

API = None

class OrderBookList(wx.ListCtrl):
    exitFlag = False
    data = []
    numEntries = 20
    columns=['Bid', 'BidQty', 'AskQty', 'Ask']

    def __init__(self, parent, id, size):
        wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_HRULES | wx.LC_VRULES | wx.LC_VIRTUAL, size=desiredSize)

        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.SetFont(font)

        for i in xrange(0, len(self.columns)):
            self.InsertColumn(i, self.columns[i])
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
        orderbook = API.get_order_book('BTCUSD')
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

        self.orderBook = OrderBookList(self, 0, size)

        self.buyOrder = wx.RadioButton(self, -1, 'Buy', style=wx.RB_GROUP)
        self.sellOrder = wx.RadioButton(self, -1, 'Sell')
        buySellSizer = wx.BoxSizer(wx.HORIZONTAL)
        buySellSizer.Add(self.buyOrder, 0, wx.ALL | wx.EXPAND, 0)
        buySellSizer.Add((30, 5), 0, 0, 0)
        buySellSizer.Add(self.sellOrder, 0, wx.ALL | wx.EXPAND, 0)

        self.orderPrice = wx.TextCtrl(self, -1, '0.0')
        self.orderSize = wx.TextCtrl(self, -1, '0.0')
        priceSizeSizer = wx.BoxSizer(wx.HORIZONTAL)
        priceSizeSizer.Add(wx.StaticText(self, -1, 'Price'), 0, 0, 0)
        priceSizeSizer.Add((30,5), 0, 0, 0)
        priceSizeSizer.Add(self.orderPrice, 0, wx.ALL | wx.EXPAND, 0)
        priceSizeSizer.Add((30,5), 0, 0, 0)
        priceSizeSizer.Add(wx.StaticText(self, -1, 'Size'), 0, 0, 0)
        priceSizeSizer.Add((30, 5), 0, 0, 0)
        priceSizeSizer.Add(self.orderSize, 0, wx.ALL | wx.EXPAND, 0)

        self.sendOrderButton = wx.Button(self, id, 'Send Order')
        self.sendOrderButton.Bind(wx.EVT_BUTTON, self.onSendOrder)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.orderBook, 0, wx.ALL | wx.EXPAND, 0)
        self.sizer.Add(buySellSizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.sizer.Add(priceSizeSizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.sizer.Add(self.sendOrderButton, 0, wx.ALL | wx.EXPAND, 0)

        self.SetSizerAndFit(self.sizer)

        self.Layout()
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.orderBook.SetExitFlag(True)
        self.orderBook.WaitForExit()
        event.Skip()

    def onSendOrder(self, event):
        order = ''
        if self.buyOrder.GetValue():
            order += 'BUY '
        elif self.sellOrder.GetValue():
            order += 'SELL '
        order += self.orderSize.GetLineText(0) + ' @ ' + self.orderPrice.GetLineText(0)
        print order
        


if __name__ == '__main__':
    ''' Simple main program to display this panel. '''
	
    # Parse cmdline args
    if len(sys.argv) != 3:
        print 'Program arguments should be: <api key> <api secret>'
        sys.exit(1)

    # Instantiate our api
    _, api_key, api_secret = sys.argv
    API = doge.HitBTC(api_key, api_secret)


    # Create a simple wxFrame to insert the panel into
    desiredSize = wx.Size(400, 515)
    app = wx.PySimpleApp()
    frame = MyFrame(None, -1, size=desiredSize)    
    frame.Show()
    app.MainLoop()
