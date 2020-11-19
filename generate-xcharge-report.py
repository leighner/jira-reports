from dateutil import parser
import json
from requests.auth import HTTPBasicAuth
import config
import requests
import datetime
import json
import xlsxwriter
import os

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
filename = 'CrossChargeReport.xlsx'
if os.path.exists(filename):
    os.remove(filename)
workbook = xlsxwriter.Workbook(filename)
worksheet = workbook.add_worksheet()

# add styles
bold = workbook.add_format({'bold': True})


row = 1
col = 0
totalTimeSpent = 0
totalTimeRemaining = 0

# write content of tables
for reportItem in reportItems:
    worksheet.write(row, 0, reportItem.key)
    worksheet.write(row, 1, reportItem.summary)
    worksheet.write(row, 2, reportItem.parent)
    worksheet.write(row, 3, reportItem.customer)
    worksheet.write(row, 4, reportItem.status)
    worksheet.write(row, 5, reportItem.remainingEstimate)
    worksheet.write(row, 6, reportItem.hoursLogged)
    row += 1
    totalTimeRemaining += reportItem.remainingEstimate
    totalTimeSpent += reportItem.hoursLogged

# put it in a table with headers
worksheet.add_table(0, 0, row - 1, 6, {'header_row': True, 'columns': [{'header': 'Key'}, {'header': 'Summary'}, {
                    'header': 'Parent'}, {'header': 'Customer'}, {'header': 'Status'}, {'header': 'Hours Remaining'}, {'header': 'Hours Spent'}]})

# write totals row
worksheet.write(row, 0, 'Total', bold)
worksheet.write(row, 1, '')
worksheet.write(row, 2, '')
worksheet.write(row, 3, '')
worksheet.write(row, 4, '')
worksheet.write(row, 5, str(totalTimeRemaining), bold)
worksheet.write(row, 6, str(totalTimeSpent), bold)
row += 2

# write disclaimer
worksheet.write(
    row, 0, 'Contains cross-charge from {0} through {1} inclusive.'.format(str(fromDate), str(toDate)), bold)

workbook.close()
