#!/bin/bash
# Post-generate script to fix generated API code for browser compatibility

echo "🔧 Patching generated API code..."

REQUEST_FILE="src/api/generated/core/request.ts"

# Fix 1: Remove Node.js FormData import (browser has native FormData)
sed -i "/import FormData from 'form-data';/d" "$REQUEST_FILE"

# Fix 2: Replace formData.getHeaders() with empty object (browser FormData doesn't have this method)
sed -i "s/const formHeaders = typeof formData?.getHeaders === 'function' && formData?.getHeaders() || {}/const formHeaders = {}; \/\/ Browser FormData doesn't have getHeaders() method/g" "$REQUEST_FILE"

echo "✅ API code patched successfully!"
echo ""
echo "Changes applied:"
echo "  - Removed Node.js FormData import"
echo "  - Fixed FormData.getHeaders() for browser compatibility"
