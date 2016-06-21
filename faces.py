#!/usr/bin/env python

import argparse
import base64
import json
import io

from googleapiclient import discovery
from googleapiclient import http
from oauth2client.client import GoogleCredentials


# [START get_vision_service]
DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'

def get_vision_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('vision', 'v1', credentials=credentials,
                           discoveryServiceUrl=DISCOVERY_URL)
# [END get_vision_service]


# [START get_storage_service]
def get_storage_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('storage', 'v1', credentials=credentials)
# [END get_storage_service]


# [START detect_face]
def detect_face(face_file, max_results=4):
    """Uses the Vision API to detect faces in the given file.

    Args:
        face_file: A file-like object containing an image with faces.

    Returns:
        An array of dicts with information about the faces in the picture.
    """
    image_content = face_file.read()
    batch_request = [{
        'image': {
            'content': base64.b64encode(image_content).decode('UTF-8')
            },
        'features': [{
            'type': 'FACE_DETECTION',
            'maxResults': max_results,
            }]
        }]

    service = get_vision_service()
    request = service.images().annotate(body={
        'requests': batch_request,
        })
    response = request.execute()

#    return response['responses'][0]['faceAnnotations']
    return response['responses'][0]
# [END detect_face]


# [START main]
def main(input_filename, max_results):
    with open(input_filename, 'rb') as image:
        bucket = 'adams-test-storage-api'
        destination = 'testjson.json'
	results = detect_face(image, max_results)
        print('Found %s face%s' % (len(results['faceAnnotations']), '' if len(results['faceAnnotations']) == 1 else 's'))
	body = {
	    'name': destination,
	}
        service = get_storage_service()
	req = service.objects().insert(
	    bucket=bucket, body=body,
	    media_body=http.MediaIoBaseUpload(io.BytesIO(str(json.dumps(results))), 'application/json'))

        resp = req.execute()

        print('> Composed files into {}'.format(destination))
        print(json.dumps(resp, indent=2))
        print '> Data exported:'
	print(json.dumps(results, indent=2))
# [END main]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Detects faces in the given image.')
    parser.add_argument(
        'input_image', help='the image you\'d like to detect faces in.')
    parser.add_argument(
        '--max-results', dest='max_results', default=4,
        help='the max results of face detection.')
    args = parser.parse_args()

    main(args.input_image, args.max_results)
