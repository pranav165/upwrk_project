import datetime
import uuid
import boto3
import json
from retry import retry
from datetime import date, datetime
import requests

requests.packages.urllib3.disable_warnings()

client = boto3.client('sqs', aws_access_key_id='AKIATIQOEEPMUU7IFPXH',
                      aws_secret_access_key='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',
                      region_name='eu-west-2', verify=False)
queue_url = 'https://sqs.eu-west-2.amazonaws.com/565045766653/BALAG711171VK9GP_SYS.fifo'


def send_message(id, result=None):
    payload = {
        "timeSlotId": id,
        "date": date.today().strftime("%d/%m/%Y"),
        "datetimeOfTest": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    if result == 1:
        payload["result"] = "accepted"
    elif result == 2:
        payload["result"] = "rejected"
    client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(payload),
        MessageGroupId=id
    )
    print("SENDER ------> Sending Message with payload as {}".format(payload))


@retry(Exception, tries=4, delay=2)
def receive_message():
    response = client.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['All']
    )
    print("RECEIVER ------> Received a message with payload {}".format(response['Messages'][0]['Body']))

    receipt_handle = response['Messages'][0]['ReceiptHandle']
    delete_message(receipt_handle)


def process_message(id):
    receive_message()
    answer = int(input("Enter 1 to select 2 to reject"))
    if answer == 1:
        print("\n Accepted")
        send_message(id, 1)
    elif answer == 2:
        print("\n Rejected")
        send_message(id, 2)
    else:
        print("Wrong input")


def delete_message(receipt_handle):
    client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )


#
while True:
    id = str(uuid.uuid1())
    send_message(id)
    process_message(id)
    receive_message()
