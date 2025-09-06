# ACNE - Agentic Conversational No-Code Environment

Deploy GitHub repositories through simple conversation. No coding knowledge required.

## 🚀 Live Demo
**Deployed Application**: [ACNE on Hugging Face Spaces](https://huggingface.co/spaces/JmDrumsGarrison/ACNE)

## 📋 Project Overview
ACNE transforms software deployment from a complex technical process into a simple conversation. Business users can deploy applications by describing what they want in plain English.

### Key Features
- 🔍 **Smart Repository Analysis** - Auto-detects tech stacks and dependencies
- 💰 **Cost Estimation** - Calculate hosting requirements and monthly costs  
- 🚀 **One-Click Deployment** - Deploy through simple conversation
- 📊 **Real-Time Progress** - Track deployment status live
- 🌐 **Instant URLs** - Get shareable application links immediately

## 🏗️ Architecture
- **Backend**: FastAPI with async support
- **Frontend**: Custom HTML/CSS/JavaScript
- **Deployment**: Docker containers on Hugging Face Spaces
- **Analysis**: GitHub API integration

## 📁 Project Structure
```
ACNE-Project/
├── app.py              # Main FastAPI application
├── analyzer.py         # GitHub repository analyzer
├── conversation.py     # Conversation management
├── frontend.html       # Web interface
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container configuration
└── README.md          # This file
```

## 🚀 Current Status
- ✅ **Deployed**: Live on Hugging Face Spaces
- ✅ **Analysis**: Repository detection working
- ✅ **Interface**: Conversational UI functional
- 🔄 **Deployment**: Working on real HF Space creation

## 🎯 Next Steps
1. Implement actual Hugging Face Spaces API integration
2. Add more deployment targets (Vercel, Netlify, etc.)
3. Enhanced cost estimation algorithms
4. Support for private repositories

## 💻 Development
```bash
# Clone repository
git clone <this-repo-url>

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

## 🤝 Contributing
This project is actively developed. See commit history for latest updates.

## 📄 License
MIT License - See LICENSE file for details

---
*Built with ❤️ for making deployment accessible to everyone*
