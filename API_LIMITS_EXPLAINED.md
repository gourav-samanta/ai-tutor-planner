# Gemini API Free Tier Limits - Reality Check

## The Harsh Truth About Free Tier

### Daily Limits (Per API Key)
- **15-20 requests per day** (not 1500, not 150, just 15-20!)
- **5 requests per minute**
- Resets at midnight UTC

### What This Means With 5 Keys
- **Total: ~75-100 requests per day** across all 5 keys
- That's it. That's all you get for free.

## Why You're Hitting Limits So Fast

### Each Action Uses API Calls:
1. **Create Learning Plan** = 1 call (generates roadmap)
2. **Generate Daily Tasks** = 1 call (8-12 tasks)
3. **Generate Daily Test** = 1 call (5-8 questions)
4. **Generate Weekly Test** = 1 call (15-20 questions)
5. **Learn More Button** = 1 call per task
6. **AI Summary** = 1 call (cached after first use)

### Example Usage:
- Create 2 plans = 2 calls
- Generate tasks for 2 days = 2 calls
- Click "Learn More" 5 times = 5 calls
- Generate 1 test = 1 call
- **Total: 10 calls** (already 50% of ONE key's daily limit!)

## Why All 5 Keys Hit Limits

You probably:
1. Created multiple learning plans today
2. Generated tasks multiple times
3. Tried generating tests multiple times
4. Clicked "Learn More" buttons
5. Each retry after an error = another API call

**Result:** All 5 keys exhausted their 15-20 daily requests

## Solutions

### Option 1: Wait (Free)
- Wait until tomorrow (midnight UTC)
- All keys reset
- You get another 75-100 requests

### Option 2: Upgrade to Paid (Recommended)
- **Gemini API Paid Tier**: $0.00015 per request
- 1000 requests = $0.15 (15 cents!)
- No daily limits
- Much faster

### Option 3: Use Fewer Features
- Don't click "Learn More" buttons (saves lots of calls)
- Generate tests only when needed
- Create plans carefully (don't regenerate)
- One subject at a time

## Current Status Check

When you see an error, click "🔍 API Key Status" to see:
- How many keys are available
- How many have failed
- When each key was last used

## Important Notes

1. **Local vs Cloud**: Your local secrets file has the keys, but you need to update Streamlit Cloud secrets too
2. **Session Reset**: Restarting the app clears the "failed keys" tracking
3. **Rotation Works**: The system IS rotating keys, but they're all hitting their daily limits
4. **Not a Bug**: This is just how restrictive the free tier is

## Recommendation

For a production app with multiple users, the free tier is NOT viable. You need:
- Paid Gemini API ($0.00015/request)
- Or use a different AI service with better free tier
- Or cache more aggressively to reduce API calls
- Or limit features (no "Learn More", fewer tests)

The free tier is meant for testing, not production use.
