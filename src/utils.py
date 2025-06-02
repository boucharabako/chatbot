from datetime import datetime
import json
from uuid import uuid4
import logging
from typing import List

import boto3

from src.config import env_vars
## Simple edit


class Utils:

    ALLOWED_EXTENSIONS = ["pdf", "docx", "doc", "png", "jpg", "jpeg"]

    @staticmethod
    def log_info(message):
        """_summary_
        Log a simple info message
        """
        logging.getLogger("uvicorn.error").info(msg=f"==> {message}")

    # @staticmethod
    # def log_debug(message):
    #     """_summary_
    #     Log a debug message
    #     """
    #     logging.getLogger("uvicorn.error").debug(msg=f"==> {message}")

    @staticmethod
    def log_error(message):
        """_summary_
        Log an error message
        """
        logging.getLogger("uvicorn.error").error(msg=f"==> {message}")

    @staticmethod
    def log_list(elements: List[any]):
        if elements:
            logging.getLogger("uvicorn.error").info(
                msg=f"Displaying all the {len(elements)} elements of the list"
            )
            for i in range(len(elements)):
                logging.getLogger("uvicorn.error").info(
                    msg=f"##### {i} ==> {json.dumps(elements[i], indent=4)}"
                )

    @staticmethod
    def get_logger():
        return logging.getLogger("uvicorn.error")

    @staticmethod
    def get_session():
        return boto3.Session(
            region_name=env_vars.AWS_REGION_NAME, profile_name=env_vars.AWS_PROFILE
        )
     
   

    @staticmethod
    def insert_data(item):
        # logging.getLogger("uvicorn.error").info(f"Table utilisée : {env_vars.DYNAMO_TABLE}")
        # logging.getLogger("uvicorn.error").info(f"REGION choisie : {env_vars.AWS_REGION_NAME}")
        # dynamo_client = boto3.client("dynamodb", region_name=env_vars.AWS_REGION_NAME)
        # logging.getLogger("*********1111").info(f"REGION choisie : {env_vars.AWS_REGION_NAME}")

        # dynamo_client.put_item(
        #     TableName=env_vars.DYNAMO_TABLE,
        #     Item=item,
        # )
        # logging.getLogger("*********222222").info(f"REGION choisie : {env_vars.AWS_REGION_NAME}")
        logger = logging.getLogger("uvicorn.error")
        logger.info(f"Table utilisée : {env_vars.DYNAMO_TABLE}")
        logger.info(f"REGION choisie : {env_vars.AWS_REGION_NAME}")
        dynamodb = boto3.resource("dynamodb", region_name=env_vars.AWS_REGION_NAME)
        table = dynamodb.Table(env_vars.DYNAMO_TABLE)
        try:
          response = table.put_item(Item=item)
          logger.info("Insertion réussie dans DynamoDB")
          logger.debug(f"Réponse DynamoDB : {response}")
        except Exception as e:
          logger.error(f"Erreur lors de l'insertion dans DynamoDB : {e}")
          raise  # Remonte l'exception si besoin
        
    @staticmethod
    def get_conversation_history(user_id: str):
        dynamo_resource = boto3.resource("dynamodb", region_name=env_vars.AWS_REGION_NAME)
        table = dynamo_resource.Table(env_vars.DYNAMO_TABLE)

        response = table.query(
            KeyConditionExpression=Key("conversation_id").eq(user_id),
            ScanIndexForward=True  # de l'ancien au récent
        )

        history = []
        for item in response.get("Items", []):
            history.append({
                "question": item.get("question"),
                "answer": item.get("answer"),
                "timestamp": item.get("timestamp")
            })
        return history

    @staticmethod
    def get_timestamp():
        return datetime.utcnow().isoformat() + "Z"
