import os
import re
from datetime import datetime
import time
import ocrspace
import redis
import validators


api = ocrspace.API()
r = redis.Redis(host='redis-10201.c92.us-east-1-3.ec2.cloud.redislabs.com',port=10201, db=0, password='Wy69cuWGscyW4x9sRPRh1Wj1IEAdOLs6')


def validate_user_input_type(user_input):
    """
    Validating the type of user input -> URL or FILE or invalid
    if the provided string is not a valid url or a valid file, will raise a TypeError exception
    :param user_input: str given by the user
    :return: if valid url or file will return str of user_input type -> URL or FILE, otherwise raise TypeError
    :raise TypeError: user_input is not a valid URL or FILE
    """
    if validators.url(user_input):
        print(f"User input is a valid URL [{user_input}]")
        input_type = "URL"
    elif os.path.isfile(user_input):
        print(f"User input is a valid FILE [{user_input}]")
        input_type = "FILE"
    else:
        raise TypeError(f"User input is not a valid URL or FILE, User input is [{user_input}]")

    return input_type


def extract_image_data(input_type, image):
    """
    Extracting text from a given image using ocrspace
    :param input_type: str of 'URL' or 'FILE' to determine in which txt extraction function to use
    :param image: str to the image url or file
    :return: image_data: extracted string from image
    :raise if ocr did not extract any txt from image, will raise en Exception
    """
    image_data = ''
    if input_type == "URL":
        # extracting txt from an image given as a url
        image_data = api.ocr_url(image)
    elif input_type == "FILE":
        # extracting txt from an image given as a file
        image_data = api.ocr_file(image)

    if not image_data:
        # input_type is not url/file or api.ocr_url / api.ocr_file did not extract any data
        raise Exception(f"OCR could not extract text from given image [{image}]")

    return image_data


def check_parking_access(licence_plate):
    """
    Check the type of the vehicle - Public Transportation, Military, Law Enforcement, No Letters, Private.
    If any of the above -> will insert the car plate number into a redis data base along with the vehicle type and a timestamp.
    :param licence_plate: str of the car plate
    :return:
    """
    licence_plate = licence_plate.strip()
    access = 0
    time_now = time.time()
    denied = "Denied"
    approved = "Approved"

    # checking if this vehicle is under Denied or Approved key - the vehicle has tried to enter in the past
    # updating the time it tried to enter now.
    if r.zrank(denied, licence_plate) is not None:
        print(f"Vehicle {licence_plate } has tried to enter in the past at {r.zscore(denied, licence_plate)} and was ==={denied}!===")
        r.zadd(denied, mapping={licence_plate: time_now})
        return 0
    elif r.zrank(approved, licence_plate) is not None:
        print(f"Vehicle {licence_plate } has tried to enter in the past at {r.zscore(denied, licence_plate)} and was ==={approved}!===")
        r.zadd(approved, mapping={licence_plate: time_now})
        return 1

    print(f"Vehicle {licence_plate} is not in data base, checking if it can access the parking lot")
    if licence_plate[-1] == '6' or licence_plate[-1] == 'G':
        car_type = 'Public Transportation'

    elif "L" in licence_plate or "M" in licence_plate:
        car_type = 'Military or Law Enforcement'

    elif not re.search('[a-zA-Z]', licence_plate):
        car_type = 'No letters'

    else:
        car_type = 'Private'
        access = 1

    result = approved if access else denied
    print(f"{licence_plate} car plate is a {car_type} vehicle type. The entrance to the parking lot is ==={result}!===")

    print(f"Inserting data into data base: key = {result}, value = {licence_plate}, score = {time_now}")
    r.zadd(result, mapping={licence_plate: time_now})
    print(f"Inserting data into data base: key = {car_type}, value = {licence_plate}, score = {time_now}")
    r.zadd(car_type, mapping={licence_plate: time_now})


input_msg = "Please enter a url or a path to a file of a car plate image\n"
user_input = input(input_msg)
while user_input:
    input_type = validate_user_input_type(user_input)
    licence_plate = extract_image_data(input_type, user_input)
    check_parking_access(licence_plate)
    user_input = input(input_msg)
