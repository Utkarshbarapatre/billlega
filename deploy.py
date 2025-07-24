#!/usr/bin/env python3
"""
Deployment script for Railway
"""
import os
import sys
import subprocess
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "CLIO_CLIENT_ID", 
        "CLIO_CLIENT_SECRET",
    ]
    
    missing_vars = []
    found_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            found_vars.append(var)
            # Show partial value for verification (first 10 chars + ...)
            display_value = value[:10] + "..." if len(value) > 10 else value
            logger.info(f"✅ {var}: {display_value}")
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("💡 Make sure your .env file exists and contains all required variables")
        return False
    
    logger.info(f"✅ All {len(found_vars)} required environment variables are set")
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        "requirements.txt",
        "railway.toml", 
        "backend/main.py",
        ".env"
    ]
    
    optional_files = [
        "client_secret.json"
    ]
    
    missing_files = []
    found_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            found_files.append(file)
            logger.info(f"✅ Found: {file}")
    
    # Check optional files
    for file in optional_files:
        if os.path.exists(file):
            logger.info(f"✅ Found (optional): {file}")
        else:
            logger.warning(f"⚠️  Missing (optional): {file} - You'll need to upload this to Railway")
    
    if missing_files:
        logger.error(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    logger.info(f"✅ All {len(found_files)} required files are present")
    return True

def check_python_packages():
    """Check if required Python packages can be imported"""
    required_packages = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "python-dotenv",
        "openai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"✅ Package available: {package}")
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"⚠️  Missing packages (install with pip): {', '.join(missing_packages)}")
        logger.info("Run: pip install -r requirements.txt")
        return False
    
    return True

def show_env_file_status():
    """Show .env file status and contents (safely)"""
    if os.path.exists('.env'):
        logger.info("✅ .env file found")
        try:
            with open('.env', 'r') as f:
                lines = f.readlines()
            
            logger.info(f"📄 .env file contains {len(lines)} lines:")
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Show key and partial value for verification
                        display_value = value[:10] + "..." if len(value) > 10 else value
                        logger.info(f"   {key}={display_value}")
                    else:
                        logger.info(f"   {line}")
        except Exception as e:
            logger.error(f"❌ Error reading .env file: {e}")
    else:
        logger.error("❌ .env file not found!")
        logger.info("💡 Create a .env file with your environment variables")

def main():
    """Main deployment function"""
    logger.info("🚀 Starting Legal Billing Email Summarizer deployment checks...")
    logger.info("="*60)
    
    # Show .env file status first
    show_env_file_status()
    logger.info("-"*60)
    
    # Check environment variables
    env_check = check_environment()
    logger.info("-"*60)
    
    # Check files
    files_check = check_files()
    logger.info("-"*60)
    
    # Check Python packages
    packages_check = check_python_packages()
    logger.info("-"*60)
    
    # Overall status
    if env_check and files_check:
        logger.info("✅ All deployment checks passed!")
        logger.info("🚀 Ready for Railway deployment")
        
        # Print deployment instructions
        print("\n" + "="*60)
        print("🚂 RAILWAY DEPLOYMENT INSTRUCTIONS")
        print("="*60)
        print("1. 📤 Push your code to GitHub:")
        print("   git add .")
        print("   git commit -m 'Ready for Railway deployment'")
        print("   git push origin main")
        print()
        print("2. 🔗 Connect your GitHub repo to Railway")
        print("3. ⚙️  Set environment variables in Railway dashboard:")
        
        # Show the actual values from .env for Railway setup
        env_vars_for_railway = [
            "OPENAI_API_KEY",
            "OPENAI_MODEL", 
            "CLIO_CLIENT_ID",
            "CLIO_CLIENT_SECRET",
            "CLIO_REDIRECT_URI",
            "CLIO_BASE_URL",
            "SECRET_KEY",
            "DEBUG",
            "PORT",
            "DATABASE_URL"
        ]
        
        for var in env_vars_for_railway:
            value = os.getenv(var)
            if value:
                print(f"   {var}={value}")
        
        print()
        print("4. 📁 Upload your client_secret.json file to Railway")
        print("5. 🚀 Deploy!")
        print("="*60)
        print()
        print("🌐 Your app will be available at:")
        print("   https://gracious-celebration.railway.internal")
        print()
        
    else:
        logger.error("❌ Deployment checks failed!")
        if not env_check:
            logger.error("   - Fix environment variables in .env file")
        if not files_check:
            logger.error("   - Add missing required files")
        if not packages_check:
            logger.error("   - Install missing Python packages")
        sys.exit(1)

if __name__ == "__main__":
    main()
