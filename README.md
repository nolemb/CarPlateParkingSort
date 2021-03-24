# CarPlateParkingSort
This program gets an input from the user: path to a file, or an url which contains an image of a license plate.
The image is being processed by ocrspace to extract the txt of the license plate.
The program decides if the vehicle may enter the parking lot by these rules:
1) '6' or 'G' at the end of the license plate is for Public Transportation -> access to parking lot is denied
2) inclusion of 'M' or 'L' in the license plate is for Military and Law Enforcement vehicles -> access to parking lot is denied
3) license plate the does not contain any latter -> access to parking lot is denied

License plate, vehicle type, time of the attempt to enter, approved or denied entrance is stored in redis DB.

User can check one input at a time, as meany times he wants.
To terminate, user should use the 'Enter' key for an empty input.

Installation
Simply install from pip:
pip install ocrspace
pip install redis
pip install requests

Requirements:
Running redis locally or use cloud redis
local: r = redis.Redis(host=localhost,port=6379, db=0)
cloud: register to RdisLabs cloud at https://redislabs.com/redis-enterprise-cloud/overview/
        you will get a host, port and a password.


OCR Exceptions are handled by OCR, for example:
timeout
not a valid file format
