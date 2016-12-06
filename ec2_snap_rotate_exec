import boto3
import logging
import datetime

ec = boto3.client('ec2')
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


def ec2_snap_rotate_exec(event, context):
    try:
        logging.info("Rotating snapshots")
        snapshot_id = event['snapshot_id']
        delete_on = get_deleteon_tag(snapshot_id, "DeleteOn")
        delete_on = datetime.datetime.strptime(delete_on, '%Y-%m-%d').date()

        if delete_on < today:
            logging.info("Deleting snapshot %s date %s" % (snapshot_id, delete_on))
            ec.delete_snapshot(DryRun=simulate, SnapshotId=snapshot_id)
        else:
            logging.info("Not rotate snapshot %s date %s" % (snapshot_id, delete_on))
    except Exception as e:
        logging.error("Unexpected error: %s" % e)
    return
