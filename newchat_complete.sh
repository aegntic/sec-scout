#!/bin/bash
# Complete newchat script that opens Claude and pastes context

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Context file
CONTEXT_FILE="/home/qubit/Downloads/secure-scout/SecureScout/NEW_CHAT_CONTEXT.md"

# Function to simulate keyboard input
send_keys() {
    sleep 1
    xdotool type --delay 50 "$1"
}

# Copy context to clipboard
if command -v xclip &> /dev/null; then
    cat "$CONTEXT_FILE" | xclip -selection clipboard
    echo -e "${GREEN}✅ Context copied to clipboard!${NC}"
elif command -v pbcopy &> /dev/null; then
    cat "$CONTEXT_FILE" | pbcopy
    echo -e "${GREEN}✅ Context copied to clipboard!${NC}"
fi

# Start Claude in new terminal
echo -e "${BLUE}🚀 Starting Claude with context...${NC}"

# Option 1: If Claude CLI is installed
if command -v claude &> /dev/null; then
    # Start new terminal with Claude and auto-paste
    gnome-terminal -- bash -c "
        claude
        sleep 2
        # Paste the context (Ctrl+Shift+V in terminal)
        xdotool key ctrl+shift+v
        sleep 1
        # Press Enter to send
        xdotool key Return
        exec bash
    " &
    
# Option 2: Open Claude in browser with xdotool automation
else
    echo -e "${BLUE}Opening Claude in browser...${NC}"
    
    # Open Claude.ai
    xdg-open "https://claude.ai/new" &
    
    # Wait for page to load
    sleep 5
    
    # Use xdotool to paste (requires xdotool)
    if command -v xdotool &> /dev/null; then
        # Wait for Claude to be ready
        sleep 2
        
        # Paste the context (Ctrl+V)
        xdotool key ctrl+v
        
        echo -e "${GREEN}✅ Context should be pasted!${NC}"
    else
        echo -e "${BLUE}Please paste the context manually (Ctrl+V)${NC}"
    fi
fi

echo -e "\n${GREEN}Next steps:${NC}"
echo "1. Context has been pasted into Claude"
echo "2. First command to run: cd /home/qubit/Downloads/secure-scout/SecureScout && git pull origin dev"