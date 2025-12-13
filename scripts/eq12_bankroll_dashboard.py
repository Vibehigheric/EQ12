"""
EQ12 Bankroll Dashboard

Real-time bankroll monitoring, performance analytics, and visualization.

Author: EQ12 System
Created: 2025-11-28
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import argparse
from collections import defaultdict


class EQ12BankrollDashboard:
    """Interactive bankroll dashboard and analytics"""
    
    def __init__(self, db_path: str = "../logs/eq12_bankroll.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
            
    def _query(self, sql: str, params: tuple = ()) -> List:
        """Execute SQL query"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        return results
        
    def get_summary(self) -> Dict:
        """Get overall summary"""
        # Latest snapshot
        snapshot = self._query("""
            SELECT * FROM snapshots ORDER BY timestamp DESC LIMIT 1
        """)
        
        if not snapshot:
            return {'error': 'No data available'}
            
        s = snapshot[0]
        
        # Pending bets
        pending = self._query("""
            SELECT COUNT(*), SUM(stake) FROM bets WHERE status = 'pending'
        """)[0]
        
        # Recent performance (last 7 days)
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        recent_bets = self._query("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won,
                SUM(profit_loss) as profit
            FROM bets 
            WHERE result_timestamp >= ? AND status IN ('won', 'lost')
        """, (week_ago,))[0]
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'bankroll': {
                'total': s[2],
                'available': s[3],
                'pending_amount': s[4],
                'pending_count': pending[0] or 0
            },
            'lifetime': {
                'total_bets': s[5],
                'won': s[6],
                'lost': s[7],
                'win_rate': s[8] * 100,
                'roi': s[9],
                'profit_loss': s[10]
            },
            'recent_7days': {
                'bets': recent_bets[0] or 0,
                'won': recent_bets[1] or 0,
                'win_rate': ((recent_bets[1] or 0) / max(recent_bets[0] or 1, 1)) * 100,
                'profit': recent_bets[2] or 0
            },
            'sizing': {
                'largest_bet': s[11],
                'average_bet': s[12]
            },
            'risk': {
                'sharpe_ratio': s[13],
                'max_drawdown': s[14]
            }
        }
        
    def get_pending_bets(self) -> List[Dict]:
        """Get all pending bets"""
        results = self._query("""
            SELECT 
                bet_id, timestamp, sport, game, outcome,
                odds, stake, edge_percent, confidence_score,
                sportsbook, sharp_money, steam_move
            FROM bets 
            WHERE status = 'pending'
            ORDER BY confidence_score DESC, timestamp DESC
        """)
        
        bets = []
        for r in results:
            bets.append({
                'bet_id': r[0],
                'timestamp': r[1],
                'sport': r[2],
                'game': r[3],
                'outcome': r[4],
                'odds': r[5],
                'stake': r[6],
                'edge': r[7],
                'confidence': r[8],
                'book': r[9],
                'sharp': bool(r[10]),
                'steam': bool(r[11])
            })
            
        return bets
        
    def get_recent_results(self, limit: int = 20) -> List[Dict]:
        """Get recent settled bets"""
        results = self._query("""
            SELECT 
                bet_id, timestamp, result_timestamp, sport, game,
                outcome, odds, stake, profit_loss, status,
                edge_percent, confidence_score, sportsbook
            FROM bets 
            WHERE status IN ('won', 'lost', 'pushed')
            ORDER BY result_timestamp DESC
            LIMIT ?
        """, (limit,))
        
        bets = []
        for r in results:
            bets.append({
                'bet_id': r[0],
                'placed': r[1],
                'settled': r[2],
                'sport': r[3],
                'game': r[4],
                'outcome': r[5],
                'odds': r[6],
                'stake': r[7],
                'profit_loss': r[8],
                'status': r[9],
                'edge': r[10],
                'confidence': r[11],
                'book': r[12]
            })
            
        return bets
        
    def get_performance_by_sport(self) -> Dict:
        """Performance breakdown by sport"""
        results = self._query("""
            SELECT 
                sport,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won,
                SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as lost,
                SUM(stake) as total_staked,
                SUM(COALESCE(profit_loss, 0)) as net_profit,
                AVG(edge_percent) as avg_edge,
                AVG(confidence_score) as avg_confidence
            FROM bets
            WHERE status IN ('won', 'lost')
            GROUP BY sport
            ORDER BY net_profit DESC
        """)
        
        sports = {}
        for r in results:
            win_rate = (r[2] / max(r[1], 1)) * 100
            roi = (r[5] / max(r[4], 1)) * 100
            
            sports[r[0]] = {
                'total_bets': r[1],
                'won': r[2],
                'lost': r[3],
                'win_rate': win_rate,
                'total_staked': r[4],
                'net_profit': r[5],
                'roi': roi,
                'avg_edge': r[6],
                'avg_confidence': r[7]
            }
            
        return sports
        
    def get_performance_by_type(self) -> Dict:
        """Performance breakdown by bet type"""
        results = self._query("""
            SELECT 
                bet_type,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won,
                SUM(stake) as total_staked,
                SUM(COALESCE(profit_loss, 0)) as net_profit
            FROM bets
            WHERE status IN ('won', 'lost')
            GROUP BY bet_type
            ORDER BY net_profit DESC
        """)
        
        types = {}
        for r in results:
            win_rate = (r[2] / max(r[1], 1)) * 100
            roi = (r[4] / max(r[3], 1)) * 100
            
            types[r[0]] = {
                'total_bets': r[1],
                'won': r[2],
                'win_rate': win_rate,
                'total_staked': r[3],
                'net_profit': r[4],
                'roi': roi
            }
            
        return types
        
    def get_sharp_performance(self) -> Dict:
        """Performance on sharp money vs regular bets"""
        results = self._query("""
            SELECT 
                CASE WHEN sharp_money = 1 THEN 'Sharp' ELSE 'Regular' END as category,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won,
                SUM(stake) as total_staked,
                SUM(COALESCE(profit_loss, 0)) as net_profit
            FROM bets
            WHERE status IN ('won', 'lost')
            GROUP BY sharp_money
        """)
        
        performance = {}
        for r in results:
            win_rate = (r[2] / max(r[1], 1)) * 100
            roi = (r[4] / max(r[3], 1)) * 100
            
            performance[r[0]] = {
                'total_bets': r[1],
                'won': r[2],
                'win_rate': win_rate,
                'total_staked': r[3],
                'net_profit': r[4],
                'roi': roi
            }
            
        return performance
        
    def get_bankroll_history(self, days: int = 30) -> List[Dict]:
        """Get bankroll snapshots over time"""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        results = self._query("""
            SELECT 
                timestamp, total_bankroll, available_bankroll,
                pending_amount, profit_loss, roi
            FROM snapshots
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        """, (cutoff,))
        
        history = []
        for r in results:
            history.append({
                'timestamp': r[0],
                'total': r[1],
                'available': r[2],
                'pending': r[3],
                'profit_loss': r[4],
                'roi': r[5]
            })
            
        return history
        
    def print_dashboard(self):
        """Print formatted dashboard to console"""
        summary = self.get_summary()
        
        if 'error' in summary:
            print(f"❌ {summary['error']}")
            return
            
        print("\n" + "=" * 80)
        print("💰 EQ12 BANKROLL DASHBOARD")
        print("=" * 80)
        print(f"📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 80)
        
        # Bankroll section
        br = summary['bankroll']
        print(f"\n💵 CURRENT BANKROLL")
        print(f"   Total:     ${br['total']:>12,.2f}")
        print(f"   Available: ${br['available']:>12,.2f}")
        print(f"   Pending:   ${br['pending_amount']:>12,.2f} ({br['pending_count']} bets)")
        
        # Lifetime performance
        lt = summary['lifetime']
        print(f"\n📊 LIFETIME PERFORMANCE")
        print(f"   Total Bets: {lt['total_bets']}")
        print(f"   Won/Lost:   {lt['won']}/{lt['lost']}")
        print(f"   Win Rate:   {lt['win_rate']:.1f}%")
        print(f"   ROI:        {lt['roi']:.2f}%")
        print(f"   P/L:        ${lt['profit_loss']:,.2f}")
        
        # Recent performance
        rec = summary['recent_7days']
        if rec['bets'] > 0:
            print(f"\n🕐 LAST 7 DAYS")
            print(f"   Bets:       {rec['bets']}")
            print(f"   Won:        {rec['won']}")
            print(f"   Win Rate:   {rec['win_rate']:.1f}%")
            print(f"   P/L:        ${rec['profit']:.2f}")
            
        # Pending bets
        pending = self.get_pending_bets()
        if pending:
            print(f"\n⏳ PENDING BETS ({len(pending)})")
            print(f"   {'Sport':<10} {'Game':<30} {'Stake':<10} {'Conf':<5} {'Edge':<5}")
            print(f"   {'-'*70}")
            for bet in pending[:5]:  # Show top 5
                indicators = ""
                if bet['sharp']: indicators += "🔥"
                if bet['steam']: indicators += "🌊"
                print(f"   {bet['sport']:<10} {bet['game'][:28]:<30} "
                      f"${bet['stake']:>7.2f}  {bet['confidence']:>3.0f}  "
                      f"{bet['edge']:>4.1f}% {indicators}")
            if len(pending) > 5:
                print(f"   ... and {len(pending)-5} more")
                
        # Recent results
        print(f"\n📈 RECENT RESULTS")
        results = self.get_recent_results(5)
        if results:
            print(f"   {'Status':<6} {'Sport':<8} {'Outcome':<25} {'Stake':<10} {'P/L':<10}")
            print(f"   {'-'*70}")
            for bet in results:
                status_icon = "✅" if bet['status'] == 'won' else "❌" if bet['status'] == 'lost' else "⚪"
                print(f"   {status_icon} {bet['status']:<6} {bet['sport']:<8} "
                      f"{bet['outcome'][:23]:<25} ${bet['stake']:>7.2f}  "
                      f"${bet['profit_loss']:>7.2f}")
        else:
            print("   No settled bets yet")
            
        # Performance by sport
        sports = self.get_performance_by_sport()
        if sports:
            print(f"\n🏆 PERFORMANCE BY SPORT")
            print(f"   {'Sport':<12} {'Bets':<6} {'Win%':<7} {'ROI%':<7} {'P/L':<12}")
            print(f"   {'-'*50}")
            for sport, data in sorted(sports.items(), key=lambda x: x[1]['roi'], reverse=True):
                print(f"   {sport:<12} {data['total_bets']:<6} "
                      f"{data['win_rate']:>5.1f}%  {data['roi']:>5.1f}%  "
                      f"${data['net_profit']:>9.2f}")
                      
        # Sharp money performance
        sharp = self.get_sharp_performance()
        if len(sharp) > 1:
            print(f"\n🔥 SHARP MONEY ANALYSIS")
            for category, data in sharp.items():
                print(f"   {category}:")
                print(f"      Bets: {data['total_bets']}, Win Rate: {data['win_rate']:.1f}%, "
                      f"ROI: {data['roi']:.1f}%, P/L: ${data['net_profit']:.2f}")
                      
        print("\n" + "=" * 80)
        
    def export_report(self, output_path: str):
        """Export comprehensive JSON report"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': self.get_summary(),
            'pending_bets': self.get_pending_bets(),
            'recent_results': self.get_recent_results(50),
            'performance_by_sport': self.get_performance_by_sport(),
            'performance_by_type': self.get_performance_by_type(),
            'sharp_performance': self.get_sharp_performance(),
            'bankroll_history': self.get_bankroll_history(30)
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"✅ Report exported to {output_path}")
        return report


def main():
    parser = argparse.ArgumentParser(description="EQ12 Bankroll Dashboard")
    parser.add_argument('--db', default='../logs/eq12_bankroll.db', help='Database path')
    parser.add_argument('--export', help='Export report to JSON file')
    parser.add_argument('--watch', action='store_true', help='Watch mode (refresh every 30s)')
    
    args = parser.parse_args()
    
    dashboard = EQ12BankrollDashboard(args.db)
    
    if args.watch:
        import time
        import os
        print("🔄 Watch mode - refreshing every 30 seconds (Ctrl+C to stop)")
        try:
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                dashboard.print_dashboard()
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n✅ Watch mode stopped")
    else:
        dashboard.print_dashboard()
        
    if args.export:
        dashboard.export_report(args.export)


if __name__ == '__main__':
    main()
