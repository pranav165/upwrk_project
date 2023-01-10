import datetime
import uuid
import boto3
import json
from retry import retry
from datetime import date, datetime
import requests

requests.packages.urllib3.disable_warnings()


class SqsClient:
    def __init__(self, queue_url):
        self.queue_url = queue_url
        self.client = boto3.client('sqs', aws_access_key_id='',
                                   aws_secret_access_key='',
                                   region_name='us-west-2', verify=False)

    def send_message(self, result=None):
        payload = {
            "timeSlotId": "1234",
            "date": date.today().strftime("%d/%m/%Y"),
            "datetimeOfTest": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

        if result == 1:
            payload["result"] = "accepted"
        elif result == 2:
            payload["result"] = "rejected"
        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(payload),
            MessageGroupId="test"
        )
        print("SENDER ------> Sending Message with payload as {}".format(payload))

    @retry(Exception, tries=4, delay=2)
    def receive_message(self):
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            AttributeNames=['All']
        )
        print("RECEIVER ------> Received a message with payload {}".format(response['Messages'][0]['Body']))

        receipt_handle = response['Messages'][0]['ReceiptHandle']
        self.delete_message(receipt_handle)

    def process_message(self):
        self.receive_message()
        answer = int(input("Enter 1 to select 2 to reject \n"))
        if answer == 1:
            print("Accepted")
            self.send_message(1)
        elif answer == 2:
            print("Rejected")
            self.send_message(2)
        else:
            print("Wrong input")

    def delete_message(self, receipt_handle):
        self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )

    #


sqs = SqsClient(queue_url='https://sqs.us-west-2.amazonaws.com/643068144265/testpranav.fifo')
while True:
    sqs.send_message()
    sqs.process_message()
    sqs.receive_message()
