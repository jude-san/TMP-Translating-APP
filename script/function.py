import boto3
import json
from translation_app import translate_language, upload_request_text, upload_translated_text
from botocore.exceptions import ClientError
import time
import os
from typing import Dict, Any


############# refactored code by amazonQ #######

def get_environment_variables() -> Dict[str, str]:
    """Retrieve and validate required environment variables."""
    required_vars = ['REQUEST_BUCKET', 'RESPONSE_BUCKET']
    env_vars = {}
    
    for var in required_vars:
        if (value := os.environ.get(var)) is None:
            raise ValueError(f"Missing required environment variable: {var}")
        env_vars[var] = value
    
    return env_vars

def parse_request(event: Dict[str, Any]) -> Dict[str, str]:
    """Parse and validate the incoming request."""
    try:
        request = json.loads(event['body'])
        required_fields = ['src_locale', 'target_locale', 'input_text']
        
        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")
        
        return request
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Invalid request format: {str(e)}")

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create a standardized API response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler function."""
    print('request:', json.dumps(event))
    
    try:
        # Get environment variables
        env_vars = get_environment_variables()
        
        # Parse request
        request = parse_request(event)
        print("request:", request)
        
        # Extract request parameters
        src_locale = request['src_locale']
        target_locale = request['target_locale']
        input_text = request['input_text']
        
        # Perform translation
        start = time.perf_counter()
        translations = translate_language(src_locale, target_locale, input_text)
        time_diff = time.perf_counter() - start

        print(f"Translation result type: {type(translations)}")
        print(f"Translation result: {translations}")
        
        # Upload to S3
        # data = json.dumps(input_text)
        # upload_request_text(env_vars['REQUEST_BUCKET'], data)
        # upload_translated_text(env_vars['RESPONSE_BUCKET'], translations)
        
        
        return create_response(200, translations)
        
    except ValueError as e:
        return create_response(400, {"error": str(e)})
    except ClientError as e:
        return create_response(500, {"error": e.response['Error']['Code']})
    except Exception as e:
        return create_response(500, {"error": f"Unexpected error: {str(e)}"})




############################## code before refactoring ##############################
# _lambda = boto3.client('lambda')


# def handler(event, context):
#     print('request: {}'.format(json.dumps(event)))

#     request = json.loads(event['body'])
#     print("request", request)

#     src_locale = request['src_locale']
#     target_locale = request['target_locale']
#     input_text = request['input_text']

#     #### environment variables
#     request_bucket = os.environ['REQUEST_BUCKET']
#     translated_bucket = os.environ['RESPONSE_BUCKET']


#     try:
#         start = time.perf_counter()
#         translations = translate_language(src_locale, target_locale, input_text)
#         end = time.perf_counter()
#         time_diff = (end - start)

#         ##### implementing s3 uploads
#         data = json.dumps(input_text)
#         ### s3 request
#         upload_request_text(request_bucket, data)

#         upload_translated_text(translated_bucket, translations)


#         translations["processing_seconds"] = time_diff

#         return {
#             'statusCode': 200,
#             'headers': {
#                 'Content-Type': 'application/json'
#             },
#             'body': json.dumps(translations)
#         }

#     except ClientError as error:

#         error = {"error_text": error.response['Error']['Code']}
#         return {
#             'statusCode': 500,
#             'headers': {
#                 'Content-Type': 'application/json'
#             },
#             'body': json.dumps(error)
#         }
    
############# s3 standalone code for later code modularity
# def handler(event, context):
    # try:
    #     data = json.dumps(input_text)
    #     upload_request_text(request_bucket, data)
    #     upload_translated_text(translated_bucket, data)
    #     return {
    #         'statusCode': 200,
    #         'headers': {
    #             'Content-Type': 'application/json'
    #         },
    #         'body': json.dumps(data)
    #     }
    # except ClientError as error:
    #     error = {"error_text": error.response['Error']['Code']}
    #     return {
    #         'statusCode': 500,
    #         'headers': {
    #             'Content-Type': 'application/json'
    #         },
    #         'body': json.dumps(error)
    #     }
        


####

