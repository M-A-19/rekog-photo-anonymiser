"""interim local testing

This file is an interim solution for the testing of lambda code locally.

"""
import json

from .modules.anonymiser import Anonymiser


def main():
    photo_name = 'wikipeople1.jpg'
    overlay_name = 'laughing.png'
    use_guides = True
    bucket = 'pez-rekog-image1'
    output_path = 'output.jpg'


    anony = Anonymiser()

    # Run Rekognition.
    locations = anony.get_face_data(bucket, photo_name)

    # Load overlay from S3 bucket.
    overlay = anony.s3_get_image(bucket, overlay_name)

    # Load image containing faces from S3 bucket.
    target = anony.s3_get_image(bucket, photo_name)

    target = anony.overlay_locations(target, overlay, locations, use_guides)

    target.save(output_path)

    output = {
        'timestamp': anony.processed,
        'jobtime': int(anony.jobtime * 1000),
        'facecount': str(len(locations)),
        'photo_name': photo_name,
    }

    print(json.dumps(output))



if __name__ == "__main__":
    main()
