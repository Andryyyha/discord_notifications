import sys
sys.path.insert(0, 'package/')
import json
import requests
import os
import boto3
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def parse_service_event(event, service='Service'):
    return [
        {
            'name': service,
            'value': 'Server started',
            "inline": True
        },
        {
            'name': 'Public IP',
            'value': event,
            "inline": True
        }
    ]


def handler(event, context):
    webhook_url = os.getenv("WEBHOOK_URL")
    parsed_message = []
    for record in event.get('Records', []):
        print(record)
        print("type of record", type(record))
        message = record['Sns']['Message']
        print(message)
        print("type of message", type(message))
        json_event = json.loads(message)
        print("type of json_event", type(json_event))
        instance_id = json_event['detail']['instance-id']
        print(instance_id)
        print("type of instance_id", type(instance_id))# This is the instance ID from the event
        ec2 = boto3.client('ec2',
        aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"))
        instances = ec2.describe_instances(InstanceIds=[instance_id])
        print(instances)
        print("Type of instances", instances)
        public_ip = instances['Reservations'][0]['Instances'][0]['PublicIpAddress']
        parsed_message = parse_service_event(public_ip,
                                              'Minecraft "Пати" Server')
        discord_data = {
            'username': 'AWS',
            'avatar_url': 'https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png',
            'embeds': [{
                'color': 16711680,
                'fields': parsed_message
            }]
        }
        print(discord_data)
        print("Type of discord_data", type(discord_data))
        headers = {'content-type': 'application/json'}
        response = requests.post(webhook_url, data=json.dumps(discord_data),
                                 headers=headers)

        logging.info(f'Discord response: {response.status_code}')
        logging.info(response.content)


def server_shutdown(event, context):
    webhook_url = os.getenv("WEBHOOK_URL")
    shutdown_event = [
        {
            'name': 'Minecraft "Пати" Server',
            'value': 'Server stopped',
            "inline": True
        }
    ]
    discord_data = {
            'username': 'AWS',
            'avatar_url': 'https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png',
            'embeds': [{
                'color': 16711680,
                'fields': shutdown_event
            }]
        }
    headers = {'content-type': 'application/json'}
    response = requests.post(webhook_url, data=json.dumps(discord_data),
                                headers=headers)

    logging.info(f'Discord response: {response.status_code}')
    logging.info(response.content)
