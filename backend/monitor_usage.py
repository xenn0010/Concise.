#!/usr/bin/env python3
"""
Real-time monitoring script for Concise API usage.
Run this while testing with Cursor to see compression stats.
"""
import requests
import time
import json
from datetime import datetime

API_KEY = "csk_live_fHE48ooBG-4UMlg59HI73fOk157nhL_lmYne-Y-9uJ0"
BASE_URL = "http://localhost:8000"

def get_stats():
    """Fetch current usage statistics"""
    try:
        response = requests.get(
            f"{BASE_URL}/v1/stats",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        return None

def format_stats(stats):
    """Format stats for display"""
    if not stats:
        return "❌ Unable to fetch stats"

    lines = [
        f"\n{'='*60}",
        f"⏰ {datetime.now().strftime('%H:%M:%S')}",
        f"{'='*60}",
        f"",
        f"📊 Overall Statistics:",
        f"  Total compressions: {stats.get('total_compressions', 0)}",
        f"  Tokens saved: {stats.get('total_tokens_saved', 0):,}",
        f"  Cost saved: ${stats.get('total_cost_saved_usd', 0):.4f}",
        f"  Cache hit rate: {stats.get('cache_hit_rate', 0)*100:.1f}%",
        f"",
        f"⚡ Recent Activity:",
        f"  Compressions (last hour): {stats.get('compressions_last_hour', 0)}",
        f"  Tokens saved (last hour): {stats.get('tokens_saved_last_hour', 0):,}",
        f"",
        f"📈 Strategy Breakdown:"
    ]

    for strategy, count in stats.get('strategy_counts', {}).items():
        lines.append(f"  {strategy}: {count}")

    return "\n".join(lines)

def main():
    """Monitor stats in real-time"""
    print("🔍 Concise API Monitor")
    print("=" * 60)
    print("Watching for compression activity...")
    print("Press Ctrl+C to stop")
    print()

    last_total = 0

    try:
        while True:
            stats = get_stats()

            if stats:
                current_total = stats.get('total_compressions', 0)

                # Show full stats every time there's new activity
                if current_total != last_total:
                    print(format_stats(stats))

                    # Show delta
                    if last_total > 0:
                        new_compressions = current_total - last_total
                        print(f"\n🆕 {new_compressions} new compression(s)!")

                    last_total = current_total
                else:
                    # Just show a heartbeat
                    print(f"⏳ Waiting for activity... (total: {current_total})", end='\r')

            time.sleep(2)  # Check every 2 seconds

    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")
        print(format_stats(get_stats()))

if __name__ == "__main__":
    main()
