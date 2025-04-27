from kafka import KafkaProducer
import json
import praw
import time
from dotenv import load_dotenv
import os
load_dotenv()

try:
    import subprocess
    current_ip = subprocess.check_output("ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1 | head -n 1", shell=True).decode('utf-8').strip()
except:
    current_ip = "192.168.1.12"  # Fallback to the IP shown in your output

print(f"Using bootstrap server: {current_ip}:9092")

producer = KafkaProducer(
    bootstrap_servers=f'{current_ip}:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

subreddits = ["news", "relationship_advice", "StockMarket", "Jokes", "mildlyinteresting"]


while True:
    try:
        print(f"\n[INFO] Fetching at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        for subreddit_name in subreddits:
            subreddit = reddit.subreddit(subreddit_name)
            print(f"[INFO] Fetching from: r/{subreddit_name}")
            
            for post in subreddit.new(limit=5):
                if post.num_comments == 0:
                    continue

                description = post.selftext[:100] if post.selftext else post.title[:100]
                
                post.comments.replace_more(limit=0)
                top_comments = [comment.body for comment in post.comments[:1]]
                
                post_data = {
                    "id": post.id,
                    "description": description,
                    "upvotes": post.score,
                    "downvotes": post.downs,
                    "num_comments": post.num_comments,
                    "top_comments": top_comments
                }

                producer.send(subreddit_name, value=post_data)
                print(f"[SENT] Topic: {subreddit_name}, Post ID: {post.id}")

        print("[INFO] Sleeping for 5 minutes...\n")
        time.sleep(300)  

    except Exception as e:
        print(f"[ERROR]  {e}")
        time.sleep(60)  
