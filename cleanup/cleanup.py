import boto3

TARGET_TAG_KEY = 'Cleanup'
TARGET_TAG_VALUE = 'true'

def clean_ec2():
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances()

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}

            if tags.get(TARGET_TAG_KEY) == TARGET_TAG_VALUE:
                print(f"Terminating EC2 instance: {instance_id}")
                ec2.terminate_instances(InstanceIds=[instance_id])

if __name__ == '__main__':
    clean_ec2()
