import logging
import sys
import os
import grpc
import contextlib
import tabulate

from enum import Enum
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from grpcoin_pb2 import *
from grpcoin_pb2_grpc import *

PROD = 'api.grpco.in:443'
LOCAL = 'localhost:8080'


class Action(Enum):
    UNDEFINED = 'UNDEFINED'
    BUY = 'BUY'
    SELL = 'SELL'


def format_amount(amount):
    value = amount.units + amount.nanos / 1000000000
    return value


def main():

    # Setting logger
    logger = logging.getLogger('SERVER')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('log.txt')
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s: %(levelname)s: %(name)s: %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # Retrive the access token
    token = os.environ['TOKEN']
    if not token:
        print('''Create a permissionless Personal Access Token on GitHub 
                https://github.com/settings/tokens and set it to TOKEN environment variable''')
        sys.exit(1)

    # Connect to grpcoin server
    metadata = (('authorization', 'Bearer ' + token),)
    if 'LOCAL' not in os.environ:
        chan = grpc.secure_channel(
            target=PROD, credentials=grpc.ssl_channel_credentials())
    else:
        chan = grpc.insecure_channel(LOCAL)

    # Authenticate with Github personal access token
    acc = AccountStub(chan)
    try:
        auth_user = acc.TestAuth(request=TestAuthRequest(),
                                 metadata=metadata)
        logger.info('Logged in, User Id: %s' % (auth_user.user_id))
    except grpc.RpcError as rpc_error:
        logger.error(rpc_error.details())
        sys.exit(1)

    # Retrive the portfolio
    pt = PaperTradeStub(chan)
    portfolio = pt.Portfolio(PortfolioRequest(), metadata=metadata)

    # Print the portfolio
    logger.info('Printing the portfolio...')
    header = ['ASSET', 'AMOUNT']
    assets = [["CASH", format_amount(portfolio.cash_usd)]]
    for pos in portfolio.positions:
        assets.append([pos.currency.symbol, format_amount(pos.amount)])

    print(tabulate.tabulate(assets,
                            headers=header,
                            tablefmt='psql',
                            disable_numparse=True))

    # List supported currencies
    logger.info('Listing supported currencies...')
    currency_list = pt.ListSupportedCurrencies(
        ListSupportedCurrenciesRequest(), metadata=metadata)

    tbl = [['CURRENCY']]
    for cur in currency_list.supported_currencies:
        tbl.append(['+ ' + cur.symbol])

    print(tabulate.tabulate(tbl, headers='firstrow', tablefmt='psql'))

    # Buy 2.5 ETH
    req = TradeRequest(action=BUY,
                       currency=Currency(symbol='ETH'),
                       quantity=Amount(units=0, nanos=500000000))

    order = pt.Trade(req, metadata=metadata)
    order = (Action.BUY.value,
             format_amount(order.quantity),
             order.currency.symbol,
             format_amount(order.executed_price),
             format_amount(order.resulting_portfolio.remaining_cash))
    logger.info(
        'ORDER EXECUTED: %s [%s] %s at USD[%s] (CASH remaining: %s)' % order)

    # Get real-time ticker info for ETH
    ti = TickerInfoStub(chan)
    stream = ti.Watch(TickerWatchRequest(currency=Currency(symbol="ETH")))
    for msg in stream:
        price = format_amount(msg.price)
        logger.info('ETH: %s' % price)


if __name__ == '__main__':
    main()
