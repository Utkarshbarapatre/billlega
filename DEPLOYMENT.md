# Railway Deployment Guide

## 🚀 Quick Deploy

Your Legal Billing Email Summarizer is ready for Railway deployment!

### Railway Domain
- **URL**: `https://gracious-celebration.railway.internal`
- **API**: `https://gracious-celebration.railway.internal/api`
- **Health Check**: `https://gracious-celebration.railway.internal/health`

## 📋 Pre-Deployment Checklist

### 1. Environment Variables (Set in Railway Dashboard)

\`\`\`bash
OPENAI_API_KEY=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
OPENAI_MODEL=gpt-3.5-turbo
CLIO_CLIENT_ID=vYGRnLqjWjlfKpQYA1Cow9U67ZFm5JFnpOst37qW
CLIO_CLIENT_SECRET=ES5vLeDOSrW5VHiAAaIPwxccwaJit6Dt5eXy0A8T
CLIO_REDIRECT_URI=https://gracious-celebration.railway.internal/callback
CLIO_BASE_URL=https://app.clio.com
SECRET_KEY=-oU9X3RQYFs2xx68UDTnAmcxqE-ZhJOBetRYumTol8Q
DEBUG=false
PORT=8000
DATABASE_URL=sqlite:///./legal_billing.db
\`\`\`

### 2. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select your project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `https://gracious-celebration.railway.internal/callback`
   - `http://localhost:8000/callback` (for local testing)
6. Download `client_secret.json`

### 3. Clio OAuth Setup

1. Go to [Clio Developer Portal](https://developers.clio.com/)
2. Create/update your app
3. Set redirect URI: `https://gracious-celebration.railway.internal/callback`
4. Note your Client ID and Secret (already in env vars above)

## 🚀 Deployment Steps

### Step 1: Push to GitHub
\`\`\`bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
\`\`\`

### Step 2: Railway Setup
1. Go to [Railway](https://railway.app)
2. Create new project from GitHub repo
3. Select your repository
4. Railway will auto-detect Python and use `railway.toml`

### Step 3: Configure Environment Variables
In Railway dashboard, add all environment variables from above.

### Step 4: Upload Google Credentials
Upload your `client_secret.json` file to the Railway project.

### Step 5: Deploy
Railway will automatically deploy when you push to main branch.

## 🔍 Post-Deployment Testing

### 1. Health Check
\`\`\`bash
curl https://gracious-celebration.railway.internal/health
\`\`\`

### 2. API Status
\`\`\`bash
curl https://gracious-celebration.railway.internal/api/status
\`\`\`

### 3. Test Endpoints
- Gmail Auth: `POST /api/gmail/authenticate`
- Clio Auth: `GET /api/clio/auth`
- Extension: `GET /api/extension/status`

## 🐛 Troubleshooting

### Common Issues

1. **Environment Variables Not Set**
   - Check Railway dashboard environment variables
   - Ensure no typos in variable names

2. **Google OAuth Issues**
   - Verify redirect URIs in Google Console
   - Check `client_secret.json` is uploaded

3. **Clio OAuth Issues**
   - Verify redirect URI in Clio Developer Portal
   - Check client ID and secret

4. **Database Issues**
   - Railway provides persistent storage
   - SQLite file will be created automatically

### Logs
View logs in Railway dashboard under "Deployments" tab.

## 📱 Chrome Extension Setup

After deployment, update Chrome extension:

1. Open `chrome://extensions/`
2. Load unpacked extension from `chrome-extension` folder
3. Extension will automatically use Railway domain
4. Test capture functionality in Gmail

## 🔒 Security Notes

- All API keys are properly configured as environment variables
- OAuth flows use secure HTTPS endpoints
- CORS is configured for production domains
- Debug mode is disabled in production

## 📊 Monitoring

- Health endpoint: `/health`
- Status endpoint: `/api/status`
- Railway provides built-in monitoring and logs

Your application is now ready for production use! 🎉
