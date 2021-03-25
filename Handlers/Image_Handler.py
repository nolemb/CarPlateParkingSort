import ocrspace


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
