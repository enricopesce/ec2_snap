import boto3
import logging
import datetime
import json

ec = boto3.client('ec2')
cli_lambda = boto3.client('lambda')
simulate = False
logger = logging.getLogger()
logger.setLevel(logging.INFO)
today = datetime.date.today()


def get_deleteon_tag(id, tag_name):
    res_ec2 = boto3.resource('ec2')
    tags = res_ec2.Snapshot(id).tags
    for tag in tags:
        if tag['Key'] == tag_name:
            return tag['Value']
    return ""


def ec2_snap_rotate_invoke(event, context):
    logging.info("Rotating snapshots")

    filters = [{'Name': 'tag-key', 'Values': ['DeleteOn']}]
    snapshot_response = ec.describe_snapshots(Filters=filters)

    for snap in snapshot_response['Snapshots']:
        # call lambda function tu execute the specific instance task
        context = json.dumps({'snapshot_id': snap['SnapshotId']})
        cli_lambda.invoke(FunctionName='ec2_snap_rotate_exec.py', InvocationType='Event', Payload=context)
