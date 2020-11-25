from dateutil import parser
import json
from requests.auth import HTTPBasicAuth
import config
import requests
import datetime
import json
import writeSpreadsheet

baseURL = config.jiraUrl
searchURL = baseURL + "/rest/api/3/search"
issueURL = baseURL + "/rest/api/3/issue/CIS-120/worklog"
issueWorkLogsURL = baseURL + "/rest/api/3/issue/{0}/worklog"
crossChargeWithWorklogBetweenDatesTemplate = 'labels = XCharge AND worklogDate >= {0} AND worklogDate <= {1} order by cf[10032]'


auth = HTTPBasicAuth(config.jiraUsername, config.jiraPassword)

headers = {
    "Accept": "application/json"
}

fromDate = "2020-10-27"
toDate = "2020-11-25"
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

    def __str__(self):
        return 'key: {0} summary: {1} customer: {2} status: {3} parent: {4} hoursLogged: {5} estimate: {6}'.format(
            self.key, self.summary, self.customer, self.status, self.parent, str(self.hoursLogged), str(self.remainingEstimate))


reportItems = []

# get issue keys within date range
issuesWithTimeLogsInRange = getItemsForQuery(fromDate, toDate)
for issue in issuesWithTimeLogsInRange['issues']:
    reportItem = ReportItem()
    reportItem.key = issue['key']
    reportItem.status = issue['fields']['status']['name']
    reportItem.summary = issue['fields']['summary']
    if issue['fields']['timeestimate']:
        reportItem.remainingEstimate = issue['fields']['timeestimate'] / 3600
    # check if this exists first
    if issue['fields']['customfield_10032']:
        reportItem.customer = issue['fields']['customfield_10032'][0]['value']
    # check if this exists first
    try:
        if issue['fields']['parent']:
            reportItem.parent = issue['fields']['parent']['key']
    except KeyError:
        pass
    reportItems.append(reportItem)

# get worklogs from issues within date range
fromDateTime = parser.parse(fromDate + 'T00:00:00.000-0400')
toDateTime = parser.parse(toDate + 'T00:00:00.000-0400')
for reportItem in reportItems:
    hrsSpent = getHoursLoggedWithinDateRange(
        fromDateTime, toDateTime, reportItem.key)
    reportItem.hoursLogged = hrsSpent

writeSpreadsheet.generateSpreadSheet(
    'CrossChargeReport.xlsx', reportItems, fromDate, toDate)
