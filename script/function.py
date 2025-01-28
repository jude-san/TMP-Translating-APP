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


translate = boto3.client(service_name='translate', region_name='eu-north-1', use_ssl=True)
# result = translate.translate_text(Text="ich bin ein Berliner", 
#             SourceLanguageCode="de", TargetLanguageCode="en")
# print('TranslatedText: ' + result.get('TranslatedText'))
# print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
# print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))


# Translate a document
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


# To use S3 resource
# s3 = boto3.resource('s3')

# Print out bucket names
# for bucket in s3.buckets.all():
#     while True:
#         print(bucket.name)
    # print(bucket.name)


# Upload a new file
# with open('test.jpg', 'rb') as data:
#     s3.Bucket('amzn-s3-demo-bucket').put_object(Key='test.jpg', Body=data)

def upload_request(bucket_name, file_name):
    with open(file_name, 'rb') as data:
        s3.Bucket(bucket_name).put_object(Key=file_name, Body=data)



def upload_translated_file(bucket_name, file_name):
    with open(file_name, 'rb') as data:
        s3.Bucket(bucket_name).put_object(Key=file_name, Body=data)

def translate_request(bucket_name, file_name):
    # Translate the file
    # Get the file from the bucket
    # Translate the file
    # Upload the translated file to the bucket
    pass