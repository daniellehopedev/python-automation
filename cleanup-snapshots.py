import boto3
from operator import itemgetter

ec2_client = boto3.client('ec2', region_name="us-east-1")

volumes = ec2_client.describe_volumes(
    Filters = [
        {
            'Name': 'tag:Name',
            'Values': ['prod']
        }
    ]
)

for volume in volumes['Volumes']:
    # only get the snapshots created by me, filter out snapshots created by aws
    # in Filters, grabbing snapshots that belong to a volume in the volumes list
    snapshots = ec2_client.describe_snapshots(
        OwnerIds = ['self'],
        Filters = [
            {
                'Name': 'volume-id',
                'Values': [volume['VolumeId']]
            }
        ]
    )

# sort the snapshots list by date, with most recent first
sorted_by_date = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse = True)

# delete all snapshots except for the 2 most recent, first two in the list
for snap in sorted_by_date[2:]:
    response = ec2_client.delete_snapshot(
        SnapshotId = snap['SnapshotId']
    )
    print(response)