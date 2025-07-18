import streamlit as st
import os
import time
from dotenv import load_dotenv
from services import (
    lifestyle_shot_by_image,
    lifestyle_shot_by_text,
    add_shadow,
    create_packshot,
    enhance_prompt,
    generative_fill,
    generate_hd_image,
    erase_foreground
)
from PIL import Image
import io
import requests
import json
import base64
from streamlit_drawable_canvas import st_canvas
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import traceback

# Import custom utilities
from utils.logger import AdSnapLogger
from utils.performance_monitor import performance_monitor

# Configure Streamlit page
st.set_page_config(
    page_title="AdSnap Studio Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = AdSnapLogger("adsnap_studio")

# Load environment variables
load_dotenv()

class APIManager:
    """Centralized API management with monitoring."""
    
    def __init__(self):
        self.api_key = os.getenv('BRIA_API_KEY')
        if not self.api_key:
            logger.error("BRIA_API_KEY not found in environment variables")
            st.error("⚠️ API Key not configured. Please set BRIA_API_KEY in your .env file.")
    
    def make_api_call(self, service_name: str, api_function, *args, **kwargs):
        """Make API call with monitoring and error handling."""
        start_time = time.time()
        
        try:
            with performance_monitor.monitor_operation(f"API_{service_name}"):
                result = api_function(*args, **kwargs)
            
            duration = time.time() - start_time
            performance_monitor.log_api_call(service_name, duration, "success")
            logger.log_api_call(service_name, "api_call", duration, 200)
            
            return result, None
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            performance_monitor.log_api_call(service_name, duration, "error", error_msg)
            logger.log_api_call(service_name, "api_call", duration, 500, error_msg)
            logger.error(f"API call failed for {service_name}: {error_msg}")
            
            return None, error_msg

# Global API manager
api_manager = APIManager()

def initialize_session_state():
    """Initialize session state variables."""
    defaults = {
        'api_key': os.getenv('BRIA_API_KEY'),
        'generated_images': [],
        'processing_history': [],
        'usage_stats': {'total_calls': 0, 'successful_calls': 0, 'failed_calls': 0}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def validate_image(image_file) -> tuple[bool, str]:
    """Validate uploaded image file."""
    if image_file is None:
        return False, "No image file provided"
    
    # Check file size (max 10MB)
    if image_file.size > 10 * 1024 * 1024:
        return False, "Image file too large (max 10MB)"
    
    # Check file type
    valid_types = ['image/jpeg', 'image/png', 'image/webp']
    if image_file.type not in valid_types:
        return False, f"Invalid file type. Supported: {', '.join(valid_types)}"
    
    return True, "Valid image"

def display_image_with_download(image_data, title: str, key_suffix: str = ""):
    """Display image with download button."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.image(image_data, caption=title, use_column_width=True)
    
    with col2:
        if isinstance(image_data, Image.Image):
            # Convert PIL Image to bytes
            img_buffer = io.BytesIO()
            image_data.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()
        else:
            img_bytes = image_data
        
        st.download_button(
            label="📥 Download",
            data=img_bytes,
            file_name=f"{title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png",
            key=f"download_{key_suffix}"
        )

def create_sidebar():
    """Create sidebar with navigation and settings."""
    with st.sidebar:
        st.title("🎨 AdSnap Studio Pro")
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["🏠 Home", "🖼️ HD Image Generation", "🎭 Background Processing", 
             "👤 Shadow Effects", "🏖️ Lifestyle Shots", "🎨 Generative Fill", 
             "🗑️ Element Erasing", "📊 Analytics", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        # API Status
        st.subheader("📡 API Status")
        if st.session_state.api_key:
            st.success("✅ API Key Configured")
        else:
            st.error("❌ API Key Missing")
            
        # Usage Stats
        stats = st.session_state.usage_stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Calls", stats['total_calls'])
        with col2:
            success_rate = (stats['successful_calls'] / max(1, stats['total_calls'])) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        if st.button("🔄 Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
        
        if st.button("📊 Refresh Analytics"):
            st.rerun()
    
    return page

def home_page():
    """Display home page with overview and recent activity."""
    st.title("🎨 AdSnap Studio Pro")
    st.markdown("### AI-Powered Image Generation and Editing Platform")
    
    # Feature overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🖼️ Image Generation
        - HD Image Creation
        - Text-to-Image AI
        - Custom Prompts
        """)
    
    with col2:
        st.markdown("""
        #### 🎭 Image Processing
        - Background Removal
        - Shadow Effects
        - Color Replacement
        """)
    
    with col3:
        st.markdown("""
        #### 🎨 Advanced Editing
        - Generative Fill
        - Element Erasing
        - Lifestyle Shots
        """)
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    if st.session_state.processing_history:
        df = pd.DataFrame(st.session_state.processing_history[-10:])  # Last 10 operations
        
        fig = px.timeline(
            df, x_start="timestamp", x_end="timestamp", 
            y="operation", color="status",
            title="Recent Operations Timeline"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No recent activity. Start using the tools to see your history!")
    
    # Quick start guide
    with st.expander("🚀 Quick Start Guide"):
        st.markdown("""
        1. **Configure API**: Make sure your BRIA_API_KEY is set in the .env file
        2. **Choose a Tool**: Select from the sidebar navigation
        3. **Upload Image**: Most tools require an input image
        4. **Configure Settings**: Adjust parameters as needed
        5. **Generate**: Click the generate button and wait for results
        6. **Download**: Save your processed images
        """)

def hd_image_generation_page():
    """HD Image Generation page with enhanced features."""
    st.title("🖼️ HD Image Generation")
    st.markdown("Generate high-quality images from text descriptions using AI.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎯 Generation Settings")
        
        # Basic settings
        prompt = st.text_area(
            "Text Prompt",
            placeholder="Describe the image you want to generate...",
            height=100
        )
        
        # Advanced settings
        with st.expander("⚙️ Advanced Settings"):
            width = st.slider("Width", 256, 1024, 512, 64)
            height = st.slider("Height", 256, 1024, 512, 64)
            num_inference_steps = st.slider("Inference Steps", 10, 50, 20)
            guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5, 0.5)
        
        # Prompt enhancement
        if st.button("✨ Enhance Prompt"):
            if prompt:
                with st.spinner("Enhancing prompt..."):
                    result, error = api_manager.make_api_call("prompt_enhancement", enhance_prompt, prompt)
                    if result and not error:
                        enhanced_prompt = result.get('result', prompt)
                        st.session_state.enhanced_prompt = enhanced_prompt
                        st.success("Prompt enhanced!")
                    else:
                        st.error(f"Enhancement failed: {error}")
        
        if 'enhanced_prompt' in st.session_state:
            st.text_area("Enhanced Prompt", st.session_state.enhanced_prompt, height=80)
        
        # Generate button
        if st.button("🎨 Generate Image", type="primary"):
            if not prompt:
                st.error("Please enter a prompt")
                return
            
            final_prompt = st.session_state.get('enhanced_prompt', prompt)
            
            with st.spinner("Generating image..."):
                result, error = api_manager.make_api_call(
                    "hd_image_generation",
                    generate_hd_image,
                    final_prompt, width, height, num_inference_steps, guidance_scale
                )
                
                if result and not error:
                    st.session_state.generated_images.append({
                        'image': result,
                        'prompt': final_prompt,
                        'timestamp': datetime.now(),
                        'settings': {'width': width, 'height': height, 'steps': num_inference_steps, 'guidance': guidance_scale}
                    })
                    
                    # Update processing history
                    st.session_state.processing_history.append({
                        'operation': 'HD Image Generation',
                        'timestamp': datetime.now(),
                        'status': 'Success'
                    })
                    
                    st.success("Image generated successfully!")
                    st.rerun()
                else:
                    st.error(f"Generation failed: {error}")
                    # Update processing history
                    st.session_state.processing_history.append({
                        'operation': 'HD Image Generation',
                        'timestamp': datetime.now(),
                        'status': 'Failed'
                    })
    
    with col2:
        st.subheader("🖼️ Generated Images")
        
        if st.session_state.generated_images:
            # Display latest image
            latest = st.session_state.generated_images[-1]
            display_image_with_download(
                latest['image'], 
                f"Generated: {latest['prompt'][:50]}...",
                "latest_generated"
            )
            
            # Image gallery
            if len(st.session_state.generated_images) > 1:
                with st.expander("📚 Image Gallery"):
                    for i, img_data in enumerate(reversed(st.session_state.generated_images[:-1])):
                        st.image(img_data['image'], caption=f"Prompt: {img_data['prompt'][:100]}...")
                        
        else:
            st.info("No images generated yet. Use the settings on the left to create your first image!")

def analytics_page():
    """Analytics and performance monitoring page."""
    st.title("📊 Analytics & Performance")
    st.markdown("Monitor application performance and usage patterns.")
    
    # Performance dashboard
    performance_monitor.create_performance_dashboard()
    
    # Usage analytics
    st.subheader("📈 Usage Analytics")
    
    if st.session_state.processing_history:
        df_history = pd.DataFrame(st.session_state.processing_history)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Operations count by type
            ops_count = df_history['operation'].value_counts()
            fig_ops = px.pie(
                values=ops_count.values, 
                names=ops_count.index,
                title="Operations Distribution"
            )
            st.plotly_chart(fig_ops, use_container_width=True)
        
        with col2:
            # Success rate by operation
            success_rate = df_history.groupby('operation')['status'].apply(
                lambda x: (x == 'Success').mean() * 100
            ).reset_index()
            success_rate.columns = ['operation', 'success_rate']
            
            fig_success = px.bar(
                success_rate, x='operation', y='success_rate',
                title="Success Rate by Operation (%)",
                color='success_rate',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_success, use_container_width=True)
        
        # Timeline of operations
        df_history['date'] = pd.to_datetime(df_history['timestamp']).dt.date
        daily_ops = df_history.groupby(['date', 'operation']).size().reset_index(name='count')
        
        fig_timeline = px.line(
            daily_ops, x='date', y='count', color='operation',
            title="Operations Over Time"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    else:
        st.info("No usage data available yet. Start using the application to see analytics.")

def main():
    """Main application entry point."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Create sidebar and get selected page
        page = create_sidebar()
        
        # Route to appropriate page
        if page == "🏠 Home":
            home_page()
        elif page == "🖼️ HD Image Generation":
            hd_image_generation_page()
        elif page == "📊 Analytics":
            analytics_page()
        # Add other pages here...
        else:
            st.info(f"Page '{page}' is under construction. Please check back later!")
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: gray;'>"
            "AdSnap Studio Pro - Powered by Bria AI | "
            f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            "</div>",
            unsafe_allow_html=True
        )
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        logger.error(traceback.format_exc())
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error("Please check the logs for more details.")

if __name__ == "__main__":
    main()