# 🎨 AdSnap Studio Pro

**AI-Powered Image Generation and Editing Platform**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Bria AI](https://img.shields.io/badge/AI-Bria-orange.svg)](https://bria.ai/)

AdSnap Studio Pro is a comprehensive AI-powered platform for image generation and editing, featuring real-time performance monitoring, advanced analytics, and a professional user interface.

## ✨ Features

### 🖼️ Image Generation & Editing
- **HD Image Generation**: Create high-quality images from text descriptions
- **Background Processing**: Remove, replace, and modify image backgrounds
- **Shadow Effects**: Add realistic shadows to images
- **Lifestyle Shots**: Generate product lifestyle images
- **Generative Fill**: AI-powered image inpainting
- **Element Erasing**: Remove unwanted objects from images
- **Prompt Enhancement**: AI-powered prompt optimization

### 📊 Analytics & Monitoring
- **Real-time Performance Dashboard**: Monitor API calls, response times, and system resources
- **Usage Analytics**: Track feature usage and success rates
- **API Success Rate Monitoring**: Visual gauges and charts
- **Memory Usage Tracking**: System resource monitoring
- **Historical Analysis**: Trends and patterns over time

### 🎯 User Experience
- **Intuitive Navigation**: Clean sidebar with organized features
- **Image Gallery**: History of generated images with metadata
- **One-click Downloads**: Timestamped file downloads
- **Progress Indicators**: Real-time feedback during processing
- **Error Handling**: User-friendly error messages and recovery

### 🔧 Professional Features
- **Structured Logging**: Comprehensive logging system for debugging
- **Input Validation**: File type, size, and parameter validation
- **Session Management**: Persistent history and settings
- **API Management**: Centralized API handling with monitoring
- **Performance Optimization**: Context managers for operation tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Bria AI API Key

### Installation

1. **Clone or extract the project**:
   ```bash
   cd adsnap-studio
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements_improved.txt
   ```

4. **Configure API Key**:
   ```bash
   # Create .env file
   echo "BRIA_API_KEY=your_api_key_here" > .env
   ```

5. **Run the application**:
   ```bash
   streamlit run app_improved.py
   ```

6. **Access the application**:
   Open your browser to `http://localhost:8501`

## 🎯 Usage Guide

### Basic Workflow

1. **Navigate**: Use the sidebar to select a feature
2. **Configure**: Set parameters and upload images as needed
3. **Generate**: Click the generate button and wait for results
4. **Download**: Save your processed images
5. **Monitor**: Check the Analytics page for performance insights

### Feature-Specific Guides

#### 🖼️ HD Image Generation
1. Enter a descriptive text prompt
2. Adjust generation parameters (width, height, steps, guidance)
3. Optional: Use prompt enhancement for better results
4. Click "Generate Image" and wait for results
5. Download or save to gallery

#### 🎭 Background Processing
1. Upload your source image
2. Select background operation (remove, replace, color)
3. Configure parameters
4. Process and download results

#### 📊 Analytics Dashboard
1. Navigate to "Analytics" in the sidebar
2. View real-time performance metrics
3. Analyze usage patterns and success rates
4. Monitor system resource usage

## 🔧 Configuration

### Environment Variables
```bash
# Required
BRIA_API_KEY=your_bria_api_key

# Optional
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB
CACHE_TIMEOUT=3600      # 1 hour
```

### Advanced Configuration
```python
# In app_improved.py, you can modify:
- API timeout settings
- File size limits
- Cache settings
- UI themes and layouts
```

## 📊 Monitoring & Analytics

### Performance Metrics
- **API Response Times**: Track request latency
- **Success Rates**: Monitor API reliability
- **Memory Usage**: System resource consumption
- **Operation Counts**: Feature usage statistics

### Logging
Logs are automatically saved to the `logs/` directory with:
- Structured JSON format
- Timestamp and severity levels
- API call details and performance metrics
- Error tracking and debugging information

### Example Log Entry
```json
{
  "timestamp": "2025-07-18T12:00:00.000Z",
  "level": "INFO",
  "service": "hd_image_generation",
  "duration_ms": 2500,
  "status_code": 200,
  "operation": "generate_image"
}
```

## 🛠️ Development

### Project Structure
```
adsnap-studio/
├── app_improved.py              # Main application (enhanced)
├── app.py                       # Original application
├── requirements_improved.txt    # Enhanced dependencies
├── utils/
│   ├── logger.py               # Logging system
│   └── performance_monitor.py  # Performance tracking
├── services/
│   ├── api_base.py            # Base API service
│   ├── hd_image_generation_improved.py
│   └── ...                     # Other services
├── logs/                       # Application logs
└── README_IMPROVED.md          # This file
```

### Code Quality Standards
- **Type Hints**: All functions use type annotations
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Consistent exception management
- **Logging**: Structured logging throughout
- **Testing**: Unit tests for all components (recommended)

### Adding New Features
1. Create service class inheriting from `BaseAPIService`
2. Add API endpoint and validation logic
3. Integrate with performance monitoring
4. Add UI components in main app
5. Update documentation

## 🔍 Troubleshooting

### Common Issues

#### API Key Not Working
```bash
# Verify API key is set
echo $BRIA_API_KEY

# Check .env file
cat .env

# Restart application after setting key
```

#### Dependencies Issues
```bash
# Update pip
pip install --upgrade pip

# Install specific versions
pip install -r requirements_improved.txt

# Clear cache if needed
pip cache purge
```

#### Performance Issues
1. Check Analytics dashboard for bottlenecks
2. Review logs for error patterns
3. Monitor memory usage
4. Consider reducing image sizes or processing parameters

#### File Upload Issues
- Check file size (max 10MB)
- Verify file format (JPEG, PNG, WebP)
- Ensure stable internet connection

## 📈 Performance Optimization

### Tips for Better Performance
1. **Image Size**: Use optimal dimensions (512x512 is recommended)
2. **Batch Processing**: Process multiple images in sequence
3. **Cache Usage**: Enable caching for repeated operations
4. **Parameter Tuning**: Adjust inference steps vs. quality tradeoffs

### Monitoring Performance
- Use the Analytics dashboard to identify slow operations
- Check API response times in logs
- Monitor memory usage during large operations
- Track success rates to identify problematic features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Bria AI** for providing the AI image generation APIs
- **Streamlit** for the web application framework
- **Contributors** to all open-source libraries used

## 📞 Support

For issues, questions, or feature requests:
1. Check the troubleshooting guide above
2. Review logs in the `logs/` directory
3. Use the Analytics dashboard to identify issues
4. Create an issue with detailed information

---

**Built with ❤️ using Streamlit and Bria AI**