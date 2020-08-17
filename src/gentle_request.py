'''
This file is only here to provide information about creating and sending
gentle requests.
'''

import requests
import json

# After starting up the server on the localhost, you will communicated
# through this endpoint
GENTLE_ENDPOINT = "http://localhost:8765/transcriptions"


def main():
    # Create a transcript of what your audio says
    transcript = "stolen our lives like it he says peter please"
    # Set params that you want
    # Disfluency catches ums, errs, uhs
    # Conservative ensures a more consistent fit, but may exclude things
    params = (('async', 'false'), ('disfluency', 'false'),
              ('conservative', 'true'),)
    # Provide audio and transcript for your request
    files = {
        'audio': ('test.wav', open('test.wav', 'rb')),
        'transcript': ('words.txt', transcript),
    }
    # Send the request and capture the response
    # Response will be in the form of a JSON
    response = requests.post(
        GENTLE_ENDPOINT, params=params, files=files)
    print(response.text)


if __name__ == '__main__':
    main()
