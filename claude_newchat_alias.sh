#!/bin/bash
# Add this to your ~/.bashrc or ~/.zshrc file

# Function to start new Claude chat with SecureScout context
claude-securescout() {
    /home/qubit/Downloads/secure-scout/SecureScout/newchat_complete.sh
}

# Shorter alias that opens Claude and pastes context
alias newchat='claude-securescout'
alias cs='cd /home/qubit/Downloads/secure-scout/SecureScout'

echo "✅ Aliases added:"
echo "  newchat - Start new Claude chat with SecureScout context"
echo "  cs - cd to SecureScout directory"