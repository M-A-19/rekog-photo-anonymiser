## Rekog Photo Anonymiser
Photo facial anonymiser using AWS Rekognition. to identify and obscure faces within a photograph.

## Intention
I had the intent to detect faces in a photo using my existing knowledge of Keras/tensorflow
Then I discovered that AWS provides this as a service called Rekognition.

This project provides Lambda function to query Rekognition and use the results to obscure the photo data in the identified regions.

My first attempt at this used virtualenv, but AWS didn't like the virtualenv generated on my mac, so this repo includes a Dockerfile to spin up a lambda image for building the Python deployment package.

## Code style
Python code compliant to the pep-8 standard.

[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
 
## License
MIT license