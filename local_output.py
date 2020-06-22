"""my god, its full of stars

my god, its full of stars

"""
import io
import boto3

from PIL import ImageDraw
from PIL import Image

s3_client = boto3.client('s3')


def draw_box(myimage, draw, bounding_box, line_width, linecolor):

    left = float(bounding_box['Left'])
    top = float(bounding_box['Top'])
    width = float(bounding_box['Width'])
    height = float(bounding_box['Height'])

    # box top left pixel coords in image
    tlx = myimage.size[0] * left
    tly = myimage.size[1] * top
    
    # box bottom right pixel coords in image
    brx = tlx + (myimage.size[0] * width)
    bry = tly + (myimage.size[1] * height)

    # draw box in image.
    for i in range(0, line_width):
        draw.rectangle(((tlx + i, tly + i), (brx - i, bry - i)), fill=None, outline=linecolor)


def paste_overlay(myimage, bounding_box, overlay):
    """Copy a transparent image on top of the original image.

    :param myimage:      Target image.
    :param bounding_box: Box descibing area to overlay. overlay will be aligned vertical centred.
    :param overlay:      Image to overlay.
    :return:
    """
    left = float(bounding_box['Left'])
    top = float(bounding_box['Top'])
    width = float(bounding_box['Width'])
    height = float(bounding_box['Height'])
    image_width = myimage.size[0]
    image_height = myimage.size[1]

    bb_centre_x = int(image_width * left) + int((image_width * width)/2)
    bb_centre_y = int(image_height * top) + int((image_height * height)/2)

    over_height = overlay.size[1]
    
    # so the top left of the overlay is the bb centre minus the height of the overlay.
    tl_over_x = bb_centre_x - int(over_height/2)
    tl_over_y = bb_centre_y - int(over_height/2)

    mask = overlay

    myimage.paste(overlay, (tl_over_x, tl_over_y), mask)


def get_face_data(bucket, photo):
    """send a request to the Rekognition detect_faces service and handle the response.

    :param bucket: string s3 bucket name
    :param photo: string image file name
    :return: list
    """
    client = boto3.client('rekognition')
    response = client.detect_faces(Image={'S3Object': {'Bucket': bucket, 'Name': photo}}, Attributes=['DEFAULT'])
    boxes = []

    for detail in response['FaceDetails']:
        boxes.append(detail['BoundingBox'])

    return boxes


def overlay_locations(target, overlay, locations, guides):
    # Draw on each face's bounding box

    with target as myimage:
        draw = ImageDraw.Draw(myimage)
        for face in locations:
            paste_overlay(myimage, face, overlay)
            if guides:
                draw_box(myimage, draw, face, 4, 'green')

    return target


def s3_get_image(bucket, key):
    file_byte_string = s3_client.get_object(Bucket=bucket, Key=key)['Body'].read()
    return Image.open(io.BytesIO(file_byte_string))


def main():
    photo_name = 'wikipeople1.jpg'
    overlay_name = 'laughing.png'
    # output_name = 'output.jpg'
    use_guides = True
    bucket = 'pez-rekog-image1'
    # output_path = '/tmp/output.jpg'
    output_path = '/io/output.jpg'

    # Run Rekognition.
    locations = get_face_data(bucket, photo_name)

    # Load overlay from S3 bucket.
    overlay = s3_get_image(bucket, overlay_name)

    # Load image containing faces from S3 bucket.
    target = s3_get_image(bucket, photo_name)

    target = overlay_locations(target, overlay, locations, use_guides)

    target.save(output_path)

    # s3_client.upload_file(output_path, bucket, output_name)

    print("Faces detected: " + str(len(locations)))


if __name__ == "__main__":
    main()
