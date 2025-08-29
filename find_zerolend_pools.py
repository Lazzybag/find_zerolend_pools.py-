#!/usr/bin/env python3
"""
find_zerolend_pools.py  (now with hourly Telegram alerts)

Runs forever:
  • prints pools ≈ $50 k to the console
    • sends a Telegram summary every 60 minutes
    """

    import json
    import time
    import requests
    from decimal import Decimal
    from web3 import Web3

    # ------------------------------------------------------------------
    # CONFIG
    # ------------------------------------------------------------------
    RPC = "https://linea.decubate.com"

    TELEGRAM_BOT_TOKEN = "7647657790:AAFQV-ijNQDKQ8mRWylniCYu8ZYpG078HTY"
    TELEGRAM_CHAT_ID   = "7435617388"

    THRESHOLD_LOW  = 40_000   # USD
    THRESHOLD_HIGH = 65_000   # USD

    PRICES = {
        "WETH": 2600,
            "USDC": 1,
                "USDT": 1,
                    "DAI": 1,
                        "WBTC": 60000,
                            "wstETH": 3000,
                                "weETH": 2600,
                                }

                                # ------------------------------------------------------------------
                                # WEB3
                                # ------------------------------------------------------------------
                                w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))
                                print("Connected:", w3.is_connected())

                                POOL_DATA_PROVIDER = "0x3B03863A9f73f8B6Ef594594B0646B48D3E1958c"
                                ABI = json.loads(
                                    '[{"inputs":[],"name":"getAllReservesTokens","outputs":[{"internalType":"address[]","name":"","type":"address[]"},{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveData","outputs":[{"components":[{"internalType":"uint256","name":"availableLiquidity","type":"uint256"},{"internalType":"uint256","name":"totalStableDebt","type":"uint256"},{"internalType":"uint256","name":"totalVariableDebt","type":"uint256"},{"internalType":"uint256","name":"liquidityRate","type":"uint256"},{"internalType":"uint256","name":"variableBorrowRate","type":"uint256"},{"internalType":"uint256","name":"stableBorrowRate","type":"uint256"},{"internalType":"uint256","name":"averageStableBorrowRate","type":"uint256"},{"internalType":"uint256","name":"liquidityIndex","type":"uint256"},{"internalType":"uint256","name":"variableBorrowIndex","type":"uint256"},{"internalType":"uint40","name":"lastUpdateTimestamp","type":"uint40"}],"name":"","type":"tuple"}],"stateMutability":"view","type":"function"}]'
                                    )
                                    contract = w3.eth.contract(address=Web3.to_checksum_address(POOL_DATA_PROVIDER), abi=ABI)

                                    # ------------------------------------------------------------------
                                    # CORE LOGIC
                                    # ------------------------------------------------------------------
                                    def scan_pools():
                                        reserves, symbols = contract.functions.getAllReservesTokens().call()
                                            hits = []
                                                for addr, sym in zip(reserves, symbols):
                                                        sym = sym.upper()
                                                                try:
                                                                            data = contract.functions.getReserveData(addr).call()
                                                                                    except Exception:
                                                                                                continue
                                                                                                        decimals = 18 if sym not in {"USDC", "USDT"} else 6
                                                                                                                liquidity = Decimal(data[0]) / 10**decimals
                                                                                                                        price = Decimal(PRICES.get(sym, 0))
                                                                                                                                usd = liquidity * price
                                                                                                                                        if THRESHOLD_LOW <= usd <= THRESHOLD_HIGH:
                                                                                                                                                    hits.append((sym, float(usd), addr))
                                                                                                                                                        return hits

                                                                                                                                                        def console_report(hits):
                                                                                                                                                            if not hits:
                                                                                                                                                                    print("No pools in $40 k–$65 k range right now.")
                                                                                                                                                                            return
                                                                                                                                                                                print("\n🎯 Pools ≈ $50 k:")
                                                                                                                                                                                    for sym, usd, addr in hits:
                                                                                                                                                                                            print(f"  {sym:<6} {usd:,.0f} USD  {addr}")

                                                                                                                                                                                            def send_telegram(hits):
                                                                                                                                                                                                if not hits:
                                                                                                                                                                                                        return
                                                                                                                                                                                                            lines = [f"Linea ZeroLend ≈ $50 k pools ({len(hits)} found):"]
                                                                                                                                                                                                                for sym, usd, addr in hits:
                                                                                                                                                                                                                        lines.append(f"• {sym:<6} {usd:,.0f} USD\n  <code>{addr}</code>")
                                                                                                                                                                                                                            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                                                                                                                                                                                                                                payload = {"chat_id": TELEGRAM_CHAT_ID, "text": "\n".join(lines), "parse_mode": "HTML"}
                                                                                                                                                                                                                                    try:
                                                                                                                                                                                                                                            r = requests.post(url, json=payload, timeout=10)
                                                                                                                                                                                                                                                    r.raise_for_status()
                                                                                                                                                                                                                                                        except Exception as e:
                                                                                                                                                                                                                                                                print("Telegram send failed:", e)

                                                                                                                                                                                                                                                                # ------------------------------------------------------------------
                                                                                                                                                                                                                                                                # MAIN LOOP
                                                                                                                                                                                                                                                                # ------------------------------------------------------------------
                                                                                                                                                                                                                                                                def main():
                                                                                                                                                                                                                                                                    while True:
                                                                                                                                                                                                                                                                            try:
                                                                                                                                                                                                                                                                                        hits = scan_pools()
                                                                                                                                                                                                                                                                                                    console_report(hits)
                                                                                                                                                                                                                                                                                                                send_telegram(hits)
                                                                                                                                                                                                                                                                                                                        except Exception as e:
                                                                                                                                                                                                                                                                                                                                    print("Scan error:", e)
                                                                                                                                                                                                                                                                                                                                            time.sleep(3600)

                                                                                                                                                                                                                                                                                                                                            if __name__ == "__main__":
                                                                                                                                                                                                                                                                                                                                                main()
                                                                                                                                                                                                                                                                                                                                                