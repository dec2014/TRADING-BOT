API_KEY = "GYB6hw04vHgEE579qSQsksLuSDwKLinsyHdzPL8UXIwjxBpGjRcQh7vQfWItYHbd"
API_SECRET = "8sSxJ33EmCKbVPOfVtFdtYboA6Mvx6l60AtP99DoAcqyEdCTnKHJ983cNeDP9yJ5"


import logging
import sys
from typing import Optional, Dict, Any

from binance import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


TESTNET_BASE_URL = "https://testnet.binancefuture.com"  # USDT-M futures testnet REST base URL
SYMBOL_DEFAULT = "BTCUSDT"


def setup_logger(log_file: str = "bot.log") -> logging.Logger:
    logger = logging.getLogger("basic_bot")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        fh_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)

    return logger


class BasicBot:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = True,
        symbol: str = SYMBOL_DEFAULT,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger or setup_logger()
        self.symbol = symbol.upper()

        # python-binance futures testnet usage:
        # - testnet=True switches to test endpoints where supported
        # - futures endpoints use fapi / dapi internally
        self.client = Client(api_key, api_secret, testnet=testnet)
        # Ensure futures base URL is testnet for USDT-M
        self.client.FUTURES_URL = TESTNET_BASE_URL

        self.logger.info("BasicBot initialized for symbol %s (testnet=%s)", self.symbol, testnet)

    def _log_request(self, action: str, params: Dict[str, Any]) -> None:
        self.logger.info("REQUEST %s: %s", action, params)

    def _log_response(self, action: str, response: Dict[str, Any]) -> None:
        self.logger.info("RESPONSE %s: %s", action, response)

    def _log_error(self, action: str, error: Exception) -> None:
        self.logger.error("ERROR %s: %s", action, str(error))

    def place_market_order(self, side: str, quantity: float) -> Optional[Dict[str, Any]]:
        """
        Place a market order on USDT-M futures.
        side: 'BUY' or 'SELL'
        """
        side = side.upper()
        params = {
            "symbol": self.symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
        }
        self._log_request("market_order", params)
        try:
            resp = self.client.futures_create_order(**params)
            self._log_response("market_order", resp)
            return resp
        except (BinanceAPIException, BinanceRequestException, Exception) as e:
            self._log_error("market_order", e)
            return None

    def place_limit_order(
        self,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC",
    ) -> Optional[Dict[str, Any]]:
        """
        Place a limit order on USDT-M futures.
        side: 'BUY' or 'SELL'
        """
        side = side.upper()
        params = {
            "symbol": self.symbol,
            "side": side,
            "type": "LIMIT",
            "timeInForce": time_in_force,
            "quantity": quantity,
            "price": price,
        }
        self._log_request("limit_order", params)
        try:
            resp = self.client.futures_create_order(**params)
            self._log_response("limit_order", resp)
            return resp
        except (BinanceAPIException, BinanceRequestException, Exception) as e:
            self._log_error("limit_order", e)
            return None

    def place_stop_limit_order(
        self,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: str = "GTC",
    ) -> Optional[Dict[str, Any]]:
        """
        Place a Stop-Limit order on USDT-M futures.
        side: 'BUY' or 'SELL'
        """
        side = side.upper()
        params = {
            "symbol": self.symbol,
            "side": side,
            "type": "STOP",
            "timeInForce": time_in_force,
            "quantity": quantity,
            "price": price,
            "stopPrice": stop_price,
        }
        self._log_request("stop_limit_order", params)
        try:
            resp = self.client.futures_create_order(**params)
            self._log_response("stop_limit_order", resp)
            return resp
        except (BinanceAPIException, BinanceRequestException, Exception) as e:
            self._log_error("stop_limit_order", e)
            return None


def validate_float(prompt: str) -> float:
    while True:
        value = input(prompt).strip()
        try:
            val = float(value)
            if val <= 0:
                print("Value must be positive.")
                continue
            return val
        except ValueError:
            print("Invalid number, try again.")


def validate_side(prompt: str) -> str:
    while True:
        side = input(prompt).strip().upper()
        if side in ["BUY", "SELL"]:
            return side
        print("Side must be BUY or SELL.")


def validate_order_type(prompt: str) -> str:
    allowed = ["MARKET", "LIMIT", "STOP_LIMIT"]
    while True:
        ot = input(prompt).strip().upper()
        if ot in allowed:
            return ot
        print(f"Order type must be one of: {', '.join(allowed)}")


def main():
    logger = setup_logger()

    print("=== Binance Futures Testnet Bot (USDT-M) ===")
    api_key = input("Enter API Key: ").strip()
    api_secret = input("Enter API Secret: ").strip()
    symbol = input(f"Enter symbol (default {SYMBOL_DEFAULT}): ").strip() or SYMBOL_DEFAULT

    bot = BasicBot(api_key, api_secret, testnet=True, symbol=symbol, logger=logger)

    while True:
        print("\nChoose action:")
        print("1) Place order")
        print("2) Exit")
        choice = input("Enter choice: ").strip()

        if choice == "2":
            print("Exiting.")
            break
        elif choice != "1":
            print("Invalid choice.")
            continue

        order_type = validate_order_type("Order type (MARKET / LIMIT / STOP_LIMIT): ")
        side = validate_side("Side (BUY / SELL): ")
        quantity = validate_float("Quantity: ")

        if order_type == "MARKET":
            resp = bot.place_market_order(side=side, quantity=quantity)

        elif order_type == "LIMIT":
            price = validate_float("Limit price: ")
            resp = bot.place_limit_order(
                side=side,
                quantity=quantity,
                price=price,
                time_in_force="GTC",
            )

        else:  # STOP_LIMIT
            stop_price = validate_float("Stop price (trigger): ")
            limit_price = validate_float("Limit price: ")
            resp = bot.place_stop_limit_order(
                side=side,
                quantity=quantity,
                price=limit_price,
                stop_price=stop_price,
                time_in_force="GTC",
            )

        if resp is not None:
            status = resp.get("status")
            order_id = resp.get("orderId")
            print(f"Order placed. ID: {order_id}, Status: {status}")
        else:
            print("Order failed. Check logs for details.")


if __name__ == "__main__":
    main()
