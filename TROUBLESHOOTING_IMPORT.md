# Troubleshooting "Failed to fetch" Error

## Common Causes

### 1. CORS Issue (Most Common)

**Problem:** Your Netlify frontend URL is not in the backend's `ALLOWED_ORIGINS`.

**Solution:**
1. Go to your **Render Dashboard** → Your Web Service
2. Go to **Environment** tab
3. Find `ALLOWED_ORIGINS` environment variable
4. Add your Netlify URL (comma-separated):
   ```
   http://localhost:5500,http://127.0.0.1:5500,https://your-netlify-site.netlify.app
   ```
5. **Save** and **Redeploy** your service

**Example:**
If your Netlify site is `https://royal-family-tree.netlify.app`, then:
```
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500,https://royal-family-tree.netlify.app
```

### 2. Backend URL Format

**Problem:** Trailing slash or wrong URL format.

**Check:**
- Backend URL should be: `https://royal-family-tree.onrender.com` (no trailing slash)
- NOT: `https://royal-family-tree.onrender.com/` (with trailing slash)

### 3. Backend Not Running

**Check:**
1. Open your backend URL in browser: `https://royal-family-tree.onrender.com/health`
2. You should see: `{"status":"healthy","database":"connected"}`
3. If you get an error, your backend is not running

### 4. Admin Token Mismatch

**Check:**
1. In Render → Environment Variables → `ADMIN_TOKEN`
2. Copy the exact value (no extra spaces)
3. Paste it in the admin import tool

### 5. Network/Firewall

**Check:**
- Open browser console (F12)
- Look for detailed error messages
- Check if there's a CORS error specifically

## Quick Test

Test the backend directly:

```bash
curl -X POST https://royal-family-tree.onrender.com/admin/import/combined \
  -H "Content-Type: application/json" \
  -H "X-ADMIN-TOKEN: your-admin-token-here" \
  -d '{"rows": [{"english_name": "Test Person"}]}'
```

If this works, the issue is CORS. If it fails, check the error message.

## Step-by-Step Fix

1. ✅ **Verify backend is running:**
   - Visit: `https://royal-family-tree.onrender.com/health`
   - Should return JSON

2. ✅ **Update ALLOWED_ORIGINS in Render:**
   - Add your Netlify URL
   - Redeploy

3. ✅ **Test again:**
   - Open admin import tool
   - Try import again

4. ✅ **Check browser console:**
   - Press F12
   - Look at Console tab for detailed errors
   - Look at Network tab to see the actual request/response

