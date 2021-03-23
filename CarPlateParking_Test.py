import os
import re
from datetime import datetime
import ocrspace
import redis
import validators


api = ocrspace.API()
r = redis.Redis(host='redis-10201.c92.us-east-1-3.ec2.cloud.redislabs.com',
                port=10201, db=0, password='Wy69cuWGscyW4x9sRPRh1Wj1IEAdOLs6')


def validate_user_input_type(user_input):
    """
    Validating the type of user input -> URL or FILE or invalid
    if the provided string is not a valid url or a valid file, will return empty string -> False
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
    Extracting text from a given image
    :param input_type: str of URL or FILE to determine in which extraction function to use
    :param image: str to the image url or file
    :return: extracted string from image
    """
    image_data = ''
    if input_type == "URL":
        image_data = api.ocr_url(image)
    elif input_type == "FILE":
        image_data = api.ocr_file(image)

    if not image_data:
        raise Exception(f"OCR could not extract text from given image [{image}]")
    return image_data


def check_parking_access(image_data):
    """
    Check the type of the vehicle - Public Transportation, Military, Law Enforcement, No Letters, Private.
    If any of the above -> will insert the car plate number into a redis data base along with the vehicle type and a timestamp.
    :param image_data: str of the car plate
    :return:
    """
    image_data = image_data.strip()
    access = False
    car_type = ''
    msg = ''
    time = str(datetime.now())
    if image_data[-1] == '6' or image_data[-1] == 'G':
        car_type = 'Public Transportation'

    elif "L" in image_data or "M" in image_data:
        car_type = 'Military or Law Enforcement'

    elif not re.search('[a-zA-Z]', image_data):
        car_type = 'no letters'

    else:
        access = True

    if not access:
        print(f"{image_data} car plate is a {car_type} vehicle type which is not allowed in the parking lot\n"
              f"Access Denied!")
        r.hset(image_data, mapping={'type': car_type, 'timestamp': time})
    else:
        print(f"Congratulation! {image_data} may enter the parking lot!\n"
              f"Access Granted!")


input_msg = "please enter a url or a path to a file of a car plate image\n"
user_input = input(input_msg)
while user_input:
    input_type = validate_user_input_type(user_input)
    image_data = extract_image_data(input_type, user_input)
    check_parking_access(image_data)
    user_input = input(input_msg)



# print(r.hget(image_data, 'type'))
# print(r.hget(image_data, 'timestamp'))