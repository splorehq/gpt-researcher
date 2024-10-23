import logging
import boto3
from botocore.exceptions import ClientError
import json
from typing import Optional, Dict, Union

logger = logging.getLogger(__name__)

class AWSecretsManager:
    def __init__(self, config: dict):
        self.sess = boto3.session.Session(region_name=config["region"])
        self.client = self.sess.client("secretsmanager", region_name=config["region"])

    def get_secret(self, secret_id: str) -> Optional[Dict[str, Union[str, int]]]:
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            secret_str = response.get("SecretString")
            return json.loads(secret_str) if secret_str else None
        except ClientError as e:
            logger.exception(f"Failed to retrieve secret {secret_id}: {e.response['Error']['Code']}")
            return None