#!/usr/bin/env python3
"""
Terminal Dashboard for Bug Bounty Monitor
Shows real-time statistics and recent changes
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import curses

class Dashboard:
    def __init__(self, data_dir="./data", diff_dir="./data/diffs", baseline_dir="./data/baseline"):
        self.data_dir = Path(data_dir)
        self.diff_dir = Path(diff_dir)
        self.baseline_dir = Path(baseline_dir)

    def get_statistics(self):
        """Calculate statistics from monitoring data"""
        stats = {
            'total_targets': 0,
            'total_subdomains': 0,
            'total_endpoints': 0,
            'changes_24h': defaultdict(int),
            'changes_7d': defaultdict(int),
            'recent_changes': []
        }

        now = datetime.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        # Count baselines (targets)
        baseline_files = list(self.baseline_dir.glob("*_baseline.json"))
        stats['total_targets'] = len(baseline_files)

        # Analyze baselines
        for baseline_file in baseline_files:
            try:
                with open(baseline_file, 'r') as f:
                    data = json.load(f)
                    stats['total_subdomains'] += len(data.get('subdomains', {}))
                    stats['total_endpoints'] += len(data.get('endpoints', {}))
            except:
                continue

        # Analyze changes
        diff_files = sorted(self.diff_dir.glob("*.json"), key=os.path.getmtime, reverse=True)

        for diff_file in diff_files[:50]:  # Last 50 change files
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(diff_file))
                with open(diff_file, 'r') as f:
                    changes = json.load(f)

                    # Count changes
                    change_count = sum([
                        len(changes.get('new_subdomains', [])),
                        len(changes.get('new_endpoints', [])),
                        len(changes.get('changed_endpoints', [])),
                        len(changes.get('new_js_endpoints', []))
                    ])

                    if change_count > 0:
                        # Extract domain from filename
                        domain = diff_file.stem.rsplit('_', 2)[0]

                        # Add to recent changes
                        if len(stats['recent_changes']) < 20:
                            stats['recent_changes'].append({
                                'domain': domain,
                                'time': file_time.strftime("%Y-%m-%d %H:%M"),
                                'changes': changes,
                                'total': change_count
                            })

                        # Count for time periods
                        if file_time > day_ago:
                            stats['changes_24h']['new_subdomains'] += len(changes.get('new_subdomains', []))
                            stats['changes_24h']['new_endpoints'] += len(changes.get('new_endpoints', []))
                            stats['changes_24h']['new_js_endpoints'] += len(changes.get('new_js_endpoints', []))

                        if file_time > week_ago:
                            stats['changes_7d']['new_subdomains'] += len(changes.get('new_subdomains', []))
                            stats['changes_7d']['new_endpoints'] += len(changes.get('new_endpoints', []))
                            stats['changes_7d']['new_js_endpoints'] += len(changes.get('new_js_endpoints', []))

            except Exception as e:
                continue

        return stats

    def render_simple(self):
        """Simple text-based dashboard"""
        stats = self.get_statistics()

        print("\n" + "="*70)
        print(" " * 20 + "BUG BOUNTY MONITORING DASHBOARD")
        print("="*70)
        print()

        # Overview
        print("📊 OVERVIEW")
        print("-" * 70)
        print(f"  Total Targets:     {stats['total_targets']}")
        print(f"  Total Subdomains:  {stats['total_subdomains']}")
        print(f"  Total Endpoints:   {stats['total_endpoints']}")
        print()

        # Changes in last 24 hours
        print("⏰ CHANGES - LAST 24 HOURS")
        print("-" * 70)
        print(f"  New Subdomains:    {stats['changes_24h']['new_subdomains']}")
        print(f"  New Endpoints:     {stats['changes_24h']['new_endpoints']}")
        print(f"  New JS Endpoints:  {stats['changes_24h']['new_js_endpoints']}")
        print()

        # Changes in last 7 days
        print("📅 CHANGES - LAST 7 DAYS")
        print("-" * 70)
        print(f"  New Subdomains:    {stats['changes_7d']['new_subdomains']}")
        print(f"  New Endpoints:     {stats['changes_7d']['new_endpoints']}")
        print(f"  New JS Endpoints:  {stats['changes_7d']['new_js_endpoints']}")
        print()

        # Recent changes
        print("🔔 RECENT CHANGES")
        print("-" * 70)
        if stats['recent_changes']:
            for change in stats['recent_changes'][:10]:
                print(f"  [{change['time']}] {change['domain']}: {change['total']} changes")
                if change['changes'].get('new_subdomains'):
                    print(f"    └─ {len(change['changes']['new_subdomains'])} new subdomain(s)")
                if change['changes'].get('new_endpoints'):
                    print(f"    └─ {len(change['changes']['new_endpoints'])} new endpoint(s)")
        else:
            print("  No recent changes")

        print()
        print("="*70)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print()

    def render_interactive(self, stdscr):
        """Interactive curses-based dashboard"""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(1000)  # Refresh every second

        # Colors
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            stats = self.get_statistics()

            # Title
            title = "BUG BOUNTY MONITORING DASHBOARD"
            stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(4))

            # Overview
            row = 2
            stdscr.addstr(row, 2, "OVERVIEW", curses.A_BOLD | curses.color_pair(1))
            row += 1
            stdscr.addstr(row, 4, f"Targets:     {stats['total_targets']}")
            row += 1
            stdscr.addstr(row, 4, f"Subdomains:  {stats['total_subdomains']}")
            row += 1
            stdscr.addstr(row, 4, f"Endpoints:   {stats['total_endpoints']}")

            # 24h changes
            row += 2
            stdscr.addstr(row, 2, "LAST 24 HOURS", curses.A_BOLD | curses.color_pair(2))
            row += 1
            stdscr.addstr(row, 4, f"New Subdomains:   {stats['changes_24h']['new_subdomains']}", curses.color_pair(2))
            row += 1
            stdscr.addstr(row, 4, f"New Endpoints:    {stats['changes_24h']['new_endpoints']}", curses.color_pair(2))
            row += 1
            stdscr.addstr(row, 4, f"New JS Endpoints: {stats['changes_24h']['new_js_endpoints']}", curses.color_pair(2))

            # Recent changes
            row += 2
            stdscr.addstr(row, 2, "RECENT CHANGES", curses.A_BOLD | curses.color_pair(1))
            row += 1

            max_changes = min(height - row - 3, len(stats['recent_changes']))
            for i in range(max_changes):
                change = stats['recent_changes'][i]
                change_str = f"[{change['time']}] {change['domain']}: {change['total']} changes"
                if len(change_str) > width - 6:
                    change_str = change_str[:width-9] + "..."
                stdscr.addstr(row, 4, change_str)
                row += 1

            # Footer
            footer = f"Last updated: {datetime.now().strftime('%H:%M:%S')} | Press 'q' to quit"
            stdscr.addstr(height - 1, (width - len(footer)) // 2, footer, curses.color_pair(4))

            stdscr.refresh()

            # Check for quit
            key = stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Bug Bounty Monitoring Dashboard')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode (curses)')
    args = parser.parse_args()

    dashboard = Dashboard()

    if args.interactive:
        try:
            curses.wrapper(dashboard.render_interactive)
        except KeyboardInterrupt:
            pass
    else:
        dashboard.render_simple()

if __name__ == "__main__":
    main()
