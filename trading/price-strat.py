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
    already_bought90 = False
    already_bought10  =False
    already_boughtspread = False
    already_soldspread = False

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
        self.already_bought90 = False
        self.already_bought10 = False
        self.already_boughtspread = False
        self.already_soldspread = False

    def __init__(self) -> None:
        self.reset_state()

    def moving_average(self, n = 5, book = pricebook):
        try:
            return np.convolve(book, np.ones(n), "valid") / n
        except:
            pass

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

        print(f"order fulfilled")
    
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

        self.pricebook.append((np.mean([b[0] for b in bids]) + np.mean([a[0] for a in asks])) / 2)

        MA10 = self.moving_average(10)
        MA20 = self.moving_average(20)

        try:
            if self.pricebook[-1] >= 90 and not self.already_bought90:
                place_market_order(Side.BUY, Ticker.TEAM_A, quantity = 50)
                self.already_bought90 = True
            elif self.pricebook[-1] <= 10 and not self.already_bought10:
                place_market_order(Side.SELL, Ticker.TEAM_A, quantity = 50)
                self.already_bought10 = True

            if MA10[-1] >= MA20[-1] and MA10[-2] < MA20[-2]:
                place_market_order(Side.BUY, Ticker.TEAM_A, quantity = (MA10[-1] - MA20[-1]) * 100)
                self.already_boughtMA = True

            if MA10[-1] <= MA20[-1] and MA10[-2] > MA20[-2]:
                place_market_order(Side.SELL, Ticker.TEAM_A, quantity = (MA20[-1] - MA10[-1]) * 100)
                self.already_boughtMA = False
        except IndexError:
            pass

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


        if event_type == "SCORE":
            self.scorebook.append([home_score, away_score])

        if time_seconds > 2000:
            pass
        
        else:
            try:
                scoreMAHome10 = self.moving_average(10, np.array(self.scorebook)[:,0]) 
                scoreMAAway10 = self.moving_average(10, np.array(self.scorebook)[:,1])
                scoreMAHome5 = self.moving_average(5, np.array(self.scorebook)[:,0]) 
                scoreMAAway5 = self.moving_average(5, np.array(self.scorebook)[:,1])


                if scoreMAHome5[-1] >= scoreMAHome10[-1] and scoreMAHome5[-2] < scoreMAHome10[-2] and self.scorebook[-1][0] > self.scorebook[-1][1]:
                    place_market_order(side = Side.BUY, ticker = Ticker.TEAM_A, quantity = (self.scorebook[-1][0] - self.scorebook[-1][1]) * 4)
                elif scoreMAHome5[-1] < scoreMAHome10[-1] and scoreMAHome5[-2] >= scoreMAHome10[-2] and self.scorebook[-1][0] < self.scorebook[-1][1]:
                    place_market_order(side = Side.SELL, ticker = Ticker.TEAM_A, quantity = (self.scorebook[-1][1] - self.scorebook[-1][0]) * 4)

                if scoreMAAway5[-1] >= scoreMAAway10[-1] and scoreMAAway5[-2] < scoreMAAway10[-2] and self.scorebook[-1][1] > self.scorebook[-1][0]:
                    place_market_order(side = Side.SELL, ticker = Ticker.TEAM_A, quantity = (self.scorebook[-1][1] - self.scorebook[-1][0]) * 4)
                elif scoreMAAway5[-1] < scoreMAAway10[-1] and scoreMAAway5[-2] >= scoreMAAway10[-2] and self.scorebook[-1][1] < self.scorebook[-1][0]:
                    place_market_order(side = Side.BUY, ticker = Ticker.TEAM_A, quantity = (self.scorebook[-1][0] - self.scorebook[-1][1]) * 4)

                if self.scorebook[-1][0] > self.scorebook[-1][1] + 10 and not self.already_boughtspread:
                    spread = (self.scorebook[-1][0] - self.scorebook[-2][0]) * 10
                    place_market_order(side = Side.BUY, ticker = Ticker.TEAM_A, quantity = spread)
                    self.already_boughtspread = True
                elif self.already_boughtspread and self.scorebook[-1][0] < self.scorebook[-1][1] - 5:
                    place_market_order(side = Side.SELL, ticker=Ticker.TEAM_A, quantity = spread)     
                    self.already_boughtspread = False
            
                if self.scorebook[-1][0] < self.scorebook[-1][1] + 10 and not self.already_soldspread:
                    spread = (self.scorebook[-1][0] - self.scorebook[-2][0]) * 10
                    place_market_order(side = Side.SELL, ticker = Ticker.TEAM_A, quantity = spread)
                    self.already_boughtspread = True
                elif self.already_soldspread and self.scorebook[-1][0] > self.scorebook[-1][1] - 5:
                    place_market_order(side = Side.BUY, ticker=Ticker.TEAM_A, quantity = spread)     
                    self.already_boughtspread = False            

            except IndexError:
                pass

        print(f"{event_type} {home_score} - {away_score}")

        if event_type == "END_GAME":
            # IMPORTANT: Highly recommended to call reset_state() when the
            # game ends. See reset_state() for more details.

            self.reset_state()
            return

