#!/bin/bash
# Script to copy context and start new Claude chat

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Copying SecureScout context to clipboard...${NC}"

# Copy the context to clipboard (works on Linux with xclip)
if command -v xclip &> /dev/null; then
    cat NEW_CHAT_CONTEXT.md | xclip -selection clipboard
    echo -e "${GREEN}✅ Context copied to clipboard!${NC}"
elif command -v pbcopy &> /dev/null; then
    # macOS
    cat NEW_CHAT_CONTEXT.md | pbcopy
    echo -e "${GREEN}✅ Context copied to clipboard!${NC}"
else
    echo -e "${BLUE}📄 Context content:${NC}"
    echo "----------------------------------------"
    cat NEW_CHAT_CONTEXT.md
    echo "----------------------------------------"
    echo -e "${BLUE}Please copy the above manually${NC}"
fi

echo -e "\n${BLUE}🚀 Starting new Claude chat...${NC}"
echo -e "${GREEN}Steps:${NC}"
echo "1. Open new terminal/tab"
echo "2. Run: claude --new-conversation"
echo "3. Paste the context from clipboard"
echo "4. Continue with: cd /home/qubit/Downloads/secure-scout/SecureScout && git pull origin dev"

# Optionally, if you have a way to start Claude programmatically:
# claude --new-conversation

echo -e "\n${BLUE}Quick command to copy:${NC}"
echo "cd /home/qubit/Downloads/secure-scout/SecureScout && git pull origin dev && cat CLAUDE.md"