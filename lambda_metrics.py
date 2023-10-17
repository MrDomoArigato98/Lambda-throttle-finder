import json
import boto3
import datetime
import pprint
from datetime import timedelta
import argparse
cw = boto3.client('cloudwatch')
client = boto3.client('lambda')
paginator = client.get_paginator('list_functions')

#this looks for a variable to parse the below metrics.

def parsers():

    parser = argparse.ArgumentParser(description="request specific metrics")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--Invocations', action="store_true", help="Add this flag to parse the number of invocations")
    group.add_argument('-e','--Errors', action="store_true", help="Add this flag to parse the number of Errors")
    group.add_argument('-d', '--DeadLetterErrors', action="store_true", help="Add this flag to parse the number of Dead Letter Errors")
    group.add_argument('-dd',  '--DestinationDeliveryFailures', action="store_true", help="Add this flag to parse the number of Destination Delivery Failures")
    group.add_argument('-t', '--Throttles', action="store_true", help="Add this flag to parse the number of Throttles")
    group.add_argument('-pc',  '--ProvisionedConcurrencySpilloverInvocations', action="store_true", help="Add this flag to parse the number of Provisioned Concurrency Spillover Invocations")
    group.add_argument('-pci',  '--ProvisionedConcurrencyInvocations', action="store_true", help="Add this flag to parse the number of Provisioned Concurrency Invocations")

    options = ["Invocations", "Errors", "DeadLetterErrors", "DestinationDeliveryFailures", "Throttles", "ProvisionedConcurrencyInvocations", "ProvisionedConcurrencySpilloverInvocations"]

    arg = parser.parse_args()
    selected_option = None
    for opt in options:
        if getattr(arg, opt):
            selected_option = opt
            break
    if selected_option:
        print(f"{selected_option.capitalize()} Selected")
        lambda_metrics(selected_option)
    else:
        print(parser.format_usage())


# #This code will print out all the data points over the past 28 days on Throttle metrics from CloudWatch
def lambda_metrics(metric):
    metric_functions = []

    # functions = lambda_client.list_functions()['Functions']
    start_time = datetime.datetime.utcnow() - timedelta(days=14)
    end_time = datetime.datetime.utcnow()

    metric_count=0

    # Iterate through each function
    for page in paginator.paginate():
        for function in page['Functions']:
            # Get the CloudWatch Logs data for the function's throttling events
            result = cw.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'm1',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Lambda',
                                'MetricName': metric,
                                'Dimensions': [
                                    {
                                        'Name': 'FunctionName',
                                        'Value': function['FunctionName']
                                    },
                                ]
                            },
                            'Period': 3600,
                            'Stat': 'Sum'
                        },
                        'ReturnData': True
                    },
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            # Extract the number of throttling events from the data

            if result['MetricDataResults'] and result['MetricDataResults'][0]['Values']:
                metric_count = sum(result['MetricDataResults'][0]['Values'])
                if metric_count != 0.0:
                    metric_functions.append({"FunctionArn": function['FunctionArn'], f"{metric} Count":metric_count})

    # Sort the resulting List of JSON Objects
    sorted_metric_functions = sorted(metric_functions, key=lambda k: k[F'{metric} Count'], reverse=True)
    pprint.pprint(sorted_metric_functions)

    return{
    'statusCode':200,
    'body': sorted_metric_functions
    }

if __name__ == "__main__":
    parsers()