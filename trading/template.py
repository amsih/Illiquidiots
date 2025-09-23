"""
Quant Challenge 2025

Algorithmic strategy template
"""

from enum import Enum
from typing import Optional
import numpy as np
import pandas as pd

class Side(Enum):
    BUY = 0
    SELL = 1

class Ticker(Enum):
    # TEAM_A (home team)
    TEAM_A = 0

def place_market_order(side: Side, ticker: Ticker, quantity: float) -> None:
    """Place a market order.
    
    Parameters
    ----------
    side
        Side of order to place
    ticker
        Ticker of order to place
    quantity
        Quantity of order to place
    """
    return

def place_limit_order(side: Side, ticker: Ticker, quantity: float, price: float, ioc: bool = False) -> int:
    """Place a limit order.
    
    Parameters
    ----------
    side
        Side of order to place
    ticker
        Ticker of order to place
    quantity
        Quantity of order to place
    price
        Price of order to place
    ioc
        Immediate or cancel flag (FOK)

    Returns
    -------
    order_id
        Order ID of order placed
    """
    return 0

def cancel_order(ticker: Ticker, order_id: int) -> bool:
    """Cancel an order.
    
    Parameters
    ----------
    ticker
        Ticker of order to cancel
    order_id
        Order ID of order to cancel

    Returns
    -------
    success
        True if order was cancelled, False otherwise
    """
    return 0

class Strategy:
    """Template for a strategy."""

    orderbook = []
    pricebook = []
    scorebook = []
    U = []
    D = []
    xRSI = []
    already_bought90 = False
    already_boughtMA = False
    RSI_Bought = False

    def reset_state(self) -> None:
        """Reset the state of the strategy to the start of game position.
        
        Since the sandbox execution can start mid-game, we recommend creating a
        function which can be called from __init__ and on_game_event_update (END_GAME).

        Note: In production execution, the game will start from the beginning
        and will not be replayed.
        """
        self.scorebook = []
        self.pricebook = []
        self.U = []
        self.D = []
        self.xRSI = []
        self.already_bought90 = False
        self.already_boughtMA = False
        self.RSI_Bought = False

    def __init__(self) -> None:
        self.reset_state()

    def moving_average(self, side, n = 5):
        try:
            return (np.convolve(np.array(self.pricebook)[:,side], np.ones(n), "valid") / n)[-1]
        except:
            pass

    def RSI(self, span = 7):
        try:
            if sum(self.pricebook[-1])/2 > sum(self.pricebook[-2])/2:
                self.U.append(sum(self.pricebook[-1])/2)
                self.D.append(0)
            elif sum(self.pricebook[-1])/2 < sum(self.pricebook[-2])/2:
                self.U.append(0)
                self.D.append(sum(self.pricebook[-1])/2)
            else:
                self.U.append(0)
                self.D.append(0)
            
            Uema = pd.DataFrame(self.U, columns = ["Up"]).ewm(span, adjust = False).mean()
            Dema = pd.DataFrame(self.D, columns = ["Up"]).ewm(span, adjust = False).mean()

            RS = (Uema/Dema).to_numpy()
            self.xRSI = 100 - 100/(1+RS)
        except IndexError:
            self.xRSI = []

    def on_trade_update(
        self, ticker: Ticker, side: Side, quantity: float, price: float
    ) -> None:
        """Called whenever two orders match. Could be one of your orders, or two other people's orders.
        Parameters
        ----------
        ticker
            Ticker of orders that were matched
        side:
            Side of orders that were matched
        quantity
            Volume traded
        price
            Price that trade was executed at
        """

        print(f"Python Trade update: {ticker} {side} {quantity} shares @ {price}")

    def on_orderbook_update(
        self, ticker: Ticker, side: Side, quantity: float, price: float
    ) -> None:
        """Called whenever the orderbook changes. This could be because of a trade, or because of a new order, or both.
        Parameters
        ----------
        ticker
            Ticker that has an orderbook update
        side
            Which orderbook was updated
        price
            Price of orderbook that has an update
        quantity
            Volume placed into orderbook
        """
        self.orderbook.append([ticker, side, quantity, price])

    def on_account_update(
        self,
        ticker: Ticker,
        side: Side,
        price: float,
        quantity: float,
        capital_remaining: float,
    ) -> None:
        """Called whenever one of your orders is filled.
        Parameters
        ----------
        ticker
            Ticker of order that was fulfilled
        side
            Side of order that was fulfilled
        price
            Price that order was fulfilled at
        quantity
            Volume of order that was fulfilled
        capital_remaining
            Amount of capital after fulfilling order
        """

        print(f"Order Fulfilled!")

    def on_orderbook_snapshot(self, ticker: Ticker, bids: list, asks: list) -> None:
        """Called periodically with a complete snapshot of the orderbook.

        This provides the full current state of all bids and asks, useful for 
        verification and algorithms that need the complete market picture.

        Parameters
        ----------
        ticker
            Ticker of the orderbook snapshot (Ticker.TEAM_A)
        bids
            List of (price, quantity) tuples for all current bids, sorted by price descending
        asks  
            List of (price, quantity) tuples for all current asks, sorted by price ascending
        """
        self.pricebook.append([bids[0][0], asks[0][0]])

    def on_game_event_update(self,
                           event_type: str,
                           home_away: str,
                           home_score: int,
                           away_score: int,
                           player_name: Optional[str],
                           substituted_player_name: Optional[str],
                           shot_type: Optional[str],
                           assist_player: Optional[str],
                           rebound_type: Optional[str],
                           coordinate_x: Optional[float],
                           coordinate_y: Optional[float],
                           time_seconds: Optional[float]
        ) -> None:
        """Called whenever a basketball game event occurs.
        Parameters
        ----------
        event_type
            Type of event that occurred
        home_score
            Home team score after event
        away_score
            Away team score after event
        player_name (Optional)
            Player involved in event
        substituted_player_name (Optional)
            Player being substituted out
        shot_type (Optional)
            Type of shot
        assist_player (Optional)
            Player who made the assist
        rebound_type (Optional)
            Type of rebound
        coordinate_x (Optional)
            X coordinate of shot location in feet
        coordinate_y (Optional)
            Y coordinate of shot location in feet
        time_seconds (Optional)
            Game time remaining in seconds
        """

        self.scorebook.append([home_score, away_score])

        try:
            if (self.pricebook[-1][1] >= 90) and not self.already_bought90:
                place_market_order(Side(0), Ticker(0), quantity = 20)
                self.already_bought90 = True
            if (self.moving_average(0, 7) >= self.pricebook[-1][1]) and not self.already_boughtMA:
                place_market_order(Side(0), Ticker(0), quantity = 10)
                self.already_boughtMA = True
            
            elif self.already_bought90 and (85 >= self.pricebook[-1][0]):
                place_market_order(Side(1), Ticker(0), quantity = 20)
                self.already_bought90 = False
            if (self.moving_average(1, 7) <= self.pricebook[-1][0]) and self.already_boughtMA:
                place_market_order(Side(1), Ticker(0), quantity = 10)
                self.already_boughtMA = False
        except IndexError:
            pass

        self.RSI()

        try:
            if self.xRSI[-2] < 30 and self.xRSI[-1] > 30 and not self.RSI_Bought:
                place_market_order(Side(0), Ticker(0), quantity = 30)
                self.RSI_Bought = True
            elif self.xRSI[-2] > 70 and self.xRSI[-1] < 70 and self.RSI_Bought:
                place_market_order(Side(1), Ticker(0), quantity = 30)
                self.RSI_Bought = False
        except IndexError:
            pass

        print(f"{event_type} {home_score} - {away_score}")

        if event_type == "END_GAME":
            # IMPORTANT: Highly recommended to call reset_state() when the
            # game ends. See reset_state() for more details.
            self.reset_state()
            return

