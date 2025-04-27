#!/bin/bash
# filepath: /home/dawgdevv/Documents/Big_Data/setup_kafka.sh

# Stop any existing Kafka and ZooKeeper processes
echo "Stopping any existing Kafka and ZooKeeper processes..."
pkill -f "kafka.Kafka"
pkill -f "org.apache.zookeeper.server.quorum.QuorumPeerMain"
sleep 2

# Get current IP address (using the primary network interface)
CURRENT_IP=$(ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1 | head -n 1)
echo "Using IP address: $CURRENT_IP"

# Update broker config files with current IP
for i in {1..3}; do
  CONFIG_FILE="/home/dawgdevv/Documents/Big_Data/brokers/broker-$i/server.properties"
  echo "Updating configuration for broker $i at $CONFIG_FILE"
  
  # First check if the file exists
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file $CONFIG_FILE not found!"
    exit 1
  fi
  
  # Update the advertised.listeners with current IP
  sed -i "s/advertised.listeners=PLAINTEXT:\/\/localhost/advertised.listeners=PLAINTEXT:\/\/$CURRENT_IP/" $CONFIG_FILE
  
  # Verify change
  grep "advertised.listeners" $CONFIG_FILE
done

# Create log directories if they don't exist
echo "Creating log directories..."
mkdir -p /tmp/kafka-logs-1
mkdir -p /tmp/kafka-logs-2
mkdir -p /tmp/kafka-logs-3

# Determine Kafka directory
KAFKA_DIR="/home/dawgdevv/Documents/Big_Data/kafka"
if [ ! -d "$KAFKA_DIR" ]; then
  echo "Kafka directory not found at $KAFKA_DIR"
  echo "Please enter the path to your Kafka installation directory:"
  read KAFKA_DIR
fi

# Start ZooKeeper
echo "Starting ZooKeeper..."
$KAFKA_DIR/bin/zookeeper-server-start.sh -daemon $KAFKA_DIR/config/zookeeper.properties
echo "Waiting for ZooKeeper to fully start..."
sleep 5

# Start Kafka brokers
echo "Starting Kafka brokers..."
$KAFKA_DIR/bin/kafka-server-start.sh -daemon /home/dawgdevv/Documents/Big_Data/brokers/broker-1/server.properties
sleep 2
$KAFKA_DIR/bin/kafka-server-start.sh -daemon /home/dawgdevv/Documents/Big_Data/brokers/broker-2/server.properties
sleep 2
$KAFKA_DIR/bin/kafka-server-start.sh -daemon /home/dawgdevv/Documents/Big_Data/brokers/broker-3/server.properties
sleep 5

echo "Kafka brokers are starting. Waiting for brokers to be ready..."
sleep 10

# Create topics with replication
# Create topics with lower replication factor
echo "Creating Reddit topics with replication..."
$KAFKA_DIR/bin/kafka-topics.sh --create --topic news --bootstrap-server $CURRENT_IP:9092 --partitions 3 --replication-factor 1 --if-not-exists
$KAFKA_DIR/bin/kafka-topics.sh --create --topic relationship_advice --bootstrap-server $CURRENT_IP:9092 --partitions 3 --replication-factor 1 --if-not-exists
$KAFKA_DIR/bin/kafka-topics.sh --create --topic StockMarket --bootstrap-server $CURRENT_IP:9092 --partitions 3 --replication-factor 1 --if-not-exists
$KAFKA_DIR/bin/kafka-topics.sh --create --topic Jokes --bootstrap-server $CURRENT_IP:9092 --partitions 3 --replication-factor 1 --if-not-exists
$KAFKA_DIR/bin/kafka-topics.sh --create --topic mildlyinteresting --bootstrap-server $CURRENT_IP:9092 --partitions 3 --replication-factor 1 --if-not-exists

# List topics and their details
echo "Listing topics:"
$KAFKA_DIR/bin/kafka-topics.sh --list --bootstrap-server $CURRENT_IP:9092

echo "Detailed topic information:"
$KAFKA_DIR/bin/kafka-topics.sh --describe --bootstrap-server $CURRENT_IP:9092

echo "Kafka cluster is ready! You can now run your producer and consumer applications."
echo "Producer bootstrap server: $CURRENT_IP:9092"