import os
import re
import time
import ocrspace
import redis
import validators


api = ocrspace.API()
redis_db = redis.Redis(host='redis-10201.c92.us-east-1-3.ec2.cloud.redislabs.com',
                       port=10201, db=0, password='Wy69cuWGscyW4x9sRPRh1Wj1IEAdOLs6')


def validate_user_input_type(user_input):
    """
    Validating the type of user input -> URL or FILE or invalid
    if the provided string is not a valid url or a valid file, will raise a TypeError exception
    :param user_input: str given by the user
    :return: if valid url or file will return str of user_input type -> URL or FILE, otherwise raise TypeError
    :raise TypeError: user_input is not a valid URL or FILE
    """
    if validators.url(user_input):
        print(f"User input is a valid URL [ {user_input} ]")
        input_type = "URL"
    elif os.path.isfile(user_input):
        print(f"User input is a valid FILE [ {user_input} ]")
        input_type = "FILE"
    else:
        raise TypeError(f"User input is not a valid URL or FILE, User input is [ {user_input} ]")

    return input_type


def extract_txt_from_image(input_type, image):
    """
    Extracting text from a given image using ocrspace
    :param input_type: str of 'URL' or 'FILE' to determine in which txt extraction function to use
    :param image: str to the image url or file
    :return: image_data: extracted string from image
    :raise if ocr did not extract any txt from image, will raise an Exception
    """
    print("Extracting text from image using ocrspace")
    image_data = ''
    if input_type == "URL":
        # extracting txt from an image given as a url
        image_data = api.ocr_url(image)
    elif input_type == "FILE":
        # extracting txt from an image given as a file
        image_data = api.ocr_file(image)

    if not image_data:
        # input_type is not url/file or api.ocr_url / api.ocr_file did not extract any data
        raise Exception(f"Image does not contain text or OCR failed to extract text from given image [ {image} ]")

    print(f"Text extracted from [ {image} ] is [ {image_data} ]")
    return image_data


def check_license_plate(txt):
    """
    Checking the validity of the license plate
    :param txt: str that holds the license plate
    :return:
    """
    if not txt:
        raise ValueError("The car license given txt is empty")
    txt = txt.replace('\r\n', ' ').strip()
    return txt


def check_parking_access(license_plate):
    """
    Check the type of the vehicle - Public Transportation, Military, Law Enforcement, No Letters, Private.
    Inserting the data into a two redis sorted lists: approved or denied sorted sets and by car type sorted sets
    :param license_plate: str of the car plate
    :return: 1 if access approved, 0 if denied
    """
    # license_plate = license_plate.strip()
    access = 0
    time_now = time.time()
    denied = "Denied"
    approved = "Approved"

    # checking if this vehicle is under Denied or Approved key - the vehicle has tried to enter in the past
    # updating the time it tried to enter now.
    if redis_db.zrank(denied, license_plate) is not None:
        print(f"==={denied}!=== Vehicle [ {license_plate} ] has tried to enter in the past "
              f"at {redis_db.zscore(denied, license_plate)} and was {denied}")
        redis_db.zadd(denied, mapping={license_plate: time_now})
        return 0
    elif redis_db.zrank(approved, license_plate) is not None:
        print(f"==={approved}!=== Vehicle [ {license_plate} ] has tried to enter in the past "
              f"at {redis_db.zscore(approved, license_plate)} and was {approved}")
        redis_db.zadd(approved, mapping={license_plate: time_now})
        return 1

    print(f"Vehicle [ {license_plate} ] is not in data base, checking if it can access the parking lot")
    if license_plate[-1] == '6' or license_plate[-1] == 'G':
        car_type = 'Public Transportation'

    elif "L" in license_plate or "M" in license_plate:
        car_type = 'Military or Law Enforcement'

    elif not re.search('[a-zA-Z]', license_plate):
        car_type = 'No letters'

    else:
        car_type = 'Private'
        access = 1

    result = approved if access else denied
    print(f"==={result}!=== [ {license_plate} ] car plate is a {car_type} vehicle type. The entrance to the parking lot is {result}!")

    print(f"Inserting data into data base: key = {result}, value = {license_plate}, score = {time_now}")
    redis_db.zadd(result, mapping={license_plate: time_now})
    print(f"Inserting data into data base: key = {car_type}, value = {license_plate}, score = {time_now}")
    redis_db.zadd(car_type, mapping={license_plate: time_now})

    return access


if __name__ == "__main__":
    input_msg = "Please enter a url or a path to a file of a car plate image, Enter to terminate\n"
    user_input = input(input_msg)
    while user_input:
        input_type = validate_user_input_type(user_input)
        txt_from_image = extract_txt_from_image(input_type, user_input)
        license_plate = check_license_plate(txt_from_image)
        entrance = check_parking_access(license_plate)
        user_input = input(input_msg)
