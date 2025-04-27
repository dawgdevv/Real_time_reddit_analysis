
from kafka import KafkaConsumer
import json
import time

# Get current IP address or use manually specified IP
try:
    import subprocess
    current_ip = subprocess.check_output("ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1 | head -n 1", shell=True).decode('utf-8').strip()
except:
    current_ip = "192.168.1.12"  # Fallback to the IP shown in your output

print(f"Connecting to bootstrap server: {current_ip}:9092")

# Create consumer for all topics
consumer = KafkaConsumer(
    'news', 'relationship_advice', 'StockMarket', 'Jokes', 'mildlyinteresting',
    bootstrap_servers=f'{current_ip}:9092',
    auto_offset_reset='earliest',
    group_id='reddit-consumer-group-new',  # Use a new group ID for testing
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
print("Consumer started. Waiting for messages...")
try:
    for message in consumer:
        print(f"\n{'-'*50}")
        print(f"Topic: {message.topic}, Partition: {message.partition}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.timestamp/1000))}")
        
        post_data = message.value
        print(f"Post ID: {post_data.get('id')}")
        print(f"Description: {post_data.get('description')}")
        print(f"Upvotes: {post_data.get('upvotes')}, Comments: {post_data.get('num_comments')}")
        
        if post_data.get('top_comments'):
            print("\nTop comment:")
            print(f"  {post_data.get('top_comments')[0][:100]}...")
        
except KeyboardInterrupt:
    print("Consumer stopped by user")
finally:
    consumer.close()
    print("Consumer closed")