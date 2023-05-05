import boto3

ec2_client_virginia = boto3.client('ec2', region_name="us-east-1")
ec2_resource_virginia = boto3.client('ec2', region_name="us-east-1")

ec2_client_california = boto3.client('ec2', region_name="us-west-1")
ec2_resource_california = boto3.client('ec2', region_name="us-west-1")

instance_ids_va = []
instance_ids_ca = []

reservations_va = ec2_client_virginia.describe_instances()['Reservations']
for res in reservations_va:
    instances = res['Instances']
    for ins in instances:
        instance_ids_va.append(ins['InstanceId'])

response = ec2_resource_virginia.create_tags(
    Resources = instance_ids_va,
    Tags = [
        {
            'Key': 'environment',
            'Value': 'prod'
        }
    ]
)

reservations_ca = ec2_client_california.describe_instances()['Resercations']
for res in reservations_ca:
    instances = res['Instances']
    for ins in instances:
        instance_ids_ca.append(ins['InstanceId'])

response = ec2_resource_california.create_tags(
    Resources = instance_ids_ca,
    Tags = [
        {
            'Key': 'environment',
            'Value': 'dev'
        }
    ]
)