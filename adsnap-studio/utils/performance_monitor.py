import time
import psutil
import streamlit as st
from contextlib import contextmanager
from typing import Dict, List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

class PerformanceMonitor:
    """Monitor and visualize application performance."""
    
    def __init__(self):
        if 'performance_data' not in st.session_state:
            st.session_state.performance_data = []
        if 'api_calls' not in st.session_state:
            st.session_state.api_calls = []
    
    @contextmanager
    def monitor_operation(self, operation_name: str):
        """Context manager to monitor operation performance."""
        start_time = time.time()
        start_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
            
            duration = end_time - start_time
            memory_change = end_memory - start_memory
            
            # Store performance data
            st.session_state.performance_data.append({
                'operation': operation_name,
                'duration': duration,
                'memory_change': memory_change,
                'timestamp': datetime.now()
            })
    
    def log_api_call(self, service: str, duration: float, status: str, error: str = None):
        """Log API call performance."""
        st.session_state.api_calls.append({
            'service': service,
            'duration': duration,
            'status': status,
            'error': error,
            'timestamp': datetime.now()
        })
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary statistics."""
        if not st.session_state.performance_data:
            return {}
        
        df = pd.DataFrame(st.session_state.performance_data)
        return {
            'total_operations': len(df),
            'avg_duration': df['duration'].mean(),
            'max_duration': df['duration'].max(),
            'total_memory_change': df['memory_change'].sum(),
            'operations_per_minute': len(df) / max(1, (datetime.now() - df['timestamp'].min()).total_seconds() / 60)
        }
    
    def create_performance_dashboard(self):
        """Create performance visualization dashboard."""
        if not st.session_state.performance_data and not st.session_state.api_calls:
            st.info("No performance data available yet. Start using the application to see metrics.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Operation Performance")
            if st.session_state.performance_data:
                df_perf = pd.DataFrame(st.session_state.performance_data)
                
                # Duration chart
                fig_duration = px.bar(
                    df_perf.groupby('operation')['duration'].mean().reset_index(),
                    x='operation', y='duration',
                    title="Average Operation Duration (seconds)",
                    color='duration',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_duration, use_container_width=True)
                
                # Memory usage chart
                fig_memory = px.scatter(
                    df_perf, x='timestamp', y='memory_change',
                    color='operation', title="Memory Usage Over Time (MB)",
                    hover_data=['duration']
                )
                st.plotly_chart(fig_memory, use_container_width=True)
        
        with col2:
            st.subheader("🌐 API Performance")
            if st.session_state.api_calls:
                df_api = pd.DataFrame(st.session_state.api_calls)
                
                # API success rate
                success_rate = (df_api['status'] == 'success').mean() * 100
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = success_rate,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "API Success Rate (%)"},
                    delta = {'reference': 100},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # API call duration by service
                fig_api_duration = px.box(
                    df_api, x='service', y='duration',
                    title="API Call Duration by Service (seconds)"
                )
                st.plotly_chart(fig_api_duration, use_container_width=True)
        
        # Performance summary metrics
        st.subheader("📈 Performance Summary")
        summary = self.get_performance_summary()
        if summary:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Operations", summary['total_operations'])
            with col2:
                st.metric("Avg Duration", f"{summary['avg_duration']:.2f}s")
            with col3:
                st.metric("Max Duration", f"{summary['max_duration']:.2f}s")
            with col4:
                st.metric("Ops/Min", f"{summary['operations_per_minute']:.1f}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()