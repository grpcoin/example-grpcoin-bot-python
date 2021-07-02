import sys
import os
import grpc
import contextlib

from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from grpcoin_pb2 import *
from grpcoin_pb2_grpc import *


PROD = 'api.grpco.in:443'
LOCAL = 'localhost:8080'

ACTION = ['BUY', 'SELL']


def main():

    # Retrive the access token
    token = os.environ['TOKEN']
    if not token:
        print('''Create a permissionless Personal Access Token on GitHub 
                https://github.com/settings/tokens and set it to TOKEN environment variable''')
        sys.exit(1)

    if 'LOCAL' not in os.environ:
        metadata = (('authorization', 'Bearer ' + token),)
        chan = grpc.secure_channel(
            target=PROD, credentials=grpc.ssl_channel_credentials())
    else:
        chan = grpc.insecure_channel(LOCAL)

    # Authenticate with Github personal access token
    acc = AccountStub(chan)
    try:
        res = acc.TestAuth(request=TestAuthRequest(),
                           metadata=metadata)
        print('Logged in, User Id: %s' % res.user_id)
    except grpc.RpcError as rpc_error:
        print(rpc_error.details())
        sys.exit(1)

    # Retrive the portfolio
    pt = PaperTradeStub(chan)
    portfolio = pt.Portfolio(PortfolioRequest(), metadata=metadata)

    # Print the portfolio
    print('---------------')
    print('CASH: %d.%d' %
          (portfolio.cash_usd.units, portfolio.cash_usd.nanos))

    for pos in portfolio.positions:
        print('%s:  %d.%d' % (pos.currency.symbol,
                              pos.amount.units, pos.amount.nanos))
    print('---------------')

    # List supported currencies
    res = pt.ListSupportedCurrencies(
        ListSupportedCurrenciesRequest(), metadata=metadata)

    # Buy 2.5 ETH
    req = TradeRequest(action=BUY,
                       currency=Currency(symbol='ETH'),
                       quantity=Amount(units=2, nanos=500000000))

    order = pt.Trade(req, metadata=metadata)
    order = (ACTION[order.action-1],
             order.quantity,
             order.currency.symbol,
             order.executed_price,
             order.resulting_portfolio.remaining_cash)
    print('ORDER EXECUTED: %s [%s] %s at USD[%s] (cash remaining: %s)' % order)

    # Get real-time ticker info for BTC
    ti = TickerInfoStub(chan)
    stream = ti.Watch(TickerWatchRequest(currency=Currency(symbol="BTC")))
    for msg in stream:
        dt = datetime.fromtimestamp(msg.t.seconds).strftime('%Y-%m-%d %H:%M:%S')
        ts = dt + '.' + str(msg.t.nanos)[:3]
        info = (ts, msg.price.units, msg.price.nanos,)
        print('[server:%s] --  %d.%d' % info)


if __name__ == '__main__':
    main()
