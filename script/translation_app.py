import datetime
from botocore.config import Config
from botocore.exceptions import ClientError
import boto3
from datetime import datetime
import os
import json

     #### environment variables
request_bucket = os.environ['REQUEST_BUCKET']
translated_bucket = os.environ['RESPONSE_BUCKET']

def translate_language(src_locale, target_locale, input_text):
    """Translate the input text from and to the specified languages by
    invoking the Amazon Translate API.


    Args:
        input: Contains following attributes
        src_locale: The ISO code of the language to translate from, e.g., 'en'.
        target_locale: The ISO code of the language to translate to, e.g., 'es'.
        text: the text to be translated.
    """
    print(f"Translating from '{src_locale}' to '{target_locale}'")

    try:
        config = Config(
            retries={
                'max_attempts': 10,
                'mode': 'standard'
            }
        )
        translate = boto3.client('translate', region_name='eu-north-1', use_ssl=True, config=config)

        response = translate.translate_text(
            Text=input_text,
            SourceLanguageCode=src_locale,
            TargetLanguageCode=target_locale
        )

        #### implementing s3 uploads
        data = response['TranslatedText']
        upload_request_text(request_bucket, input_text)
        upload_translated_text(translated_bucket, data)

    except ClientError as error:
        raise error

    print("Translated text: '{}'".format(response['TranslatedText']))
    return response['TranslatedText']


#####################
s3bucket = boto3.client('s3', region_name='eu-north-1')

def upload_request_text(request_bucket, data):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file_name = f"{timestamp}.txt"
    try:
        print(f'starting to upload files to {request_bucket}')
        s3bucket.put_object(Bucket=request_bucket,Key=file_name, Body=str(data))
        return True
    except ClientError as error:
        raise error
    


####
def upload_translated_text(translated_bucket, data):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file_name = f"{timestamp}.txt"
    try:
        print(f'starting to upload files to {translated_bucket}')
        s3bucket.put_object(Bucket=translated_bucket, Key=file_name, Body=str(data))
        return True
    except ClientError as error:
        raise error
