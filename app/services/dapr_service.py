"""
Dapr service for distributed application runtime features
"""

import logging
from typing import Any, Dict, Optional
from dapr.clients import DaprClient
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DaprService:
    """Dapr service for state management and pub/sub"""

    @staticmethod
    @contextmanager
    def get_client():
        """Get Dapr client in a context manager"""
        client = DaprClient()
        try:
            yield client
        finally:
            client.close()

    @classmethod
    def save_state(cls, key: str, value: Any, store_name: str = "learnflow-statestore"):
        """Save state using Dapr state management"""
        try:
            with cls.get_client() as client:
                # Convert value to string if it's not already
                if not isinstance(value, str):
                    import json
                    value_str = json.dumps(value)
                else:
                    value_str = value
                
                client.save_state(store_name, key, value_str)
                logger.info(f"State saved: {key} to {store_name}")
        except Exception as e:
            logger.error(f"Error saving state for key {key}: {str(e)}")
            raise

    @classmethod
    def get_state(cls, key: str, store_name: str = "learnflow-statestore") -> Optional[Any]:
        """Get state using Dapr state management"""
        try:
            with cls.get_client() as client:
                response = client.get_state(store_name, key)
                if response.data:
                    import json
                    return json.loads(response.data.decode('utf-8'))
                return None
        except Exception as e:
            logger.error(f"Error getting state for key {key}: {str(e)}")
            return None

    @classmethod
    def publish_event(cls, topic: str, data: Dict[str, Any], pubsub_name: str = "learnflow-pubsub"):
        """Publish event using Dapr pub/sub"""
        try:
            with cls.get_client() as client:
                client.publish_event(pubsub_name, topic, data)
                logger.info(f"Event published to topic {topic}")
        except Exception as e:
            logger.error(f"Error publishing event to topic {topic}: {str(e)}")
            raise

    @classmethod
    def invoke_service(cls, service_name: str, method: str, data: Dict[str, Any] = None):
        """Invoke another service using Dapr service invocation"""
        try:
            with cls.get_client() as client:
                response = client.invoke_method(
                    service_name,
                    method,
                    data,
                    content_type='application/json'
                )
                return response
        except Exception as e:
            logger.error(f"Error invoking service {service_name} method {method}: {str(e)}")
            raise