import os
import time
import validators


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
