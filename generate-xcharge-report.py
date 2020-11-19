from dateutil import parser
import json
from requests.auth import HTTPBasicAuth
import config
import requests
import datetime
import json

baseURL = config.url
searchURL = baseURL + "/rest/api/3/search"
issueURL = baseURL + "/rest/api/3/issue/CIS-120/worklog"
issueWorkLogsURL = baseURL + "/rest/api/3/issue/{0}/worklog"
crossChargeWithWorklogBetweenDatesTemplate = 'labels = XCharge AND worklogDate >= {0} AND worklogDate <= {1}'


auth = HTTPBasicAuth(config.username, config.password)

headers = {
    "Accept": "application/json"
}

fromDate = "2020-10-1"
toDate = "2020-11-1"
epoch = parser.parse("1970-1-1T00:00:00.000-0400").utcfromtimestamp(0)


def getItemsForQuery(fromDate, toDate):
    queryString = crossChargeWithWorklogBetweenDatesTemplate.format(
        fromDate, toDate)
    params = {
        'jql': queryString
    }
    response = requests.request(
        "GET",
        searchURL,
        headers=headers,
        params=params,
        auth=auth
    )
    return json.loads(response.text)


def getWorkLogs(date, key):
    url = issueWorkLogsURL.format(key)
    # print(url)
    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
    )
    return json.loads(response.text)


def getHoursLoggedWithinDateRange(fromDate, toDate, key):
    totalSecondsSpent = 0
    timeLogsForIssues = getWorkLogs(fromDate, key)
    for worklog in timeLogsForIssues['worklogs']:
        logDate = parser.parse(worklog['started'])
        if logDate >= fromDate and logDate <= toDate:
            totalSecondsSpent = totalSecondsSpent + worklog['timeSpentSeconds']
            # print(worklog['timeSpentSeconds'])
    return totalSecondsSpent / 3600


class ReportItem:
    key = ''
    hoursLogged = 0
    customer = ''
    summary = ''
    status = ''
    remainingEstimate = 0
    parent = ''


reportItems = []

# get issue keys within date range
issuesWithTimeLogsInRange = getItemsForQuery(fromDate, toDate)
for issue in issuesWithTimeLogsInRange['issues']:
    reportItem = ReportItem()
    reportItem.key = issue['key']
    reportItem.status = issue['fields']['status']['name']
    reportItem.summary = issue['fields']['summary']
    # check if this exists first
    if issue['fields']['customfield_10032']:
        reportItem.customer = issue['fields']['customfield_10032'][0]['value']
    # check if this exists first
    if issue['fields']['parent']:
        reportItem.parent = issue['fields']['parent']['key']
    reportItems.append(reportItem)

# get worklogs from issues within date range
fromDateTime = parser.parse(fromDate + 'T00:00:00.000-0400')
toDateTime = parser.parse(toDate + 'T00:00:00.000-0400')
for reportItem in reportItems:
    hrsSpent = getHoursLoggedWithinDateRange(
        fromDateTime, toDateTime, reportItem.key)
    reportItem.hoursLogged = hrsSpent

for reportItem in reportItems:
    print(reportItem)
