def should_buy(price: float, moving_average: float) -> bool:
    """Return True if price is above moving average."""
    return price > moving_average
