# CarPlateParkingSort
This program gets an input from the user: path to a file, or an url which contains an image of a license plate.
The image is being processed by ocrspace to extract the text of the license plate.
The program decides if the vehicle may enter the parking lot by these rules:
1. '6' or 'G' at the end of the license plate is for Public Transportation -> access to parking lot is denied
2. inclusion of 'M' or 'L' in the license plate is for Military and Law Enforcement vehicles -> access to parking lot is denied
3. license plate the does not contain any latter -> access to parking lot is denied

License plate, vehicle type, time of the attempt to enter, approved or denied entrance is stored in redis DB.

User can check one input at a time, as meany times he wants.

## Installation
1. Python 3.5 and up
Simply install from pip:
2. pip install ocrspace
3. pip install redis
4. pip install requests

## Requirements:
Running redis locally or use cloud redis
 local: `redis.Redis(host=localhost,port=6379)`, those are the default values
 cloud: register to [RdisLabs cloud](https://redislabs.com/redis-enterprise-cloud/overview/)
  You will get a host, port and a password.
  Inset in the module `Redis_DB`, in `self.redis_db = redis.Redis()`
  `redis.Redis(host='your host', port= your port, password='your password')`

## Program will be terminated in the following cases: 
1. To terminate, user should use the 'Enter' key for an empty input.
2. User input is invalid
3. ocrspace exception
4. ocrspace failed to extract text from image
5. Image does not contain any text

## OCRSPACE Exceptions are handled by OCRSPACE, for example:
1. timeout
2. Not a valid file format
3. Unable to recognize the file type
4. If you are using Redis as a FREE user you might encounter this exception:
  "Exception: You may only perform this action up to maximum 10 number of times within 600 seconds"

