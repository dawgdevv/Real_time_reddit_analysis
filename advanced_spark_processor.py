from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode, udf, to_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, FloatType, TimestampType
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
import datetime

# Download NLTK resources (run once)

nltk.download('vader_lexicon', quiet=True)
#mongo connetion
mongo_uri = "mongodb+srv://nishantraj:nishant24@cluster0.oqfjt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_db = "reddit_analytics"
mongo_collections = {
    "stats": "subreddit_stats",
    "posts": "reddit_posts",
    "comments": "reddit_comments"
}

# Create Spark session with improved configuration
spark = SparkSession.builder \
    .appName("RedditAdvancedProcessor") \
    .config("spark.jars", "/home/dawgdevv/kafka/libs/spark-sql-kafka-0-10_2.12-3.3.0.jar,/home/dawgdevv/kafka/libs/spark-token-provider-kafka-0-10_2.12-3.3.0.jar,/home/dawgdevv/kafka/libs/slf4j-api-1.7.32.jar") \
    .config("spark.mongodb.output.uri", mongo_uri) \
    .config("spark.mongodb.output.database", mongo_db) \
    .config("spark.sql.streaming.stopActiveRunOnRestart", "true") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .getOrCreate()

# Set log level to hide irrelevant warnings
spark.sparkContext.setLogLevel("ERROR")

# Get current IP address for Kafka connection
try:
    import subprocess
    current_ip = subprocess.check_output("ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1 | head -n 1", shell=True).decode('utf-8').strip()
except:
    current_ip = "192.168.1.12"

# Schema definition
schema = StructType([
    StructField("id", StringType(), True),
    StructField("description", StringType(), True),
    StructField("upvotes", IntegerType(), True),
    StructField("downvotes", IntegerType(), True),
    StructField("num_comments", IntegerType(), True),
    StructField("top_comments", ArrayType(StringType()), True)
])

# Create output directories if they don't exist
output_dir = "/home/dawgdevv/Documents/Big_Data/processed_data"
checkpoint_dir = "/home/dawgdevv/Documents/Big_Data/checkpoints"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(checkpoint_dir, exist_ok=True)


# Sentiment analysis function
def analyze_sentiment(text):
    if not text:
        return 0.0
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(text)
    return sentiment['compound']

# Function to write batch data to MongoDB
# Function to write batch data to MongoDB
def write_to_mongo(df, epoch_id, collection_name):
    # Add processing timestamp
    df = df.withColumn("processing_timestamp", 
                      lit(datetime.datetime.now().isoformat()))
    
    # Write to MongoDB - CORRECTED FORMAT
    df.write \
        .format("mongo") \
        .option("uri", mongo_uri) \
        .option("database", mongo_db) \
        .option("collection", collection_name) \
        .mode("append") \
        .save()
    
    print(f"Batch {epoch_id}: Wrote {df.count()} records to MongoDB collection '{collection_name}'")

# Register UDF
sentiment_udf = udf(analyze_sentiment, FloatType())

# Read from Kafka with proper configurations
# Read from Kafka with proper configurations
kafka_options = {
    "kafka.bootstrap.servers": f"{current_ip}:9092",
    "subscribe": "news,relationship_advice,StockMarket,Jokes,mildlyinteresting", 
    "startingOffsets": "latest",
    "failOnDataLoss": "false",
    "kafka.consumer.pollTimeoutMs": "10000",
    "fetchOffset.numRetries": "5",
    "fetchOffset.retryIntervalMs": "1000",
    "maxOffsetsPerTrigger": "10000",
    "kafkaConsumer.pollTimeoutMs": "5000"
}

df = spark \
    .readStream \
    .format("kafka") \
    .options(**kafka_options) \
    .load()

# Parse JSON data
parsed_df = df \
    .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)", "topic", "timestamp") \
    .select(
        col("topic").alias("subreddit"),
        from_json(col("value"), schema).alias("data"),
        to_timestamp(col("timestamp").cast("long") / 1000).alias("event_time")
    ) \
    .select("subreddit", "event_time", "data.*")

# Apply sentiment analysis to descriptions
df_with_sentiment = parsed_df \
    .withColumn("sentiment_score", sentiment_udf(col("description")))

# Process comments with sentiment
comments_df = parsed_df \
    .select("subreddit", "id", "description", explode("top_comments").alias("comment")) \
    .withColumn("comment_sentiment", sentiment_udf(col("comment")))

# Aggregate data by subreddit
subreddit_stats = df_with_sentiment \
    .groupBy("subreddit") \
    .agg(
        {"upvotes": "avg", "num_comments": "avg", "sentiment_score": "avg", "id": "count"}
    ) \
    .withColumnRenamed("avg(upvotes)", "avg_upvotes") \
    .withColumnRenamed("avg(num_comments)", "avg_comments") \
    .withColumnRenamed("avg(sentiment_score)", "avg_sentiment") \
    .withColumnRenamed("count(id)", "post_count")

# Common options for all queries
query_options = {
    "checkpointLocation": f"{checkpoint_dir}/stats",
    "truncate": False
}

# Write processed data to console
query1 = subreddit_stats.writeStream \
    .outputMode("complete") \
    .format("console") \
    .options(**query_options) \
    .start()

# Write to Parquet files with better options
query2 = df_with_sentiment.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", f"{output_dir}/posts") \
    .option("checkpointLocation", f"{checkpoint_dir}/posts") \
    .start()

query3 = comments_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", f"{output_dir}/comments") \
    .option("checkpointLocation", f"{checkpoint_dir}/comments") \
    .start()

# Write subreddit stats to MongoDB
query_mongo_stats = subreddit_stats.writeStream \
    .foreachBatch(lambda df, epoch_id: write_to_mongo(df, epoch_id, mongo_collections["stats"])) \
    .outputMode("update") \
    .option("checkpointLocation", f"{checkpoint_dir}/mongo_stats") \
    .start()

# Write posts with sentiment to MongoDB
query_mongo_posts = df_with_sentiment.writeStream \
    .foreachBatch(lambda df, epoch_id: write_to_mongo(df, epoch_id, mongo_collections["posts"])) \
    .outputMode("append") \
    .option("checkpointLocation", f"{checkpoint_dir}/mongo_posts") \
    .start()

# Write comments with sentiment to MongoDB
query_mongo_comments = comments_df.writeStream \
    .foreachBatch(lambda df, epoch_id: write_to_mongo(df, epoch_id, mongo_collections["comments"])) \
    .outputMode("append") \
    .option("checkpointLocation", f"{checkpoint_dir}/mongo_comments") \
    .start()

# Gracefully handle termination
try:
    spark.streams.awaitAnyTermination()
except KeyboardInterrupt:
    print("Shutting down gracefully...")
finally:
    print("Stream processing ended")