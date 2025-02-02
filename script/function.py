import boto3
import json
# from botocore.config import Config # Import Config from botocore.config && use it to configure the boto3 client


# to configure resource use the following code on a specific region and resource
# my_config = Config(
#     region_name = 'eu-north-1',
#     signature_version = 'v4',
#     retries = {
#         'max_attempts': 10,
#         'mode': 'standard'
#     }
# )
#  Example of how to configure the client
# client = boto3.client('kinesis', config=my_config)



# # Translate a document ############# It works

translate = boto3.client(service_name='translate', region_name='eu-north-1', use_ssl=True)
s3bucket = boto3.client('s3', region_name='eu-north-1')


# BUCKET_NAME = 'tryouta'


with open('input_file.json', 'r') as file:
        data = json.load(file)

        info = data['Content']
        # print(info)

result2 = translate.translate_document(Document={'Content': info, 'ContentType':'text/plain'}, SourceLanguageCode='en',
    TargetLanguageCode='fr')

TranslatedDocument = result2.get('TranslatedDocument')

print(f"{TranslatedDocument['Content'].decode('utf-8')}")
print('SourceLanguageCode: ' + result2.get('SourceLanguageCode'))
print('TargetLanguageCode: ' + result2.get('TargetLanguageCode'))



### print out the list of buckets using prefix attribute or remove prefix to get all buckets in AWS account(Not recommended)
def list_bucket(name):
    ### getting list of buckets using in a specific region helps in debugging
    response = s3bucket.list_buckets(
        Prefix= name,
    )

    list_bucket = ''
    ### Output the bucket names
    # print('Existing buckets:')
    for bucket in response['Buckets']:
        # print(f'  {bucket["Name"]}')
        if name == bucket['Name']:
            list_bucket += bucket['Name']
        else:
            exit(1)
    # print(f' in def list_bucket = {list_bucket}')
    return list_bucket

### using variable: BUCKET_NAME & Function: list_bucket to search for the bucket existence
# name = list_bucket(BUCKET_NAME)
# print(f'Bucket found = {name}')








### Upload a new file
### with open('test.jpg', 'rb') as data:

# s3.Bucket('amzn-s3-demo-bucket').put_object(Key='test.jpg', Body=data)

def upload_request(bucket_name, file_name):
    with open(file_name, 'rb') as data:
        s3bucket.Bucket(bucket_name).put_object(Key=file_name, Body=data)



def upload_translated_file(bucket_name, file_name):
    with open(file_name, 'rb') as data:
        s3bucket.Bucket(bucket_name).put_object(Key=file_name, Body=data)

def translate_request(bucket_name, file_name):
    # Translate the file
    # Get the file from the bucket
    # Translate the file
    # Upload the translated file to the bucket
    
    with open('input_file.json', 'r') as file:
        data = json.load(file)

    info = data['Content']
    # print(info)

    result2 = translate.translate_document(Document={'Content': info, 'ContentType':'text/plain'}, SourceLanguageCode='en',
        TargetLanguageCode='fr')

    TranslatedDocument = result2.get('TranslatedDocument')

    print(f"{TranslatedDocument['Content'].decode('utf-8')}")
    print('SourceLanguageCode: ' + result2.get('SourceLanguageCode'))
    print('TargetLanguageCode: ' + result2.get('TargetLanguageCode'))
