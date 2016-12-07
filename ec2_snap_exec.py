import logging
import boto3
import datetime


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
simulate = False


def get_instance_tag(id, tag_name):
    res_ec2 = boto3.resource('ec2')
    tags = res_ec2.Instance(id).tags
    for tag in tags:
        if tag['Key'] == tag_name:
            return tag['Value']
    return id


def get_volume_tag(id, tag_name):
    res_ec2 = boto3.resource('ec2')
    tags = res_ec2.Volume(id).tags
    for tag in tags:
        if tag['Key'] == tag_name:
            return tag['Value']
    return id


def snapshots_by_instance(instance, delete_date, mode):
    devices = instance.block_device_mappings
    inst_id = instance.instance_id
    inst_name = get_instance_tag(inst_id, "Name")
    mode_type = "HOT-SNAPSHOT"

    try:
        if mode == 'cold':
            res_instance = boto3.resource('ec2').Instance(inst_id)
            res_instance.stop(DryRun=simulate)
            logging.info("Stopping instance %s" % inst_name)
            res_instance.wait_until_stopped()
            logging.info("Stopped instance %s" % inst_name)
            mode_type = "COLD-SNAPSHOT"

        for dev in devices:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            vol_name = get_volume_tag(vol_id, "Name")
            dev_name = dev['DeviceName']
            volume = boto3.resource('ec2').Volume(vol_id)
            logging.info("Snapshotting instance %s (%s) mode %s device %s" % (inst_id, inst_name, mode_type, dev_name))
            res_snap = volume.create_snapshot(DryRun=simulate)
            res_snap.create_tags(DryRun=simulate, Tags=[{'Key': 'Name', 'Value': vol_name},
                                                        {'Key': 'DeviceName', 'Value': dev_name},
                                                        {'Key': 'InstanceName', 'Value': inst_name},
                                                        {'Key': 'VolumeID', 'Value': vol_id},
                                                        {'Key': 'SnapMode', 'Value': mode_type},
                                                        {'Key': 'DeleteOn', 'Value': delete_date}])

        logging.info("Snapshots finished")

        if mode == "cold":
            logging.info("Starting instance %s %s" % (inst_id, inst_name))
            res_instance.start(DryRun=simulate)
    except Exception as e:
        logging.error("Unexpected error: %s" % e)
        #se spenta la instance va riaccesa
    return


#lambda call
def ec2_snap_exec(event, context):
    try:
        instance = boto3.resource('ec2').Instance(event['instance_id'])
        days = int(event['retention'])
        delete_date = datetime.date.today() + datetime.timedelta(days=days)
        mode = event['mode']
    except Exception as e:
        logging.error("Unexpected error: %s" % e)
    else:
        snapshots_by_instance(instance, delete_date.strftime('%Y-%m-%d'), mode)
    return
