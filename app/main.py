"""Entry point for the trading system."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Trading system entry point")
    parser.add_argument("--mode", choices=["backtest", "paper", "live"], required=True)
    args = parser.parse_args()

    print(f"Running in {args.mode} mode")


if __name__ == "__main__":
    main()
