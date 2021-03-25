import datetime
import redis


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
        # host='localhost', port=6379, db=0 are default
        self.redis_db = redis.Redis()

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
