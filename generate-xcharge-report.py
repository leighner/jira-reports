from dateutil import parser
import config
import datetime
import json
from commonScripts import Emailer, ReportItem, getJiraData
from xchargeReportScripts import writeSpreadsheet

crossChargeReportFilename = "CrossChargeReport.xlsx"
fromDate = "2020-11-26"
toDate = "2020-12-28"
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

htmlMessage = """ \
<html>
    <head></head>
    <body>
        <h2>It's cross charge report time again!</h2>
        <p>Please review the contents of this cross charge report and send me any corrections within 24 hours.</p>
        <p>If there are no corrections, this cross charge report will be sent out at that time.</p>
        <p>Cheers,</p>
        <strong>RG!</strong>
    </body>
</html>
"""

Emailer.sendEmail(config.emailSender, config.emailReceiver,
                  'Cross Charge Report', htmlMessage, filePaths=crossChargeReportFilename)
