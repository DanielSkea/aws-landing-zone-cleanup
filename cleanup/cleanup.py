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


def clean_s3():
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        bucket_tagging = boto3.client('s3')
        try:
            tags = bucket_tagging.get_bucket_tagging(Bucket=bucket.name)['TagSet']
            tag_dict = {tag['Key']: tag['Value'] for tag in tags}
            if tag_dict.get(TARGET_TAG_KEY) == TARGET_TAG_VALUE:
                print(f"Deleting S3 bucket: {bucket.name}")
                bucket.objects.all().delete()
                bucket.delete()
        except bucket_tagging.exceptions.ClientError:
            continue


def clean_lambda():
    client = boto3.client('lambda')
    functions = client.list_functions()['Functions']

    for function in functions:
        name = function['FunctionName']
        tags = client.list_tags(Resource=function['FunctionArn'])['Tags']
        if tags.get(TARGET_TAG_KEY) == TARGET_TAG_VALUE:
            print(f"Deleting Lambda function: {name}")
            client.delete_function(FunctionName=name)


def clean_ebs_volumes():
    ec2 = boto3.client('ec2')
    volumes = ec2.describe_volumes()['Volumes']

    for volume in volumes:
        tags = {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
        if tags.get(TARGET_TAG_KEY) == TARGET_TAG_VALUE:
            print(f"Deleting EBS Volume: {volume['VolumeId']}")
            ec2.delete_volume(VolumeId=volume['VolumeId'])


def clean_rds_instances():
    rds = boto3.client('rds')
    instances = rds.describe_db_instances()['DBInstances']

    for db in instances:
        arn = db['DBInstanceArn']
        tags = rds.list_tags_for_resource(ResourceName=arn)['TagList']
        tag_dict = {tag['Key']: tag['Value'] for tag in tags}
        if tag_dict.get(TARGET_TAG_KEY) == TARGET_TAG_VALUE:
            print(f"Deleting RDS Instance: {db['DBInstanceIdentifier']}")
            rds.delete_db_instance(
                DBInstanceIdentifier=db['DBInstanceIdentifier'],
                SkipFinalSnapshot=True,
                DeleteAutomatedBackups=True
            )


def clean_dynamodb_tables():
    dynamodb = boto3.client('dynamodb')
    tables = dynamodb.list_tables()['TableNames']

    for table in tables:
        tags = dynamodb.list_tags_of_resource(
            ResourceArn=f"arn:aws:dynamodb:{boto3.Session().region_name}:{boto3.client('sts').get_caller_identity()['Account']}:table/{table}"
        )['Tags']
        tag_dict = {tag['Key']: tag['Value'] for tag in tags}
        if tag_dict.get(TARGET_TAG_KEY) == TARGET_TAG_VALUE:
            print(f"Deleting DynamoDB table: {table}")
            dynamodb.delete_table(TableName=table)


if __name__ == '__main__':
    clean_ec2()
    clean_s3()
    clean_lambda()
    clean_ebs_volumes()
    clean_rds_instances()
    clean_dynamodb_tables()
