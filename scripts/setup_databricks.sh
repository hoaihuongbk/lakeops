#!/bin/bash

# Databricks Connect Setup Script
echo "🚀 Databricks Connect Setup Helper"
echo "=================================="

# Check if databricks CLI is installed
if ! command -v databricks &> /dev/null; then
    echo "❌ Databricks CLI is not installed."
    echo "Installing databricks-cli..."
    pip install databricks-cli
fi

echo "✅ Databricks CLI is available"

# Get workspace URL from user
echo ""
read -p "📝 Enter your Databricks workspace URL [https://dbc-36096262-fee6.cloud.databricks.com]: " WORKSPACE_URL

# Use default if no input provided
if [ -z "$WORKSPACE_URL" ]; then
    WORKSPACE_URL="https://dbc-36096262-fee6.cloud.databricks.com"
    echo "Using default workspace URL: $WORKSPACE_URL"
fi

echo ""
echo "🔐 Starting OAuth authentication flow for serverless compute..."
echo "This will open a browser window for authentication."
echo ""

# Setup for serverless compute
echo "🚀 Setting up for serverless compute..."
databricks auth login --host "$WORKSPACE_URL"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Databricks serverless authentication setup successful!"
    echo ""
    echo "📋 Your profiles:"
    databricks auth profiles
    echo ""
    echo "🧪 Testing connection..."
    databricks clusters list --output json | head -n 5
    echo ""
    echo "✅ Setup complete! You can now run:"
    echo "   make run-databricks  # Run with serverless compute"
    echo ""
    echo "💡 Tips:"
    echo "   - Set DATABRICKS_PROFILE=<profile_name> to use a specific profile"
    echo "   - Serverless compute provides better performance and cost efficiency"
else
    echo "❌ Authentication failed. Please check your workspace URL and try again."
    exit 1
fi 