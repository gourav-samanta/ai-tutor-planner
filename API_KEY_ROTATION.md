# API Key Rotation System

## Overview
The application now uses multiple Gemini API keys to handle quota limits automatically.

## How It Works

### 1. Multiple API Keys
- 5 API keys configured in `.streamlit/secrets.toml`
- Keys are stored in an array: `gemini.api_keys`

### 2. Rotation Strategy
- **Round-robin rotation**: Keys are used in sequence
- **Automatic failover**: When a key hits quota (429 error), it's marked as failed
- **Smart retry**: Automatically tries the next available key (up to 3 attempts)
- **Auto-reset**: When all keys fail, the system resets and tries again (quotas may have refreshed)

### 3. Key Features
- **Transparent**: No code changes needed in pages - rotation happens automatically
- **Resilient**: Continues working as long as at least one key has quota remaining
- **Rate-limited**: Still maintains 2-second delay between calls to avoid hitting rate limits
- **Stateful**: Tracks which keys have failed during the session

## Configuration

### secrets.toml Format
```toml
[gemini]
api_keys = [
    "AIzaSyAHB6KQdzP0-BArLgr6CXFeYPZNcRLpXls",
    "AIzaSyC9TymBbWHRmwprfSwp2tRQc70cNu5RIaY",
    "AIzaSyBnsYyq2a7_5cfCb2XJ_Np_O39qL59zPHc",
    "AIzaSyCSoSzNlQhPVmC6DRkzlmxffIsmcxuxccU",
    "AIzaSyDFjEqMENIvnAn-qCuTwqaUuuSURw7TFNI"
]
```

## Error Handling

### Quota Errors (429)
- Key is automatically marked as failed
- Next key is tried immediately
- User sees error only if all keys are exhausted

### Other Errors
- Non-quota errors are raised immediately
- No automatic retry for non-quota issues

## Benefits

1. **5x Quota**: Effectively multiplies your daily quota by 5
2. **High Availability**: Service continues even if some keys hit limits
3. **No Manual Intervention**: Automatic failover without user action
4. **Better UX**: Users experience fewer quota errors

## Monitoring

The system tracks:
- Current key index (rotates 0-4)
- Failed keys set (cleared when all keys fail)
- Last call timestamp (for rate limiting)

## Deployment

When deploying to Streamlit Cloud:
1. Go to App Settings → Secrets
2. Update the `[gemini]` section with the array format
3. Save and restart the app

## Limitations

- Free tier: 20 requests per day per key = 100 total requests/day
- Rate limit: Still 2 seconds between calls (shared across all keys)
- Session-based tracking: Failed keys reset when app restarts
