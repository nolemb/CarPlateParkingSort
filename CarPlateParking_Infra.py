import os
import re
import time
import datetime
import validators
import ocrspace
import redis


class UserInputHandler:
    def __init__(self):
        """
        Getting an input from the user and handling it
        """
        input_msg = "\n\nPlease enter a url or a path to a file of a license plate image, Enter to terminate\n"
        self.user_input = input(input_msg)
        self.file_or_url = None  # if user input is a file or a url address this argument will be updated
        self.input_time = time.time()  # the time the user insert an input, will be used for the Redis DB

    def is_valid(self):
        """
        Validating the type of user input -> URL or FILE or invalid
        if the provided string is not a valid url or a valid file, will raise a TypeError exception
        :return: self.file_or_url -> if valid url or file will return str of user_input type -> URL or FILE,
                 otherwise raise TypeError
        :raise TypeError: user_input is not a valid URL or FILE
        """
        if not self.user_input:
            return self.user_input
        elif validators.url(self.user_input):
            print(f"User input is a valid URL [ {self.user_input} ]")
            self.file_or_url = "URL"
        elif os.path.isfile(self.user_input):
            print(f"User input is a valid FILE [ {self.user_input} ]")
            self.file_or_url = "FILE"
        else:
            raise TypeError(f"User input is not a valid URL or FILE, User input is [ {self.user_input} ]")

        return self.file_or_url

    def get_user_input(self):
        return self.user_input

    def get_input_type(self):
        return self.file_or_url

    def get_input_time(self):
        return self.input_time


class ImageHandler:
    def __init__(self, image_adrs='', file_or_url=None):
        """
        :param image_adrs: path to an image given by the user
        :param file_or_url: str of the type of the image_adrs -> URL or FILE
        """
        self.api = ocrspace.API()
        self.file_or_url = file_or_url
        self.image_adrs = image_adrs
        self.txt_from_image = ''

    def extract_txt_from_image(self):
        """
        Extracting text from a given image using ocrspace
        :param self.file_or_url: str of 'URL' or 'FILE' to determine in which txt extraction function to use
        :param self.image_adrs str to the image url or file
        :return: self.txt_from_image: extracted string from image
        :raise if ocr did not extract any txt from image, will raise an Exception
        """
        print("Extracting text from image using ocrspace")
        if not self.file_or_url:
            raise ValueError(
                f"Input type is empty or None. ocr input should be url or file address")
        elif self.file_or_url == "URL":
            # extracting txt from an image given as a url
            self.txt_from_image = self.api.ocr_url(self.image_adrs)
        elif self.file_or_url == "FILE":
            # extracting txt from an image given as a file
            self.txt_from_image = self.api.ocr_file(self.image_adrs)
        else:
            raise TypeError(
                f"ocrspace can handle only input type of url or file address. "
                f"your input type is [ {self.file_or_url} ]")

        if not self.txt_from_image:
            # input_type is not url/file or api.ocr_url / api.ocr_file did not extract any data
            raise Exception(
                f"Image does not contain text or OCR failed to extract text from given image [ {self.image_adrs} ]")
        print(f"Text extracted from [ {self.image_adrs} ] is [ {self.txt_from_image} ]")
        return self.txt_from_image


class LicensePlateHandler:
    def __init__(self, license_plate=''):
        """
        Handling with the license plate - validity, access to parking lot
        :param license_plate: str of a license plate
        """
        self.license_plate = license_plate.replace('\r\n', ' ').strip()
        self.car_type = None

    def is_valid(self):
        """
        Checking the validity of the license plate - empty, too long, too short
        :return: True if license_plate has content and its length is not too long and not too short, False otherwise
        """
        too_long = 60
        too_short = 6
        valid_license_plate = False
        if not self.license_plate:
            print("The license plate given text is empty")
        elif len(self.license_plate) > too_long:
            print(f"The license plate given text is too long. given text is [ {self.license_plate} ]")
        elif len(self.license_plate) < too_short:
            print(f"The license plate given text is too short. given text is [ {self.license_plate} ]")
        else:
            print("License plate length is Valid")
            valid_license_plate = True

        return valid_license_plate

    def check_parking_access(self):
        """
        Check the type of the vehicle - Public Transportation, Military, Law Enforcement, No Letters, Private.
        Inserting the data into a two redis sorted lists: approved or denied sorted sets and by car type sorted sets
        :return: True if access approved, False if denied
        """
        access = False
        denied = "Denied"
        approved = "Approved"

        print(f"Vehicle [ {self.license_plate} ] is not in data base, checking if it can access the parking lot")
        if self.license_plate[-1] == '6' or self.license_plate[-1] == 'G':
            self.car_type = 'Public Transportation'

        elif "L" in self.license_plate or "M" in self.license_plate:
            self.car_type = 'Military or Law Enforcement'

        elif not re.search('[a-zA-Z]', self.license_plate):
            self.car_type = 'No letters'

        else:
            self.car_type = 'Private'
            access = True

        result = approved if access else denied
        print(f"==={result}!=== [ {self.license_plate} ] license plate is a {self.car_type} vehicle type. "
              f"The entrance to the parking lot is {result}!")

        return access

    def get_license_plate(self):
        return self.license_plate

    def get_car_type(self):
        return self.car_type


def singleton(cls, *args, **kw):
    """
    Create a single instance of an object, in this case a single object of RedisDB
    Taken from: https://stackoverflow.com/questions/42237752/single-instance-of-class-in-python
    :param cls: class to create only once
    :param args: arguments passed to class constructor
    :param kw: keyword passed to class constructor
    :return: A single instance of the cls
    """
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class RedisDB:
    def __init__(self):
        """
        Handles the Redis data base - check if license plate is already in DB, insert license plate into DB
        :param self.redis_db holds the Redis client object
        """
        self.redis_db = redis.Redis(host='redis-10201.c92.us-east-1-3.ec2.cloud.redislabs.com',
                                    port=10201, db=0, password='Wy69cuWGscyW4x9sRPRh1Wj1IEAdOLs6')

    def check_in_db(self, license_plate, input_time):
        """
        Checking if this vehicle is under Denied or Approved key - the vehicle has tried to enter in the past
        updating the time it tried to enter now.
        :param input_time: the time the user entered the license_plate image input
        :param license_plate: str of license plate number
        :return: None if not in DB, True if in DB and entrance approved, False if in DB and entrance denied
        """
        denied = "Denied"
        approved = "Approved"
        access = None

        last_denied_time = self.redis_db.zscore(denied, license_plate)
        last_approved_time = self.redis_db.zscore(approved, license_plate)

        print("Checking if the vehicle has tried to enter in the past")

        if last_denied_time is not None:
            print(f"==={denied}!=== Vehicle [ {license_plate} ] has tried to enter in the past "
                  f"at {datetime.datetime.fromtimestamp(last_denied_time).strftime('%Y-%m-%dT%H:%M:%SZ')} "
                  f"and was {denied}")
            self.redis_db.zadd(denied, mapping={license_plate: input_time})
            access = False
        elif last_approved_time is not None:
            print(f"==={approved}!=== Vehicle [ {license_plate} ] has tried to enter in the past "
                  f"at {datetime.datetime.fromtimestamp(last_approved_time).strftime('%Y-%m-%dT%H:%M:%SZ')} "
                  f"and was {approved}")
            self.redis_db.zadd(approved, mapping={license_plate: input_time})
            access = True
        else:
            print(f"Vehicle [ {license_plate} ] hasn't tried to enter in the past")

        return access

    def save_to_db(self, license_plate, car_type, input_time, access):
        """
        Saving new vehicle into redis DB
        :param license_plate: license plate text
        :param access: bool, True if approved in parking lot, False otherwise
        :param car_type: str Public Transportation, Military, Law Enforcement, No Letters, Private
        :param input_time: the time the user entered the license_plate image input
        """
        denied = "Denied"
        approved = "Approved"
        result = approved if access else denied

        print(f"Inserting data into data base: key = {result}, value = {license_plate}, score = {input_time}")
        self.redis_db.zadd(result, mapping={license_plate: input_time})
        print(f"Inserting data into data base: key = {car_type}, value = {license_plate}, score = {input_time}")
        self.redis_db.zadd(car_type, mapping={license_plate: input_time})
