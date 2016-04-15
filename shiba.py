import wx
import threading
import time
import doge
import sys

API = None

class OrderBookList(wx.ListCtrl):
    _NUM_ENTRIES = 20
    _COLUMN_LABELS = ['Bid', 'BidQty', 'AskQty', 'Ask']

    def __init__(self, parent, id, size, symbol):
        wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_HRULES | wx.LC_VRULES | wx.LC_VIRTUAL, size=desiredSize)

        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.SetFont(font)

        for i in xrange(0, len(self._COLUMN_LABELS)):
            self.InsertColumn(i, self._COLUMN_LABELS[i])
            self.SetColumnWidth(i, 149)

        self.data = []
        for i in xrange(0, self._NUM_ENTRIES):
            self.data.append(['', '', '', ''])

        self.SetItemCount(self._NUM_ENTRIES)
        self.SetExitFlag(False)

        self.currentSymbol = symbol

        self.UpdateTimer()

    def OnGetItemText(self, item, column):
        return self.data[item][column]

    def SetExitFlag(self, value):
        self.exitFlag = value

    def WaitForExit(self):
        while self.exitFlag:
            time.sleep(0.1)

    def UpdateTimer(self):
        orderbook = API.get_order_book(self.currentSymbol)
        bids = orderbook['bids']
        asks = orderbook['asks']

        for i in xrange(0, self._NUM_ENTRIES):
            bid = bids[i]
            ask = asks[i]
            self.data[i] = [bid[0], bid[1], ask[1], ask[0]]

        self.RefreshItems(0, self._NUM_ENTRIES)

        if self.exitFlag:
            self.exitFlag = False
        else:
            threading.Timer(5, self.UpdateTimer).start()

    def setSymbol(self, value):
        self.SetExitFlag(True)
        self.WaitForExit()
        self.currentSymbol = value
        self.UpdateTimer()

class OrderEntry(wx.BoxSizer):
    def __init__(self, parent, id, size, symbol):
        wx.BoxSizer.__init__(self, wx.VERTICAL)

        self.buyOrder = wx.RadioButton(parent, -1, 'Buy', style=wx.RB_GROUP)
        self.sellOrder = wx.RadioButton(parent, -1, 'Sell')
        self.orderPrice = wx.TextCtrl(parent, -1, '0.0')
        self.orderSize = wx.TextCtrl(parent, -1, '0.0')
        self.limitOrder = wx.RadioButton(parent, -1, 'Limit', style=wx.RB_GROUP)
        self.marketOrder = wx.RadioButton(parent, -1, 'Market')
        parent.Bind(wx.EVT_RADIOBUTTON, self.onOrderTypeSelect)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([
            self.buyOrder,
            self.sellOrder,
            (30,5),
            wx.StaticText(parent, -1, 'Price'),
            self.orderPrice,
            (30,5),
            wx.StaticText(parent, -1, 'Size'),
            self.orderSize,
            (30,5),
            self.limitOrder,
            self.marketOrder
            ])

        sendOrderButton = wx.Button(parent, id, 'Send Order')
        parent.Bind(wx.EVT_BUTTON, self.onSendOrder)

        self.Add(sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.Add(sendOrderButton, 0, wx.ALL | wx.EXPAND, 0)

        self.currentSymbol = symbol

    def onSendOrder(self, event):
        symbol = self.currentSymbol
        buyOrSell = 'buy' if self.buyOrder.GetValue() else 'sell' if self.sellOrder.GetValue else ''
        price = self.orderPrice.GetLineText(0)
        size = self.orderSize.GetLineText(0)

        order =  API.send_new_order(symbol, buyOrSell, price, size)
        print order.body

    def onOrderTypeSelect(self, event):
        if self.marketOrder.GetValue():
            self.orderPrice.SetEditable(False)
            self.orderPrice.SetValue('')
        else:
            self.orderPrice.SetEditable(True)
            self.orderPrice.SetValue('0.0')

    def setSymbol(self, value):
        self.currentSymbol = value


class MyFrame(wx.Frame):
    def __init__(self, parent, id ,size):
        wx.Frame.__init__(self, parent, id, size=desiredSize, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        self.symbolList = API.get_symbols()

        self.symbolSelection = wx.ComboBox(self, 0, value = self.symbolList[0], choices = self.symbolList, style=wx.CB_READONLY)
        self.orderBook = OrderBookList(self, 0, size, self.symbolList[0])
        self.orderEntry = OrderEntry(self, 0, size, self.symbolList[0])

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.symbolSelection, 0, wx.ALL | wx.EXPAND, 0)
        self.sizer.Add(self.orderBook, 0, wx.ALL | wx.EXPAND, 0)
        self.sizer.Add(self.orderEntry, 0, wx.ALL | wx.EXPAND, 0)

        self.SetSizerAndFit(self.sizer)

        self.Layout()
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_COMBOBOX, self.onSelect)

    def onClose(self, event):
        self.orderBook.SetExitFlag(True)
        self.orderBook.WaitForExit()
        event.Skip()

    def onSelect(self, event):
        self.orderBook.setSymbol(self.symbolList[event.GetSelection()])
        self.orderEntry.setSymbol(self.symbolList[event.GetSelection()])


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
    desiredSize = wx.Size(600, 515)
    app = wx.PySimpleApp()
    frame = MyFrame(None, -1, size=desiredSize)    
    frame.Show()
    app.MainLoop()
