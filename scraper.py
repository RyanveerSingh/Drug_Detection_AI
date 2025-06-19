print("Script started")
import tweepy
print("Tweepy imported")
import pandas as pd
import time
import hashlib

# Twitter API credentials
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAOJT2gEAAAAA56K4520i2rwSGQ4qxMPPrfWxB6w%3DX1mQKPubOzQ9tWWrJxpytVeTxvX8VaQ06DNpfD8ZpwKLy2jvtO"
API_KEY = "Zfu0UHwSQVCRLBmatPG0TCWfx"
API_SECRET = "68NSlcSMyxiKuwvljC05LiNJddCAeUn6V3TNWZkw3BG6CTP85D"
ACCESS_TOKEN = "1578655053409198085-e3o1q7x0oOZsjfSVioRaJP7Xpa15zy"
ACCESS_TOKEN_SECRET = "Qb78jo2LC2zvcdsL78QL1FQhC5r2BA4TAFGEqzhxFXQUh"

print("Initializing Tweepy client...")
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Keywords for drug use and overdose symptoms
KEYWORDS = ["heroin", "fentanyl", "cocaine", "xanax", "overdose", "can't breathe", "unconscious"]

# Function to anonymize user IDs
def anonymize_username(username):
    return hashlib.md5(str(username).encode()).hexdigest() if username else "unknown"

# Scrape up to exactly 20 tweets per keyword
def scrape_tweets(keywords):
    data = []
    print(f"Starting to scrape tweets for {len(keywords)} keywords...\n")

    for keyword in keywords:
        print(f"🔍 Scraping for keyword: '{keyword}'")
        collected_count = 0

        try:
            # Get up to 100 (Twitter API max per request)
            tweets = client.search_recent_tweets(
                query=keyword,
                max_results=100,
                tweet_fields=["created_at", "author_id"]
            )

            if tweets.data:
                for tweet in tweets.data:
                    data.append({
                        "post_id": tweet.id,
                        "text": tweet.text,
                        "timestamp": tweet.created_at,
                        "username": anonymize_username(tweet.author_id)
                    })
                    collected_count += 1
                    if collected_count >= 20:
                        break
                print(f"✅ Collected exactly {collected_count} tweets for '{keyword}'")
            else:
                print(f"⚠️ No tweets found for '{keyword}'")

        except tweepy.TooManyRequests as e:
            print(f"❌ Rate limit hit: Too many requests.\n{e}")
            break
        except Exception as e:
            print(f"❌ Error scraping for '{keyword}': {e}")

        time.sleep(10)  # Delay to avoid hitting rate limit

    return pd.DataFrame(data)

# Main process
if __name__ == "__main__":
    print("📡 Beginning tweet collection process...")
    df = scrape_tweets(KEYWORDS)
    print(f"\n📊 Total tweets collected: {len(df)}")
    df.to_csv("raw_data.csv", index=False)
    print("💾 Saved to raw_data.csv")
