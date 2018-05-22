from __future__ import print_function

import datetime
import os
import json
import pprint
import datetime
import boto3
from botocore.exceptions import ClientError


#
# Main handler
#
def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    status = True
    debug_enabled = False

    return status
