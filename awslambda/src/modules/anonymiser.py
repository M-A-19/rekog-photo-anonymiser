"""Methods for modifying images using data returned from the AWS Rekog service.

"""
import io, os
from time import gmtime, strftime, perf_counter

import boto3
from PIL import ImageDraw
from PIL import Image
from PIL import ImageFont


class Anonymiser(object):
    """
    Methods for modifying images using data returned from the AWS Rekog service.
    """
    def __init__(self):
        """
        Constructor
        """
        self.s3_client = boto3.client('s3')
        self.start = 0
        self.jobtime = 0
        self.processed = ''
        # can we get rekog time used also?


    def position_from_bounding_box(self, bounding_box, x_context, y_context):
        """Derive pixel co-ords from relative positions returned by the service.

        :param (dict) bounding_box: Relative box location and dimension.
        :param (int)  x_context:    Width of target image.
        :param (int)  y_context:    Height of target image.
        :return (list):
        """
        left = float(bounding_box['Left'])
        top = float(bounding_box['Top'])
        width = float(bounding_box['Width'])
        height = float(bounding_box['Height'])

        # box top left pixel coords in image
        tlx = int(x_context * left)
        tly = int(y_context * top)

        # box bottom right pixel coords in image
        brx = tlx + int(x_context * width)
        bry = tly + int(y_context * height)

        return (tlx, tly), (brx, bry)

    def draw_text(self, draw, text, x_context, y_context):
        """
        Write text into an image.

        :param (obj) draw: Drawing library handle.
        :param (str) text: Text to write into image.
        :param (int) x_context:    Width of target image.
        :param (int) y_context:    Height of target image.
        :return:
        """
        # get a font
        fnt = ImageFont.truetype(os.environ['FONT_DIR'] + '/FreeMono.ttf', 40)
        text_width, text_height = draw.textsize(text, fnt)

        # draw text, half opacity
        draw.text((x_context - text_width, y_context - text_height), text, font=fnt, fill=255)


    def draw_box(self, draw, coords, style):
        """
        Draw a rectangle in a given image using passed coords and style attributes.

        :param (obj)  draw:     Drawing library handle.
        :param (list) coords:   Co-ords to locate box at.
        :param (dict) style:    Styling information for line.
        :return:
        """

        # draw box in image.
        for i in range(0, style['line_width']):
            tplt = (coords[0][0] + i, coords[0][1] + i)
            btrt = (coords[1][0] + i, coords[1][1] + i)
            draw.rectangle((tplt, btrt), fill=None, outline=style['linecolor'])

    def find_box_centre(self, coords):
        """
        Find the centre coords of a box from a pair of corner tuples.

        :param (list) coords:   Co-ords to locate box at.
        :return (list): list of tuples, top-left, bottom-right.
        """
        # The center of rectangle is the mid point of the diagonal end points of rectangle.
        return int((coords[0][0] + coords[1][0])/2), int((coords[0][1] + coords[1][1])/2)

    def paste_overlay(self, myimage, coords, overlay):
        """Copy a transparent image on top of the original image.

        :param (obj)  myimage:  Target image.
        :param (list) coords:   Co-ords to locate box at.
        :param (obj)  overlay:  Image to overlay.
        :return:
        """

        box_centre = self.find_box_centre(coords)
        over_height = overlay.size[1]

        # so the top left of the overlay is the bb centre minus the height of the overlay.
        tl_over_x = box_centre[0] - int(over_height/2)
        tl_over_y = box_centre[1] - int(over_height/2)

        mask = overlay
        myimage.paste(overlay, (tl_over_x, tl_over_y), mask)

    def get_face_data(self, bucket, photo):
        """send a request to the Rekognition detect_faces service and handle the response.

        :param (str) bucket: s3 bucket name
        :param (str) photo:  image file name
        :return: list
        """
        client = boto3.client('rekognition')
        s3bucket = {'S3Object': {'Bucket': bucket, 'Name': photo}}
        response = client.detect_faces(Image=s3bucket, Attributes=['DEFAULT'])
        boxes = []

        for detail in response['FaceDetails']:
            boxes.append(detail['BoundingBox'])

        return boxes

    def s3_get_image(self, bucket, key):
        """

        :param (str) bucket: s3 bucket name
        :param (str) key:
        :return:
        """
        file_byte_string = self.s3_client.get_object(Bucket=bucket, Key=key)['Body'].read()
        return Image.open(io.BytesIO(file_byte_string))

    def overlay_locations(self, target, overlay, locations, guides):
        """
        Write an overlay image at a list of face locations in an image.

        :param (obj)  target:    Target image.
        :param (obj)  overlay:   Image to overlay.
        :param (list) locations: list of face location co-ords.
        :param (bool) guides:    Include guides?
        :return:
        """
        # Draw on each face's bounding box

        with target as myimage:
            draw = ImageDraw.Draw(myimage)
            self.processed = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            jobstart = perf_counter()
            for face in locations:
                box = self.position_from_bounding_box(face, target.size[0], target.size[1])
                self.paste_overlay(myimage, box, overlay)
                self.draw_text(draw, self.processed, target.size[0], target.size[1])
                if guides:
                    self.draw_box(draw, box, {'line_width': 4, 'linecolor': 'green'})
        self.jobtime = perf_counter() - jobstart
        return target
