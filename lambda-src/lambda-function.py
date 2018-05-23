from __future__ import print_function

import os
import json
import pprint
from datadog import initialize, api
from pprint import pprint, pformat

def parse_tags(tag_str):
    '''
    Parse the list of tags passed in the environment
    :param tag_str: Raw list of tags
    :return: array
    '''
    dd_formatted_tags = []
    tag_list = tag_str.split(',')

    # DD tags are an arrary where each element is tag:value.  ie.
    # tags = ['version:1', 'application:web']
    for tag in tag_list:
        tag_name, tag_value = tag.split('=', 1)
        dd_formatted_tags.append(tag_name + ':' + tag_value)

    return dd_formatted_tags

def send_datadog_event(priority, type, title, text):
    print("Sending Datadog event")
    status = True

    host = 'deepsecurity'
    source_type_name = 'IMMUNIO' # Cannot have custom event sources, use one that is security related

    # Init credentials
    options = {
        'api_key': os.environ['DatadogAPIKey'],
        'app_key': os.environ['DatadogAppKey']
    }
    initialize(**options)

    tags = parse_tags(os.environ['DatadogTags'])

    response = api.Event.create(priority=priority, alert_type=type, title=title, text=text, tags=tags, host=host, source_type_name=source_type_name)

    if response['status'] == 'ok':
        status = True
    else:
        print("Error submitting event to datadog:" + pformat(response))
        status = False

    return status

#
# Main handler
#
def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    status = True
    ds_event_levels_to_report = []
    min_rank_to_send = 0

    ds_event_dict = json.loads(event['Records'][0]['Sns']['Message'])[0]

    # Which severity DS events should we send to Datadog?
    if os.environ['EventFilter'].lower() != 'all':
        print("Sending events to Datadog for Deep Security events at severities " + os.environ['EventFilter'])
        ds_event_levels_to_report = os.environ['EventFilter'].split(',')
    else:
        print("Sending events to Datadog for all severity Deep Security events")
        ds_event_levels_to_report.append('all')

    # which rank events should we send to Datadog?
    if 'RankGreater' in os.environ:
        min_rank_to_send = int(os.environ['RankGreater'])
        print("Will only send DS events with rank > " + str(min_rank_to_send) + " to Datadog")

    # get the severity and rank from the event
    current_event_severity = ds_event_dict['OSSEC_Level']
    current_rank = ds_event_dict['Rank']

    if current_rank >= min_rank_to_send:
        if 'all' in ds_event_levels_to_report or str(current_event_severity) in ds_event_levels_to_report:
            host = ds_event_dict['Hostname']
            severity_string = ds_event_dict['SeverityString']

            print("Level " + str(current_event_severity) + " DS event found with severity "
                           + severity_string + " and rank " + str(current_rank) + ". Sending to Datadog")

            if (current_rank >= 100):
                type = 'error'
            else:
                type = 'info'

            priority = "normal"
            type = 'warning'
            title = "DS event on  " + host

            text = "%%% \n"
            text += "**" + ds_event_dict['EventType'] + "** detected on " + host + "\n"
            text += "**Severity:** " + severity_string + "\n"
            text += "**Rank:** " + str(current_rank) + "\n"
            text += "**Description:** " + ds_event_dict['OSSEC_Description'] + "\n"
            text += "- - -" + "\n"
            text += "\n %%%"

            response = send_datadog_event(priority, type, title, text)

            if response:
                print("Successfully sent event to Datadog")
            else:
                status = False

    return status
