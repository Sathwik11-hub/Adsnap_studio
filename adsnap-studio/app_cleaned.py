import streamlit as st
import os
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
import time
import base64
from streamlit_drawable_canvas import st_canvas
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="AdSnap Studio Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize session state variables."""
    defaults = {
        'api_key': os.getenv('BRIA_API_KEY'),
        'generated_images': [],
        'current_image': None,
        'pending_urls': [],
        'edited_image': None,
        'original_prompt': "",
        'enhanced_prompt': None,
        'generation_history': [],
        'performance_metrics': {
            'total_generations': 0,
            'successful_generations': 0,
            'average_generation_time': 0,
            'error_count': 0
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def log_generation_attempt(operation_type: str, success: bool, duration: float = None, error: str = None):
    """Log generation attempts for performance tracking."""
    timestamp = datetime.now()
    
    # Update performance metrics
    st.session_state.performance_metrics['total_generations'] += 1
    if success:
        st.session_state.performance_metrics['successful_generations'] += 1
        if duration:
            current_avg = st.session_state.performance_metrics['average_generation_time']
            total_successful = st.session_state.performance_metrics['successful_generations']
            new_avg = ((current_avg * (total_successful - 1)) + duration) / total_successful
            st.session_state.performance_metrics['average_generation_time'] = new_avg
    else:
        st.session_state.performance_metrics['error_count'] += 1
    
    # Add to history
    history_entry = {
        'timestamp': timestamp,
        'operation': operation_type,
        'success': success,
        'duration': duration,
        'error': error
    }
    
    st.session_state.generation_history.append(history_entry)
    
    # Keep only last 100 entries
    if len(st.session_state.generation_history) > 100:
        st.session_state.generation_history = st.session_state.generation_history[-100:]

def display_performance_dashboard():
    """Display performance metrics and analytics."""
    st.subheader("📊 Performance Dashboard")
    
    metrics = st.session_state.performance_metrics
    history = st.session_state.generation_history
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Generations", metrics['total_generations'])
    
    with col2:
        success_rate = (metrics['successful_generations'] / max(metrics['total_generations'], 1)) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col3:
        st.metric("Average Time", f"{metrics['average_generation_time']:.1f}s")
    
    with col4:
        st.metric("Errors", metrics['error_count'])
    
    if history:
        # Success rate over time
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.floor('h')
        
        hourly_stats = df.groupby('hour').agg({
            'success': ['count', 'sum'],
            'duration': 'mean'
        }).round(2)
        
        hourly_stats.columns = ['total_attempts', 'successful_attempts', 'avg_duration']
        hourly_stats['success_rate'] = (hourly_stats['successful_attempts'] / hourly_stats['total_attempts']) * 100
        
        if len(hourly_stats) > 1:
            # Success rate chart
            fig_success = px.line(
                hourly_stats.reset_index(), 
                x='hour', 
                y='success_rate',
                title='Success Rate Over Time',
                labels={'success_rate': 'Success Rate (%)', 'hour': 'Time'}
            )
            st.plotly_chart(fig_success, use_container_width=True)
            
            # Duration chart
            if hourly_stats['avg_duration'].notna().any():
                fig_duration = px.bar(
                    hourly_stats.reset_index(), 
                    x='hour', 
                    y='avg_duration',
                    title='Average Generation Time',
                    labels={'avg_duration': 'Duration (seconds)', 'hour': 'Time'}
                )
                st.plotly_chart(fig_duration, use_container_width=True)
        
        # Recent operations table
        st.subheader("Recent Operations")
        recent_ops = df.tail(10)[['timestamp', 'operation', 'success', 'duration', 'error']].copy()
        recent_ops['timestamp'] = recent_ops['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        recent_ops['duration'] = recent_ops['duration'].apply(lambda x: f"{x:.1f}s" if pd.notna(x) else "N/A")
        st.dataframe(recent_ops, use_container_width=True)

def download_image(url):
    """Download image from URL and return as bytes."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        st.error(f"Error downloading image: {str(e)}")
        return None

def safe_api_call(api_function, operation_name, *args, **kwargs):
    """Safely call API functions with error handling and performance tracking."""
    start_time = time.time()
    
    try:
        result = api_function(*args, **kwargs)
        duration = time.time() - start_time
        log_generation_attempt(operation_name, True, duration)
        return result
    except requests.exceptions.RequestException as e:
        duration = time.time() - start_time
        error_msg = f"Network error: {str(e)}"
        log_generation_attempt(operation_name, False, duration, error_msg)
        st.error(f"Network error in {operation_name}: {str(e)}")
        return None
    except ValueError as e:
        duration = time.time() - start_time
        error_msg = f"Invalid input: {str(e)}"
        log_generation_attempt(operation_name, False, duration, error_msg)
        st.error(f"Invalid input for {operation_name}: {str(e)}")
        return None
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Unexpected error: {str(e)}"
        log_generation_attempt(operation_name, False, duration, error_msg)
        st.error(f"Unexpected error in {operation_name}: {str(e)}")
        return None

def main():
    """Main application function."""
    initialize_session_state()
    
    # Sidebar configuration
    with st.sidebar:
        st.title("🎨 AdSnap Studio Pro")
        st.markdown("AI-Powered Image Generation & Editing")
        
        # API Key validation
        if not st.session_state.api_key:
            st.error("⚠️ BRIA API Key not found!")
            st.markdown("Please set your `BRIA_API_KEY` in the `.env` file.")
            st.stop()
        else:
            st.success("✅ API Key loaded")
        
        # Performance toggle
        show_performance = st.checkbox("📊 Show Performance Dashboard", value=False)
        
        if show_performance:
            display_performance_dashboard()
    
    # Main interface
    st.title("🎨 AdSnap Studio Pro")
    st.markdown("Create stunning product advertisements with AI-powered image generation and editing.")
    
    # Create tabs for different features
    tabs = st.tabs([
        "🖼️ HD Generation", 
        "🌅 Lifestyle Shots", 
        "🎨 Generative Fill", 
        "✂️ Erase Elements",
        "🌟 Background Effects"
    ])
    
    # HD Image Generation Tab
    with tabs[0]:
        st.header("🖼️ HD Image Generation")
        st.markdown("Generate high-quality images from text descriptions using advanced AI models.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Prompt input with enhancement
            prompt = st.text_area(
                "Describe your image", 
                value=st.session_state.original_prompt,
                height=100,
                help="Be descriptive and specific for better results"
            )
            
            if prompt != st.session_state.original_prompt:
                st.session_state.original_prompt = prompt
                st.session_state.enhanced_prompt = None
            
            # Prompt enhancement
            col_enhance, col_generate = st.columns([1, 1])
            
            with col_enhance:
                if st.button("✨ Enhance Prompt", disabled=not prompt):
                    result = safe_api_call(
                        enhance_prompt, 
                        "Prompt Enhancement",
                        st.session_state.api_key, 
                        prompt
                    )
                    if result:
                        st.session_state.enhanced_prompt = result
                        st.success("Prompt enhanced!")
                        st.rerun()
            
            # Display enhanced prompt
            if st.session_state.enhanced_prompt:
                st.info(f"Enhanced: {st.session_state.enhanced_prompt}")
                final_prompt = st.session_state.enhanced_prompt
            else:
                final_prompt = prompt
        
        with col2:
            st.subheader("Generation Settings")
            num_images = st.slider("Number of images", 1, 4, 1)
            aspect_ratio = st.selectbox("Aspect ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])
            enhance_img = st.checkbox("Enhance image quality", value=True)
            
            # Advanced settings
            with st.expander("Advanced Settings"):
                model_version = st.selectbox("Model Version", ["2.2", "2.1", "2.0"], index=0)
                negative_prompt = st.text_area("Negative prompt (what to avoid)", height=60)
                seed = st.number_input("Seed (for reproducible results)", value=None, min_value=1)
                steps = st.slider("Steps", 20, 50, 30)
                guidance_scale = st.slider("Text Guidance", 1.0, 10.0, 7.5, 0.5)
        
        # Generate button
        if st.button("🎨 Generate Images", disabled=not final_prompt, use_container_width=True):
            with st.spinner("Generating HD images..."):
                result = safe_api_call(
                    generate_hd_image,
                    "HD Image Generation",
                    final_prompt,
                    st.session_state.api_key,
                    model_version=model_version,
                    num_results=num_images,
                    aspect_ratio=aspect_ratio,
                    negative_prompt=negative_prompt,
                    seed=seed,
                    steps_num=steps,
                    text_guidance_scale=guidance_scale,
                    enhance_image=enhance_img
                )
                
                if result:
                    st.success("✨ Images generated successfully!")
                    if "result_urls" in result:
                        st.session_state.generated_images = result["result_urls"]
                    elif "result_url" in result:
                        st.session_state.generated_images = [result["result_url"]]
        
        # Display generated images
        if st.session_state.generated_images:
            st.subheader("Generated Images")
            cols = st.columns(min(len(st.session_state.generated_images), 4))
            for i, img_url in enumerate(st.session_state.generated_images):
                with cols[i % 4]:
                    st.image(img_url, caption=f"Image {i+1}", use_column_width=True)
                    
                    # Download button
                    img_data = download_image(img_url)
                    if img_data:
                        st.download_button(
                            "⬇️ Download",
                            img_data,
                            f"generated_image_{i+1}.png",
                            "image/png",
                            key=f"download_{i}"
                        )
    
    # Lifestyle Shots Tab
    with tabs[1]:
        st.header("🌅 Lifestyle Shots")
        st.markdown("Transform product images into lifestyle scenes using AI.")
        
        uploaded_file = st.file_uploader(
            "Upload Product Image", 
            type=["png", "jpg", "jpeg"], 
            key="lifestyle_upload"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(uploaded_file, caption="Original Product", use_column_width=True)
                
                # Scene description
                scene_prompt = st.text_area(
                    "Describe the lifestyle scene",
                    height=100,
                    help="E.g., 'Modern kitchen with marble countertops and natural lighting'"
                )
                
                # Settings
                with st.expander("Lifestyle Settings"):
                    placement_type = st.selectbox("Placement", [
                        "Automatic", "Original", "Manual Placement", "Custom Coordinates"
                    ])
                    num_results = st.slider("Number of variations", 1, 8, 4)
                    fast_mode = st.checkbox("Fast mode", True)
                    optimize_desc = st.checkbox("Optimize description", True)
                
                if st.button("🌅 Generate Lifestyle Shot", disabled=not scene_prompt):
                    with st.spinner("Creating lifestyle shot..."):
                        result = safe_api_call(
                            lifestyle_shot_by_text,
                            "Lifestyle Shot Generation",
                            api_key=st.session_state.api_key,
                            image_data=uploaded_file.getvalue(),
                            scene_description=scene_prompt,
                            placement_type=placement_type.lower().replace(" ", "_"),
                            num_results=num_results,
                            fast=fast_mode,
                            optimize_description=optimize_desc
                        )
                        
                        if result and "result_urls" in result:
                            st.session_state.generated_images = result["result_urls"]
                            st.success("✨ Lifestyle shot created!")
            
            with col2:
                if st.session_state.generated_images:
                    st.subheader("Generated Lifestyle Shots")
                    for i, img_url in enumerate(st.session_state.generated_images):
                        st.image(img_url, caption=f"Variation {i+1}", use_column_width=True)
                        
                        img_data = download_image(img_url)
                        if img_data:
                            st.download_button(
                                "⬇️ Download",
                                img_data,
                                f"lifestyle_shot_{i+1}.png",
                                "image/png",
                                key=f"lifestyle_download_{i}"
                            )
    
    # Generative Fill Tab
    with tabs[2]:
        st.header("🎨 Generative Fill")
        st.markdown("Fill selected areas with AI-generated content.")
        
        uploaded_file = st.file_uploader(
            "Upload Image to Edit", 
            type=["png", "jpg", "jpeg"], 
            key="fill_upload"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Display original image and drawing canvas
                img = Image.open(uploaded_file)
                
                # Calculate canvas dimensions
                max_width = 800
                aspect_ratio = img.height / img.width
                canvas_width = min(img.width, max_width)
                canvas_height = int(canvas_width * aspect_ratio)
                
                # Resize and convert image
                img_resized = img.resize((canvas_width, canvas_height))
                if img_resized.mode != 'RGB':
                    img_resized = img_resized.convert('RGB')
                
                # Drawing controls
                stroke_width = st.slider("Brush size", 5, 50, 20)
                
                # Canvas for mask drawing
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 0.7)",
                    stroke_width=stroke_width,
                    stroke_color="#ffffff",
                    background_image=img_resized,
                    drawing_mode="freedraw",
                    height=canvas_height,
                    width=canvas_width,
                    key="fill_canvas",
                )
                
                # Fill prompt
                fill_prompt = st.text_area(
                    "What to generate in the masked area",
                    height=80,
                    help="Describe what should appear in the white-painted areas"
                )
                
                # Generation settings
                with st.expander("Fill Settings"):
                    negative_prompt = st.text_area("Negative prompt", height=60)
                    num_results = st.slider("Number of variations", 1, 4, 2)
                    seed = st.number_input("Seed", value=None, min_value=1)
                
                if st.button("🎨 Fill Area", disabled=not fill_prompt):
                    if canvas_result.image_data is not None:
                        with st.spinner("Generating fill content..."):
                            # Create mask from canvas
                            mask_img = Image.fromarray(
                                canvas_result.image_data.astype('uint8'), 
                                mode='RGBA'
                            )
                            mask_gray = mask_img.convert('L')
                            
                            # Convert to bytes
                            mask_bytes = io.BytesIO()
                            mask_gray.save(mask_bytes, format='PNG')
                            mask_bytes = mask_bytes.getvalue()
                            
                            result = safe_api_call(
                                generative_fill,
                                "Generative Fill",
                                api_key=st.session_state.api_key,
                                image_data=uploaded_file.getvalue(),
                                mask_data=mask_bytes,
                                prompt=fill_prompt,
                                negative_prompt=negative_prompt,
                                num_results=num_results,
                                seed=seed
                            )
                            
                            if result and "result_urls" in result:
                                st.session_state.generated_images = result["result_urls"]
                                st.success("✨ Area filled successfully!")
                    else:
                        st.warning("Please draw on the image to select areas to fill.")
            
            with col2:
                if st.session_state.generated_images:
                    st.subheader("Generated Results")
                    for i, img_url in enumerate(st.session_state.generated_images):
                        st.image(img_url, caption=f"Result {i+1}", use_column_width=True)
                        
                        img_data = download_image(img_url)
                        if img_data:
                            st.download_button(
                                "⬇️ Download",
                                img_data,
                                f"filled_image_{i+1}.png",
                                "image/png",
                                key=f"fill_download_{i}"
                            )

    # Erase Elements Tab
    with tabs[3]:
        st.header("✂️ Erase Elements")
        st.markdown("Remove unwanted objects from your images.")
        
        uploaded_file = st.file_uploader(
            "Upload Image", 
            type=["png", "jpg", "jpeg"], 
            key="erase_upload"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Simple erase button (the service seems to do automatic erasing)
                content_moderation = st.checkbox("Enable Content Moderation", False)
                
                if st.button("✂️ Auto-Erase Elements"):
                    with st.spinner("Erasing elements..."):
                        result = safe_api_call(
                            erase_foreground,
                            "Element Erasing",
                            api_key=st.session_state.api_key,
                            image_data=uploaded_file.getvalue(),
                            content_moderation=content_moderation
                        )
                        
                        if result and "result_url" in result:
                            st.session_state.edited_image = result["result_url"]
                            st.success("✨ Elements erased successfully!")
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Erased Result", use_column_width=True)
                    
                    img_data = download_image(st.session_state.edited_image)
                    if img_data:
                        st.download_button(
                            "⬇️ Download Result",
                            img_data,
                            "erased_image.png",
                            "image/png",
                            key="erase_result_download"
                        )

    # Background Effects Tab
    with tabs[4]:
        st.header("🌟 Background Effects")
        st.markdown("Add professional background effects to your images.")
        
        uploaded_file = st.file_uploader(
            "Upload Image", 
            type=["png", "jpg", "jpeg"], 
            key="bg_upload"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                effect_type = st.selectbox("Background Effect", [
                    "Add Shadow", "Create Packshot"
                ])
                
                if effect_type == "Add Shadow":
                    shadow_intensity = st.slider("Shadow Intensity", 0.1, 1.0, 0.5, 0.1)
                    shadow_blur = st.slider("Shadow Blur", 1, 20, 10)
                    
                    if st.button("🌟 Add Shadow"):
                        with st.spinner("Adding shadow..."):
                            result = safe_api_call(
                                add_shadow,
                                "Shadow Addition",
                                api_key=st.session_state.api_key,
                                image_data=uploaded_file.getvalue()
                            )
                            
                            if result and "result_url" in result:
                                st.session_state.edited_image = result["result_url"]
                                st.success("✨ Shadow added successfully!")
                
                elif effect_type == "Create Packshot":
                    bg_color = st.color_picker("Background Color", "#FFFFFF")
                    
                    if st.button("🌟 Create Packshot"):
                        with st.spinner("Creating packshot..."):
                            result = safe_api_call(
                                create_packshot,
                                "Packshot Creation",
                                api_key=st.session_state.api_key,
                                image_data=uploaded_file.getvalue()
                            )
                            
                            if result and "result_url" in result:
                                st.session_state.edited_image = result["result_url"]
                                st.success("✨ Packshot created successfully!")
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Enhanced Result", use_column_width=True)
                    
                    img_data = download_image(st.session_state.edited_image)
                    if img_data:
                        st.download_button(
                            "⬇️ Download Result",
                            img_data,
                            "enhanced_image.png",
                            "image/png",
                            key="bg_result_download"
                        )

if __name__ == "__main__":
    main()