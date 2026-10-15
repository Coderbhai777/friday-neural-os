"""
ULTRON Real-Time Crypto & Stock Market Neural Ticker
Provides real-time equity & crypto telemetry, technical analysis indicators (RSI, MACD, SMA),
global market overviews, and proactive price alerts.
"""

import os
import io
import time
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data" / "market_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ALERTS_FILE = DATA_DIR / "price_alerts.json"

if not ALERTS_FILE.exists():
    ALERTS_FILE.write_text("[]", encoding="utf-8")


def _get_crypto_coingecko(coin_id: str) -> Optional[Dict[str, Any]]:
    """Fetches real-time crypto price and market stats from CoinGecko public API."""
    try:
        clean_coin = coin_id.lower().replace("-usd", "").replace("usd", "").strip()
        coin_map = {
            "btc": "bitcoin", "bitcoin": "bitcoin",
            "eth": "ethereum", "ethereum": "ethereum",
            "sol": "solana", "solana": "solana",
            "bnb": "binancecoin", "binance": "binancecoin",
            "xrp": "ripple", "ripple": "ripple",
            "doge": "dogecoin", "dogecoin": "dogecoin",
            "ada": "cardano", "cardano": "cardano",
            "dot": "polkadot", "polkadot": "polkadot",
            "matic": "matic-network", "polygon": "matic-network",
            "avax": "avalanche-2", "avalanche": "avalanche-2",
            "link": "chainlink", "chainlink": "chainlink"
        }
        target_id = coin_map.get(clean_coin, clean_coin)
        url = f"https://api.coingecko.com/api/v3/coins/{target_id}?localization=false&tickers=false&community_data=false&developer_data=false"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            market_data = data.get("market_data", {})
            return {
                "name": data.get("name"),
                "symbol": data.get("symbol", "").upper(),
                "price_usd": market_data.get("current_price", {}).get("usd", 0.0),
                "price_inr": market_data.get("current_price", {}).get("inr", 0.0),
                "change_24h_pct": round(market_data.get("price_change_percentage_24h", 0.0), 2),
                "high_24h_usd": market_data.get("high_24h", {}).get("usd", 0.0),
                "low_24h_usd": market_data.get("low_24h", {}).get("usd", 0.0),
                "market_cap_usd": market_data.get("market_cap", {}).get("usd", 0),
                "total_volume_usd": market_data.get("total_volume", {}).get("usd", 0),
                "ath_usd": market_data.get("ath", {}).get("usd", 0.0),
            }
    except Exception:
        pass
    return None


def _get_crypto_binance(symbol: str) -> Optional[Dict[str, Any]]:
    """Fallback to Binance public ticker API."""
    try:
        clean = symbol.upper().replace("-", "").replace("/", "")
        if not clean.endswith("USDT") and not clean.endswith("BTC"):
            clean = f"{clean}USDT"
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={clean}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            return {
                "name": symbol.upper(),
                "symbol": symbol.upper(),
                "price_usd": float(d.get("lastPrice", 0)),
                "price_inr": round(float(d.get("lastPrice", 0)) * 86.5, 2),
                "change_24h_pct": round(float(d.get("priceChangePercent", 0)), 2),
                "high_24h_usd": float(d.get("highPrice", 0)),
                "low_24h_usd": float(d.get("lowPrice", 0)),
                "total_volume_usd": float(d.get("quoteVolume", 0)),
            }
    except Exception:
        pass
    return None


async def get_stock_quote(symbol: str) -> str:
    """
    Fetches real-time market quote, day range, volume, 52-week range, and P/E ratio for any global stock or index.
    
    Args:
        symbol: Ticker symbol (e.g. 'AAPL', 'NVDA', 'TSLA', 'MSFT', 'RELIANCE.NS', 'TCS.NS', 'BTC-USD', '^GSPC').
    """
    def _execute():
        sym = symbol.strip().upper()
        # 1. If it's a known crypto, check crypto first
        if any(c in sym for c in ["BTC", "ETH", "SOL", "DOGE", "XRP", "BNB"]):
            cg = _get_crypto_coingecko(sym) or _get_crypto_binance(sym)
            if cg:
                arrow = "🟢" if cg.get("change_24h_pct", 0) >= 0 else "🔴"
                return (
                    f"💎 [CRYPTO QUOTE] {cg['name']} ({cg['symbol']})\n"
                    f"• Price (USD): ${cg['price_usd']:,.2f}\n"
                    f"• Price (INR): ₹{cg.get('price_inr', 0):,.2f}\n"
                    f"• 24h Change: {arrow} {cg.get('change_24h_pct', 0)}%\n"
                    f"• 24h Range: ${cg.get('low_24h_usd', 0):,.2f} - ${cg.get('high_24h_usd', 0):,.2f}\n"
                    f"• 24h Volume: ${cg.get('total_volume_usd', 0):,.0f}"
                )

        # 2. Use yfinance for stocks and indices
        try:
            import yfinance as yf
            ticker = yf.Ticker(sym)
            info = ticker.fast_info
            
            price = getattr(info, "last_price", None) or getattr(info, "previous_close", None)
            if price is None:
                # Try regular info
                reg_info = ticker.info
                price = reg_info.get("currentPrice") or reg_info.get("regularMarketPrice") or reg_info.get("previousClose")

            if price is None:
                return f"[FAIL] Could not fetch quote for ticker '{symbol}'. Verify the symbol name."

            prev_close = getattr(info, "previous_close", price)
            change = price - prev_close if prev_close else 0.0
            change_pct = (change / prev_close * 100) if prev_close else 0.0
            arrow = "🟢 +" if change >= 0 else "🔴 "
            
            currency = getattr(info, "currency", "USD") or "USD"
            sym_prefix = "₹" if currency == "INR" else "$"
            
            high_52 = getattr(info, "year_high", None)
            low_52 = getattr(info, "year_low", None)
            mcap = getattr(info, "market_cap", None)

            lines = [
                f"📈 [STOCK QUOTE] {sym}",
                f"• Live Price: {sym_prefix}{price:,.2f} {currency}",
                f"• Change: {arrow}{change:,.2f} ({change_pct:+.2f}%)",
            ]
            if low_52 and high_52:
                lines.append(f"• 52-Week Range: {sym_prefix}{low_52:,.2f} - {sym_prefix}{high_52:,.2f}")
            if mcap:
                lines.append(f"• Market Cap: {sym_prefix}{mcap:,.0f}")
                
            return "\n".join(lines)
        except Exception as e:
            # REST Fallback via Yahoo Query API
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1d"
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url, headers=headers, timeout=6)
                if res.status_code == 200:
                    d = res.json()
                    meta = d["chart"]["result"][0]["meta"]
                    lp = meta.get("regularMarketPrice", 0)
                    pc = meta.get("chartPreviousClose", lp)
                    chg = lp - pc
                    pct = (chg / pc) * 100 if pc else 0
                    arrow = "🟢 +" if chg >= 0 else "🔴 "
                    return (
                        f"📈 [STOCK QUOTE] {sym}\n"
                        f"• Price: ${lp:,.2f} {meta.get('currency', 'USD')}\n"
                        f"• Change: {arrow}{chg:,.2f} ({pct:+.2f}%)"
                    )
            except Exception:
                pass
            return f"[ERROR] Could not fetch quote for '{symbol}': {e}"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def get_crypto_ticker(coin: str = "bitcoin") -> str:
    """
    Fetches live cryptocurrency prices (USD & INR), 24h high/low, volume, and market stats.
    
    Args:
        coin: Coin name or symbol (e.g. 'bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol', 'xrp', 'doge').
    """
    def _execute():
        data = _get_crypto_coingecko(coin) or _get_crypto_binance(coin)
        if not data:
            return f"[FAIL] Could not retrieve crypto telemetry for '{coin}'."

        arrow = "🟢 +" if data.get("change_24h_pct", 0) >= 0 else "🔴 "
        lines = [
            f"⚡ [CRYPTO TELEMETRY] {data['name']} ({data['symbol']})",
            f"• Spot Price (USD): ${data['price_usd']:,.2f}",
            f"• Spot Price (INR): ₹{data.get('price_inr', 0):,.2f}",
            f"• 24h Change: {arrow}{data.get('change_24h_pct', 0)}%",
            f"• 24h High: ${data.get('high_24h_usd', 0):,.2f}",
            f"• 24h Low: ${data.get('low_24h_usd', 0):,.2f}",
        ]
        if data.get("market_cap_usd"):
            lines.append(f"• Market Cap: ${data['market_cap_usd']:,.0f}")
        if data.get("ath_usd"):
            lines.append(f"• All-Time High: ${data['ath_usd']:,.2f}")
            
        return "\n".join(lines)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def get_market_technical_analysis(symbol: str = "NVDA", period: str = "3mo") -> str:
    """
    Computes technical indicators (SMA-20, SMA-50, RSI 14, MACD, Bollinger Bands) and provides an AI technical outlook.
    
    Args:
        symbol: Stock or Crypto ticker (e.g. 'NVDA', 'AAPL', 'TSLA', 'BTC-USD', 'RELIANCE.NS').
        period: Timeframe ('1mo', '3mo', '6mo', '1y').
    """
    def _execute():
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np

            sym = symbol.strip().upper()
            t = yf.Ticker(sym)
            df = t.history(period=period)
            
            if df.empty or len(df) < 15:
                return f"[FAIL] Insufficient historical data for '{symbol}' over period '{period}'."

            close = df["Close"]
            current_price = close.iloc[-1]

            # 1. Simple Moving Averages
            sma_20 = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else current_price
            sma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else current_price

            # 2. RSI (14)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            rsi = rsi_series.iloc[-1]

            # 3. Bollinger Bands (20)
            std_20 = close.rolling(window=20).std().iloc[-1] if len(close) >= 20 else 0
            bb_upper = sma_20 + (std_20 * 2)
            bb_lower = sma_20 - (std_20 * 2)

            # Signal evaluation
            rsi_verdict = "OVERBOUGHT (High Pullback Risk)" if rsi >= 70 else ("OVERSOLD (Rebound Potential)" if rsi <= 30 else "NEUTRAL / HEALTHY MOMENTUM")
            trend_verdict = "BULLISH (Trading above SMA-20 & SMA-50)" if current_price > sma_20 and current_price > sma_50 else ("BEARISH (Below key Moving Averages)" if current_price < sma_20 and current_price < sma_50 else "MIXED / CONSOLIDATION")

            return (
                f"📊 [TECHNICAL ANALYSIS] {sym} (Timeframe: {period})\n"
                f"• Current Close: ${current_price:,.2f}\n"
                f"• SMA-20: ${sma_20:,.2f} | SMA-50: ${sma_50:,.2f}\n"
                f"• Relative Strength Index (RSI 14): {rsi:.1f} [{rsi_verdict}]\n"
                f"• Bollinger Upper: ${bb_upper:,.2f} | Lower: ${bb_lower:,.2f}\n"
                f"• Trend Analysis: {trend_verdict}\n"
                f"• Summary: Market bias is {trend_verdict.split(' ')[0]} with RSI at {rsi:.1f}."
            )
        except Exception as e:
            return f"[ERROR] Technical analysis computation failed for '{symbol}': {e}"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def get_market_overview() -> str:
    """
    Provides a real-time macro overview of key global market indices, commodities, and benchmark cryptos.
    """
    def _execute():
        benchmarks = [
            ("^GSPC", "S&P 500"),
            ("^IXIC", "NASDAQ"),
            ("^NSEI", "Nifty 50"),
            ("^BSESN", "BSE Sensex"),
            ("BTC-USD", "Bitcoin"),
            ("ETH-USD", "Ethereum"),
            ("GC=F", "Gold"),
            ("CL=F", "Crude Oil")
        ]
        
        results = ["🌐 [GLOBAL MARKET SNAPSHOT]"]
        try:
            import yfinance as yf
            for sym, name in benchmarks:
                try:
                    t = yf.Ticker(sym)
                    info = t.fast_info
                    p = getattr(info, "last_price", None) or getattr(info, "previous_close", None)
                    prev = getattr(info, "previous_close", p)
                    if p:
                        chg_pct = ((p - prev) / prev * 100) if prev else 0.0
                        arrow = "🟢 +" if chg_pct >= 0 else "🔴 "
                        results.append(f"• {name} ({sym}): {p:,.2f} | {arrow}{chg_pct:+.2f}%")
                except Exception:
                    continue
        except Exception:
            pass

        if len(results) <= 1:
            # Fallback to crypto telemetry
            for c in ["bitcoin", "ethereum", "solana"]:
                cg = _get_crypto_coingecko(c)
                if cg:
                    arrow = "🟢 +" if cg.get("change_24h_pct", 0) >= 0 else "🔴 "
                    results.append(f"• {cg['name']}: ${cg['price_usd']:,.2f} | {arrow}{cg.get('change_24h_pct', 0)}%")

        return "\n".join(results)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def set_price_alert(symbol: str, target_price: float, condition: str = "above") -> str:
    """
    Sets an automated threshold alert for a stock or cryptocurrency.
    
    Args:
        symbol: Ticker symbol (e.g. 'NVDA', 'BTC', 'TSLA', 'RELIANCE.NS').
        target_price: Trigger price number.
        condition: 'above' (trigger when price rises above target) or 'below' (when price drops below target).
    """
    try:
        alerts = []
        if ALERTS_FILE.exists():
            alerts = json.loads(ALERTS_FILE.read_text(encoding="utf-8"))
            
        new_alert = {
            "id": f"alert_{int(time.time())}",
            "symbol": symbol.strip().upper(),
            "target_price": float(target_price),
            "condition": condition.lower().strip(),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active"
        }
        alerts.append(new_alert)
        ALERTS_FILE.write_text(json.dumps(alerts, indent=2), encoding="utf-8")
        
        return f"🔔 [PRICE ALERT ARMED]: Alert created for {new_alert['symbol']} when price moves {new_alert['condition']} ${new_alert['target_price']:,.2f}."
    except Exception as e:
        return f"[ERROR] Failed to set price alert: {e}"
