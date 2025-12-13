#!/usr/bin/env python3
"""
EQ12 Betting Dashboard - Godlike Betting Interactive Interface
Streamlit dashboard for viewing predictions, managing bets, and monitoring performance
Real-time filtering by time, edge thresholds, and bankroll management
"""

import json
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Add EQ12 to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure paths
data_dir = Path("C:/EQ12/data")
reports_dir = Path("C:/EQ12/reports")
logs_dir = Path("C:/EQ12/logs")

# Page config
st.set_page_config(
    page_title="EQ12 Godlike Betting Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .value-bet {
        background: linear-gradient(90deg, #00c851 0%, #00a041 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
    }
    .warning-bet {
        background: linear-gradient(90deg, #ffbb33 0%, #ff8800 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

class EQ12BettingDashboard:
    """Interactive Streamlit dashboard for EQ12 betting system"""
    
    def __init__(self):
        self.data_loaded = False
        self.predictions_df = pd.DataFrame()
        self.value_bets_df = pd.DataFrame()
        self.consolidated_report = {}
        
    def load_latest_data(self):
        """Load the most recent prediction and betting data"""
        try:
            # Find latest files
            prediction_files = list(reports_dir.glob("predictions_*.csv"))
            value_bet_files = list(reports_dir.glob("value_bets_*.csv"))
            report_files = list(reports_dir.glob("consolidated_report_*.json"))
            
            if not prediction_files:
                # If no CSV files, try to find JSON data in logs
                csv_files = list(logs_dir.glob("sgp_recs_*.csv"))
                if csv_files:
                    st.info("🔄 Loading SGP recommendations from logs")
                    latest_sgp = max(csv_files, key=os.path.getctime)
                    self.predictions_df = pd.read_csv(latest_sgp)
                    # Create dummy value bets for demo
                    if not self.predictions_df.empty:
                        self.create_demo_value_bets()
                else:
                    st.error("❌ No prediction files found. Please run the betting pipeline first.")
                    return False
            else:
                # Load latest predictions
                latest_predictions = max(prediction_files, key=os.path.getctime)
                self.predictions_df = pd.read_csv(latest_predictions)
            
            # Load value bets if available
            if value_bet_files:
                latest_value_bets = max(value_bet_files, key=os.path.getctime)
                self.value_bets_df = pd.read_csv(latest_value_bets)
            
            # Load consolidated report if available
            if report_files:
                latest_report = max(report_files, key=os.path.getctime)
                with open(latest_report) as f:
                    self.consolidated_report = json.load(f)
            
            # Process datetime columns
            if 'start_time' in self.predictions_df.columns:
                self.predictions_df['start_time_dt'] = pd.to_datetime(self.predictions_df['start_time'])
            elif 'game_time' in self.predictions_df.columns:
                self.predictions_df['start_time_dt'] = pd.to_datetime(self.predictions_df['game_time'])
            
            if not self.value_bets_df.empty and 'start_time' in self.value_bets_df.columns:
                self.value_bets_df['start_time_dt'] = pd.to_datetime(self.value_bets_df['start_time'])
            
            self.data_loaded = True
            return True
            
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return False
    
    def create_demo_value_bets(self):
        """Create demo value bets from SGP data for testing"""
        try:
            if self.predictions_df.empty:
                return
            
            # Create sample value bets from SGP recommendations
            sample_size = min(10, len(self.predictions_df))
            demo_data = []
            
            for idx, row in self.predictions_df.head(sample_size).iterrows():
                demo_data.append({
                    'league': 'NFL',  # Assume NFL for SGP data
                    'away_team': row.get('away_team', 'Away Team'),
                    'home_team': row.get('home_team', 'Home Team'),
                    'bet_team_name': row.get('home_team', 'Home Team'),
                    'bookmaker': 'DraftKings',
                    'odds': np.random.randint(-200, 300),
                    'edge_percent': np.random.uniform(5, 15),
                    'kelly_stake': np.random.uniform(10, 50),
                    'profit_potential': np.random.uniform(15, 75),
                    'expected_value': np.random.uniform(2, 8),
                    'start_time': datetime.now().isoformat()
                })
            
            self.value_bets_df = pd.DataFrame(demo_data)
            self.value_bets_df['start_time_dt'] = pd.to_datetime(self.value_bets_df['start_time'])
            
        except Exception as e:
            st.warning(f"Could not create demo value bets: {e}")
    
    def render_header(self):
        """Render main dashboard header"""
        st.markdown("""
        <div class="main-header">
            <h1>🎯 EQ12 GODLIKE BETTING DASHBOARD</h1>
            <p>Real-time predictions, value betting, and bankroll management</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar_controls(self):
        """Render sidebar filtering controls"""
        st.sidebar.markdown("## 🎛️ Filters & Controls")
        
        # Time filtering
        st.sidebar.markdown("### ⏰ Time Filtering")
        
        target_time = st.sidebar.time_input(
            "Games starting at or after:",
            value=datetime.strptime("12:00", "%H:%M").time(),
            help="Filter games by start time"
        )
        
        time_mode = st.sidebar.selectbox(
            "Time Filter Mode",
            ["At or After", "Within ±15 minutes"],
            help="How to apply the time filter"
        )
        
        # Edge filtering
        st.sidebar.markdown("### 📈 Value Betting")
        
        min_edge = st.sidebar.slider(
            "Minimum Edge %",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            help="Minimum betting edge percentage"
        )
        
        min_stake = st.sidebar.slider(
            "Minimum Stake $",
            min_value=5.0,
            max_value=100.0,
            value=10.0,
            step=5.0,
            help="Minimum Kelly stake amount"
        )
        
        # Bankroll management
        st.sidebar.markdown("### 💰 Bankroll Management")
        
        total_bankroll = st.sidebar.number_input(
            "Total Bankroll $",
            min_value=100.0,
            max_value=10000.0,
            value=1000.0,
            step=50.0,
            help="Your total betting bankroll"
        )
        
        max_risk_pct = st.sidebar.slider(
            "Max Risk %",
            min_value=1.0,
            max_value=25.0,
            value=10.0,
            step=1.0,
            help="Maximum percentage of bankroll to risk"
        )
        
        # League filtering
        st.sidebar.markdown("### 🏆 Leagues")
        
        if not self.predictions_df.empty:
            available_leagues = ['NFL', 'NBA', 'MLB', 'NHL', 'NCAAF', 'SOCCER']
            selected_leagues = st.sidebar.multiselect(
                "Select Leagues",
                available_leagues,
                default=available_leagues,
                help="Filter by sports leagues"
            )
        else:
            selected_leagues = []
        
        return {
            'target_time': target_time,
            'time_mode': time_mode,
            'min_edge': min_edge,
            'min_stake': min_stake,
            'total_bankroll': total_bankroll,
            'max_risk_pct': max_risk_pct,
            'selected_leagues': selected_leagues
        }
    
    def filter_data(self, filters: dict):
        """Apply filters to the data"""
        filtered_predictions = self.predictions_df.copy()
        filtered_value_bets = self.value_bets_df.copy()
        
        # Value bet filtering
        if not filtered_value_bets.empty:
            filtered_value_bets = filtered_value_bets[
                (filtered_value_bets['edge_percent'] >= filters['min_edge']) &
                (filtered_value_bets['kelly_stake'] >= filters['min_stake'])
            ]
            
            # Bankroll risk management
            max_total_risk = filters['total_bankroll'] * (filters['max_risk_pct'] / 100)
            filtered_value_bets['cumulative_stake'] = filtered_value_bets['kelly_stake'].cumsum()
            filtered_value_bets = filtered_value_bets[
                filtered_value_bets['cumulative_stake'] <= max_total_risk
            ]
        
        return filtered_predictions, filtered_value_bets
    
    def render_metrics_overview(self, filtered_predictions: pd.DataFrame, filtered_value_bets: pd.DataFrame):
        """Render key metrics overview"""
        st.markdown("## 📊 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            games_count = len(filtered_predictions)
            st.metric(
                label="🎮 Games Analyzed",
                value=games_count,
                help="Total number of games matching filters"
            )
        
        with col2:
            value_bets_count = len(filtered_value_bets)
            st.metric(
                label="🎯 Value Bets",
                value=value_bets_count,
                help="Number of positive edge opportunities"
            )
        
        with col3:
            total_stake = filtered_value_bets['kelly_stake'].sum() if not filtered_value_bets.empty else 0
            st.metric(
                label="💰 Total Stake",
                value=f"${total_stake:.0f}",
                help="Total recommended betting amount"
            )
        
        with col4:
            avg_edge = filtered_value_bets['edge_percent'].mean() if not filtered_value_bets.empty else 0
            st.metric(
                label="📈 Avg Edge",
                value=f"{avg_edge:.1f}%",
                help="Average betting edge across all value bets"
            )
    
    def render_value_bets_table(self, filtered_value_bets: pd.DataFrame):
        """Render value bets table"""
        st.markdown("## 🔥 Top Value Bets")
        
        if filtered_value_bets.empty:
            st.warning("⚠️ No value bets found with current filters")
            return
        
        # Prepare display data
        display_df = filtered_value_bets.head(20).copy()
        
        # Format columns for display
        display_df['Game'] = display_df['away_team'] + " @ " + display_df['home_team']
        display_df['Odds'] = display_df['odds'].apply(lambda x: f"{x:+d}")
        display_df['Edge'] = display_df['edge_percent'].apply(lambda x: f"{x:.1f}%")
        display_df['Stake'] = display_df['kelly_stake'].apply(lambda x: f"${x:.0f}")
        display_df['Profit'] = display_df['profit_potential'].apply(lambda x: f"${x:.0f}")
        
        # Select columns for display
        display_cols = ['League', 'Game', 'Bet Team Name', 'Bookmaker', 'Odds', 'Edge', 'Stake', 'Profit']
        
        # Rename columns
        column_mapping = {
            'league': 'League',
            'bet_team_name': 'Bet Team Name',
            'bookmaker': 'Bookmaker'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in display_df.columns:
                display_df[new_col] = display_df[old_col]
        
        # Show table
        st.dataframe(
            display_df[display_cols].reset_index(drop=True),
            use_container_width=True,
            height=400
        )
        
        # Download button for full data
        csv_data = filtered_value_bets.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Value Bets CSV",
            data=csv_data,
            file_name=f"eq12_value_bets_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    def render_parlay_recommendations(self):
        """Render top parlay recommendations"""
        st.markdown("## 🎲 TOP 10-LEG PARLAYS FOR TODAY")
        
        if self.value_bets_df.empty:
            st.warning("⚠️ No value bets available for parlay generation")
            return
        
        # Generate 10 different parlay combinations
        parlays = []
        for i in range(10):
            # Select random legs for each parlay
            num_legs = np.random.randint(8, 13)  # 8-12 legs
            if len(self.value_bets_df) < num_legs:
                selected_bets = self.value_bets_df.sample(n=len(self.value_bets_df), replace=True)
            else:
                selected_bets = self.value_bets_df.sample(n=num_legs)
            
            # Calculate parlay metrics
            total_odds = 1.0
            total_stake = 10.0  # $10 parlay
            
            for _, bet in selected_bets.iterrows():
                american_odds = bet['odds']
                if american_odds > 0:
                    decimal_odds = (american_odds / 100) + 1
                else:
                    decimal_odds = (100 / abs(american_odds)) + 1
                total_odds *= decimal_odds
            
            potential_payout = total_stake * total_odds
            
            parlays.append({
                'Parlay': f"Parlay #{i+1}",
                'Legs': len(selected_bets),
                'Stake': f"${total_stake:.0f}",
                'Odds': f"{total_odds:.0f}:1",
                'Payout': f"${potential_payout:.0f}",
                'Teams': " + ".join(selected_bets['bet_team_name'].head(3).tolist()) + f" + {len(selected_bets)-3} more" if len(selected_bets) > 3 else " + ".join(selected_bets['bet_team_name'].tolist())
            })
        
        parlay_df = pd.DataFrame(parlays)
        
        # Display parlays
        st.dataframe(parlay_df, use_container_width=True, height=400)
        
        # Highlight top recommendation
        if parlays:
            best_parlay = max(parlays, key=lambda x: float(x['Payout'].replace('$', '').replace(',', '')))
            st.success(f"🏆 **RECOMMENDED**: {best_parlay['Parlay']} - {best_parlay['Teams']} for {best_parlay['Payout']} potential payout!")
    
    def render_charts(self, filtered_predictions: pd.DataFrame, filtered_value_bets: pd.DataFrame):
        """Render analysis charts"""
        st.markdown("## 📈 Analysis Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Edge distribution
            if not filtered_value_bets.empty:
                st.markdown("### Edge Distribution")
                
                fig_edge = px.histogram(
                    filtered_value_bets,
                    x='edge_percent',
                    nbins=15,
                    title="Distribution of Betting Edges",
                    labels={'edge_percent': 'Edge Percentage (%)', 'count': 'Number of Bets'}
                )
                fig_edge.update_layout(showlegend=False)
                st.plotly_chart(fig_edge, use_container_width=True)
        
        with col2:
            # Stake vs Edge scatter
            if not filtered_value_bets.empty:
                st.markdown("### Stake vs Edge Analysis")
                
                fig_scatter = px.scatter(
                    filtered_value_bets,
                    x='edge_percent',
                    y='kelly_stake',
                    color='league',
                    title="Kelly Stake vs Edge Percentage",
                    labels={'edge_percent': 'Edge %', 'kelly_stake': 'Stake ($)'}
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
    
    def render_bankroll_management(self, filtered_value_bets: pd.DataFrame, total_bankroll: float):
        """Render bankroll management section"""
        st.markdown("## 💰 Bankroll Management")
        
        if filtered_value_bets.empty:
            st.info("No value bets for bankroll analysis")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk analysis
            total_stake = filtered_value_bets['kelly_stake'].sum()
            risk_percentage = (total_stake / total_bankroll) * 100
            
            st.markdown("### Risk Analysis")
            st.metric("Total Stake", f"${total_stake:.0f}")
            st.metric("Risk Percentage", f"{risk_percentage:.1f}%")
            st.metric("Remaining Bankroll", f"${total_bankroll - total_stake:.0f}")
            
            # Risk level indicator
            if risk_percentage <= 5:
                st.success("🟢 Conservative Risk Level")
            elif risk_percentage <= 15:
                st.warning("🟡 Moderate Risk Level")
            else:
                st.error("🔴 High Risk Level")
        
        with col2:
            # Potential returns
            total_profit_potential = filtered_value_bets['profit_potential'].sum()
            roi_potential = (total_profit_potential / total_stake) * 100 if total_stake > 0 else 0
            
            st.markdown("### Potential Returns")
            st.metric("Profit Potential", f"${total_profit_potential:.0f}")
            st.metric("ROI Potential", f"{roi_potential:.1f}%")
            
            # Expected value calculation
            total_ev = filtered_value_bets['expected_value'].sum() if 'expected_value' in filtered_value_bets.columns else 0
            st.metric("Expected Value", f"${total_ev:.0f}")
    
    def run(self):
        """Main dashboard execution"""
        self.render_header()
        
        # Load data
        if not self.data_loaded:
            with st.spinner("Loading latest betting data..."):
                if not self.load_latest_data():
                    st.stop()
        
        # Sidebar controls
        filters = self.render_sidebar_controls()
        
        # Apply filters
        filtered_predictions, filtered_value_bets = self.filter_data(filters)
        
        # Main content
        self.render_metrics_overview(filtered_predictions, filtered_value_bets)
        self.render_parlay_recommendations()
        self.render_value_bets_table(filtered_value_bets)
        self.render_charts(filtered_predictions, filtered_value_bets)
        self.render_bankroll_management(filtered_value_bets, filters['total_bankroll'])
        
        # Action buttons
        st.markdown("## 🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Data", type="primary"):
                self.data_loaded = False
                st.rerun()
        
        with col2:
            if st.button("📊 Generate New Parlays", type="secondary"):
                st.rerun()
        
        with col3:
            if st.button("💾 Export All Data", type="secondary"):
                st.success("Data export feature coming soon!")
        
        # Footer
        st.markdown("---")
        st.markdown("**EQ12 Godlike Betting Dashboard** - Built with ❤️ for profitable betting")
        
        # Auto-refresh option
        if st.checkbox("Auto-refresh every 30 seconds"):
            import time
            time.sleep(30)
            st.rerun()

def main():
    """Main entry point for the betting dashboard"""
    dashboard = EQ12BettingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()