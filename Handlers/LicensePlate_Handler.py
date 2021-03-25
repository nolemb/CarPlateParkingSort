import re


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
