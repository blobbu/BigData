"""
Module to provide kafka handlers for internal logging facility.
https://stackoverflow.com/questions/21102293/how-to-write-to-kafka-from-python-logging-module
"""

import json
import logging
from kafka import KafkaProducer


class KafkaHandler(logging.Handler):
    """Class to instantiate the kafka logging facility."""

    def __init__(self, hostlist, topic='log', identifier='', tls=None):
        """Initialize an instance of the kafka handler."""
        logging.Handler.__init__(self)
        self.identifier = identifier
        self.producer = KafkaProducer(bootstrap_servers=hostlist,
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                      linger_ms=10)
        self.topic = topic

    def emit(self, record):
        """Emit the provided record to the kafka_client producer."""
        # drop kafka logging to avoid infinite recursion
        if 'kafka.' in record.name:
            return

        try:
            # apply the logger formatter
            msg = self.format(record)
            self.producer.send(self.topic, {'id': self.identifier, 'message': msg})
            self.flush(timeout=1.0)
        except Exception:
            logging.Handler.handleError(self, record)

    def flush(self, timeout=None):
        """Flush the objects."""
        self.producer.flush(timeout=timeout)

    def close(self):
        """Close the producer and clean up."""
        self.acquire()
        try:
            if self.producer:
                self.producer.close()

            logging.Handler.close(self)
        finally:
            self.release()