from dateutil import parser
import json
from requests.auth import HTTPBasicAuth
import config
import requests
import datetime
import json
import xlsxwriter

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

    def __str__(self):
        return 'key: {0} summary: {1} customer: {2} status: {3} parent: {4} hoursLogges: {5} estimate: {6}'.format(
            self.key, self.summary, self.customer, self.status, self.parent, str(self.hoursLogged), str(self.remainingEstimate))


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

# export to spreadsheet
workbook = xlsxwriter.Workbook('CrossChargeReport.xlsx')
worksheet = workbook.add_worksheet()

# Start from the first cell. Rows and columns are zero indexed.
worksheet.write(0, 0, 'Key')
worksheet.write(0, 1, 'Summary')
worksheet.write(0, 2, 'Parent')
worksheet.write(0, 3, 'Customer')
worksheet.write(0, 4, 'Status')
worksheet.write(0, 5, 'Hours Remaining')
worksheet.write(0, 6, 'Hours Spent')

row = 1
col = 0

for reportItem in reportItems:
    worksheet.write(row, 0, reportItem.key)
    worksheet.write(row, 1, reportItem.summary)
    worksheet.write(row, 2, reportItem.parent)
    worksheet.write(row, 3, reportItem.customer)
    worksheet.write(row, 4, reportItem.status)
    worksheet.write(row, 5, reportItem.remainingEstimate)
    worksheet.write(row, 6, reportItem.hoursLogged)
    row += 1

workbook.close()
