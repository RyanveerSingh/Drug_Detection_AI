print("Script started")
import tweepy
print("Tweepy imported")
import pandas as pd
import time
import hashlib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Twitter API credentials (replace with your own)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAADZe2gEAAAAA84gtLH72%2BzSV39oKtAxGleKMbig%3Dz54ozY1ZSCz8FG62Z9z5vO21B2ML1s0ccORHGcJVqWSPCHIFCs"
API_KEY = "Kaha82MbODxuBs72O0p8Gjj8m"
API_SECRET = "l9LXxu7PYAoqTykxIo2z0BnSLQXPiX2Mop4feZBMzEJMDl18Dg"
ACCESS_TOKEN = "1935608638741032960-Aa6yP6oajDzY6YLrSBlcXH6olhQ7Wp"
ACCESS_TOKEN_SECRET = "uV5SGj808L4GOnFriM6PaKZpsC7eY01t0AGTdOkdFa6s4"

logger.info("Initializing Tweepy client...")
try:
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True  # Automatically wait if rate limit is hit
    )
except Exception as e:
    logger.error(f"Failed to initialize Tweepy client: {e}")
    exit(1)

# Keywords for drug use and overdose symptoms (limited to 3)
KEYWORDS = ["heroin", "fentanyl", "cocaine"]

# Function to anonymize user IDs
def anonymize_username(username):
    return hashlib.md5(str(username).encode()).hexdigest() if username else "unknown"

# Scrape up to exactly 10 tweets per keyword from a maximum of 30 searched posts
def scrape_tweets(keywords, max_tweets_per_keyword=10, max_search_limit=30):
    data = []
    logger.info(f"Starting to scrape tweets for {len(keywords)} keywords...")

    for keyword in keywords:
        logger.info(f"🔍 Scraping for keyword: '{keyword}'")
        collected_count = 0
        search_count = 0

        try:
            # Paginate to search up to max_search_limit posts
            query = f"{keyword} -is:retweet lang:en"  # Filter out retweets, English only
            for tweet_batch in tweepy.Paginator(
                client.search_recent_tweets,
                query=query,
                max_results=10,  # Smaller batches to stay within limits
                tweet_fields=["created_at", "author_id"]
            ):
                if tweet_batch.data and search_count < max_search_limit:
                    for tweet in tweet_batch.data:
                        search_count += 1
                        if collected_count < max_tweets_per_keyword:
                            data.append({
                                "post_id": tweet.id,
                                "text": tweet.text,
                                "timestamp": tweet.created_at,
                                "username": anonymize_username(tweet.author_id)
                            })
                            collected_count += 1
                        if collected_count >= max_tweets_per_keyword or search_count >= max_search_limit:
                            break
                    logger.info(f"Collected {collected_count} tweets out of {search_count} searched for '{keyword}'")
                else:
                    logger.warning(f"No more tweets found for '{keyword}' within search limit")
                
                if collected_count >= max_tweets_per_keyword or search_count >= max_search_limit:
                    break

        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit hit for '{keyword}': {e}")
            break
        except tweepy.TweepyException as e:
            logger.error(f"API error for '{keyword}': {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error for '{keyword}': {e}")
            continue

        time.sleep(5)  # Reduced delay since wait_on_rate_limit handles most cases

    df = pd.DataFrame(data)
    logger.info(f"Total tweets collected: {len(df)}")
    return df

# Main process
if __name__ == "__main__":
    logger.info("📡 Beginning tweet collection process...")
    df = scrape_tweets(KEYWORDS)
    if not df.empty:
        df.to_csv("raw_data.csv", index=False)
        logger.info("💾 Saved to raw_data.csv")
    else:
        logger.warning("No data collected, raw_data.csv not created")