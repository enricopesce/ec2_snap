import boto3
import logging
import json

simulate = False
retention_days = 15

logger = logging.getLogger()
logger.setLevel(logging.INFO)
cli_lambda = boto3.client('lambda')
cli_ec2 = boto3.client('ec2')

#lambda call
def ec2_snap_invoke(event, context):
    filters = [{'Name': 'tag:Backup', 'Values': ['NOREBOOT']}]

    reservations = cli_ec2.describe_instances(Filters=filters).get('Reservations', [])
    instances = sum([[i for i in r['Instances']]for r in reservations], [])
    logging.info("Found  %d instances that need backing up in HOT mode" % len(instances))

    for instance in instances:
        #call lambda function tu execute the specific instance task
        context = json.dumps({'instance_id': instance['InstanceId'],
                              'retention': retention_days,
                              'mode': 'hot'})
        cli_lambda.invoke(FunctionName='ec2_snap_exec.py', InvocationType='Event', Payload=context)

    filters = [{'Name': 'tag:Backup', 'Values': ['REBOOT']}]

    reservations = cli_ec2.describe_instances(Filters=filters).get('Reservations', [])
    instances = sum([[i for i in r['Instances']] for r in reservations], [])
    logging.info("Found  %d instances that need backing up in COLD mode" % len(instances))

    for instance in instances:
        # call lambda function tu execute the specific instance task
        context = json.dumps({'instance_id': instance['InstanceId'],
                              'retention': retention_days,
                              'mode': 'cold'})
        cli_lambda.invoke(FunctionName='ec2_snap_exec.py', InvocationType='Event', Payload=context)
