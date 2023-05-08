import boto3
from operator import itemgetter

ec2_client = boto3.client('ec2', region_name="us-east-1")
ec2_resource = boto3.resource('ec2', region_name="us-east-1")

instance_id = "<aws-instance-id>"

volumes = ec2_client.describe_volumes(
    Filters = [
        {
            'Name': 'attachment.instance-id',
            'Values': [instance_id]
        }
    ]
)

instance_volume = volumes['Volumes'][0] # expecting just one volume in the list for the instance

snapshots = ec2_client.describe_snapshots(
    OwnerIds = ['self'],
    Filters = [
        {
            'Name': 'volume-id',
            'Values': [instance_volume['VolumeId']]
        }
    ]
)

# grabbing the one latest snapshot
latest_snapshot = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)[0]

print(latest_snapshot['StartTime'])

# create the new volume
new_volume = ec2_client.create_volume(
    SnapshotId = latest_snapshot['SnapshotId'],
    AvailabilityZone = "us-east-1a",
    TagSpecifications = [
        {
            'ResourceType': 'volume',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'prod'
                }
            ]
        }
    ]
)

# attaching the volume to the ec2 instance
while True:
    vol = ec2_resource.Volume(new_volume['VolumeId'])
    print(vol.state)
    # only attach when the volume is available
    if vol.state == 'available':
        ec2_resource.Instance(instance_id).attach_volume(
            VolumeId = new_volume['VolumeId'],
            Device = '/dev/xvdb'
        )
        break