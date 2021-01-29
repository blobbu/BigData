#!/bin/bash

TOPICS=$(kafka-topics.sh --zookeeper 10.7.38.62:2181 --list)

for T in $TOPICS
do
	if [ "$T" != "__consumer_offsets" ]; then
  		kafka-topics.sh --zookeeper 10.7.38.62:2181 --delete --topic $T
	fi
done
