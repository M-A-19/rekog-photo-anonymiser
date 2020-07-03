import json, boto3

from modules.anonymiser import Anonymiser

s3_client = boto3.client('s3')

def lambda_handler(event, context):

    if 'photo_name' in event.keys():
        photo_name = event['photo_name']
    else:
        photo_name = 'wikiperson1.jpg'

    bucket = 'pez-rekog-image1'
    overlay_name = 'laughing.png'
    use_guides = False
    output_path = '/tmp/output.jpg'
    output_name = 'output.jpg'

    # Start the anonymiser
    anony = Anonymiser()

    # Run Rekognition.
    locations = anony.get_face_data(bucket, photo_name)

    # Load overlay from S3 bucket.
    overlay = anony.s3_get_image(bucket, overlay_name)

    # Load image containing faces from S3 bucket.
    target = anony.s3_get_image(bucket, photo_name)

    target = anony.overlay_locations(target, overlay, locations, use_guides)

    target.save(output_path)

    s3_client.upload_file(output_path, bucket, output_name, ExtraArgs={'ACL': 'public-read'})

    output = {
        'isError' : False,
        'timestamp': anony.processed,
        'jobtime': int(anony.jobtime * 1000),
        'facecount': str(len(locations)),
        'photo_name': photo_name,
    }

    return output
