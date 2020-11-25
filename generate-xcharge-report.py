from dateutil import parser
import config
import datetime
import json
import writeSpreadsheet
import ReportItem
import getJiraData
import EmailSummary

crossChargeReportFilename = "CrossChargeReport.xlsx"
fromDate = "2020-10-27"
toDate = "2020-11-25"
epoch = parser.parse("1970-1-1T00:00:00.000-0400").utcfromtimestamp(0)
crossChargeWithWorklogBetweenDatesTemplate = 'labels = XCharge AND worklogDate >= {0} AND worklogDate <= {1} order by cf[10032]'


reportItems = []

# get issue keys within date range
issuesWithTimeLogsInRange = getJiraData.runJiraItemQuery(crossChargeWithWorklogBetweenDatesTemplate.format(
    fromDate, toDate))
for issue in issuesWithTimeLogsInRange['issues']:
    reportItem = ReportItem.ReportItem()
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
    hrsSpent = getJiraData.getHoursLoggedWithinDateRange(
        fromDateTime, toDateTime, reportItem.key)
    reportItem.hoursLogged = hrsSpent

writeSpreadsheet.generateSpreadSheet(
    crossChargeReportFilename, reportItems, fromDate, toDate)
EmailSummary.sendEmail(
    config.emailSender, config.emailReceiver, crossChargeReportFilename)
