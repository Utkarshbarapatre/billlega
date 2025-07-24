# Legal Billing Email Summarizer

Automatically fetch Gmail emails, generate AI-powered summaries for legal billing, and sync with Clio practice management software.

## 🚀 Features

- **📧 Gmail Integration** - Automatically fetch sent emails using Gmail API
- **🤖 AI Summarization** - Generate professional billing summaries using OpenAI GPT
- **⚖️ Clio Integration** - Push time entries directly to Clio practice management
- **🌐 Modern Web UI** - Clean, responsive interface with real-time updates
- **🔌 Chrome Extension** - Capture emails directly from Gmail interface
- **📊 Bulk Operations** - Process multiple emails with filtering and search
- **🔐 OAuth Security** - Secure authentication for Gmail and Clio APIs

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, FastAPI, SQLAlchemy, Uvicorn
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Database**: SQLite (production: PostgreSQL)
- **APIs**: OpenAI GPT-3.5/4, Gmail API, Clio API v4
- **Authentication**: OAuth 2.0 (Google, Clio)
- **Extension**: Chrome Extension Manifest V3
- **Deployment**: Railway

## 🚀 Quick Start

### 1. Clone and Setup

\`\`\`bash
git clone <your-repo>
cd legal-billing-summarizer
\`\`\`

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

\`\`\`bash
cp .env.example .env
\`\`\`

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `CLIO_CLIENT_ID` - Clio OAuth client ID
- `CLIO_CLIENT_SECRET` - Clio OAuth client secret
- `CLIO_REDIRECT_URI` - Your app's callback URL

### 3. Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `client_secret.json` to project root

### 4. Deploy to Railway

1. Connect your GitHub repo to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

## 📱 Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `chrome-extension` folder
4. Pin the extension to your toolbar

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /api/gmail/authenticate` - Authenticate Gmail
- `GET /api/gmail/emails` - Fetch emails
- `POST /api/summarizer/generate` - Generate summaries
- `POST /api/clio/push-entries` - Push to Clio

## 📄 License

MIT License - see LICENSE file for details.
