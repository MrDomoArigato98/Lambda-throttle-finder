# Lambda-throttle-finder
This Python script should reduce the time needed finding throttling across functions by getting the metric data from all the functions in the account. Works on other metrics too.

It prints out a sorted list (Highest Throttle) and functions for easier visibility. It will work in the region it is executed in, and the region configured for credentials.

The Data is from CloudWatch Metrics using the GetMetricData API, and this code will get the last 14 days. This can be modified to be less, or more by changing the delta lower or higher. 
It will paginate across all the functions in the region.

Other AWS Lambda metrics that are by default a SumStatistic can be gathered by this script.

Additionally you can get an aggregation on the below metrics per function by passing any of these when calling the script:

--Invocations OR -i 

--Errors OR -e

--DeadLetterErrors OR -d

--DestinationDeliveryFailures OR -dd

--Throttles OR -t

--ProvisionedConcurrencyInvocations OR -pc

--ProvisionedConcurrencySpilloverInvocations OR -pci

Example

```python3 list_throttles.py -pci```

```python3 list_throttles.py --ProvisionedConcurrencyInvocations```
