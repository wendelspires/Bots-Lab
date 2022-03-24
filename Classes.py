

#----------------------------------------------------------------------
#------------------------------Classes---------------------------------
#----------------------------------------------------------------------

class API_KEY:
    
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key


    def get_headers(self):

        headers = {
            'Content-Type': 'application/json',
            'X-MBX-APIKEY': '{}'.format(self.api_key)
            }

        return headers

#Class Orders
class Orders:

    def __init__(self):
        self.order = None #Buy, Sell, Close
        self.order_type = None #Market, Limit, start, stop
        self.move_order = None #If a limit, what the price?
        self.entry_time = None #Time 
        self.entry_price = None # Price
        self.volume = None #Volume
        self.tp = None #Take profit
        self.sl = None #Stop Loss

    #GETTERS
    @property
    def Order(self):
        return self.__order
    
    @property
    def OrderType(self):
        return self.__order_type

    @property
    def MoveOrder(self):
        return self.__move_order
    
    @property
    def EntryTime(self):
        return self.__entry_time

    @property
    def EntryPrice(self):
        return self.__entry_price

    @property
    def Volume(self):
        return self.__volume

    @property
    def TakeProfit(self):
        return self.__tp

    @property
    def StopLoss(self):
        return self.__sl


    #SETTERS
    @Order.setter
    def Order(self,string):
        self.__order = string
        
    @OrderType.setter
    def OrderType(self,string):
        self.__order_type = string

    @MoveOrder.setter
    def MoveOrder(self,move_order_value):
        self.__move_order = move_order_value

    @EntryTime.setter
    def EntryTime(self,date):
        self.__entry_time = date

    @EntryPrice.setter
    def EntryPrice(self,price):
        self.__entry_price = price

    @Volume.setter
    def Volume(self,volume_value):
        self.__volume = volume_value

    @TakeProfit.setter
    def TakeProfit(self,tp_value):
        self.__tp = tp_value

    @StopLoss.setter
    def StopLoss(self,sl_value):
        self.__sl = sl_value

class Position:

    def __init__(self):

        self.__long_position = False
        self.__short_position = False
        self.__long_pending_order = False
        self.__short_pending_order = False

    #Getters
    @property
    def LongOpened(self):
        return self.__long_position

    @property
    def LongOnly(self):
        return self.__long_only

    @property
    def ShortOpened(self):
        return self.__short_position

    @property
    def ShortOnly(self):
        return self.__short_only

    @property
    def LongPedingOrder(self):
        return self.__long_pending_order

    @property
    def ShortPedingOrder(self):
        return self.__short_pending_order

    @property
    def ReversalPosition(self):
        return self.__reversal_position

    @property
    def InversePosition(self):
        return self.__inverse_position

    #Setters
    @LongOpened.setter
    def LongOpened(self,boolean_value):
        self.__long_position = boolean_value

    @LongOnly.setter
    def LongOnly(self,boolean_value):
        self.__long_only = boolean_value

    @ShortOpened.setter
    def ShortOpened(self,boolean_value):
        self.__short_position = boolean_value

    @ShortOnly.setter
    def LongOnly(self,boolean_value):
        self.__short_only = boolean_value

    @LongPedingOrder.setter
    def LongPedingOrder(self,boolean_value):
        self.__long_pending_order = boolean_value

    @ShortPedingOrder.setter
    def ShortPedingOrder(self,boolean_value):
        self.__short_pending_order = boolean_value

    @ReversalPosition.setter
    def ReversalPosition(self,boolean_value):
        self.__reversal_position = boolean_value

    @InversePosition.setter
    def InversePosition(self,boolean_value):
        self.__inverse_position = boolean_value

