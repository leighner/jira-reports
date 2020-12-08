import json
import getJiraData
import ReportItem
from dateutil import parser
from TimeLogEmailer import sendEmail
import config
import datetime
import pytz

print('begun new time-log-check-run on {0}'.format(datetime.datetime.now()))

timezone = pytz.timezone("America/Montreal")
toDateTime = timezone.localize(
    datetime.datetime.now() - datetime.timedelta(days=1))
fromDateTime = toDateTime - datetime.timedelta(days=7)

print('checking worklogs between {0} and {1}'.format(
    fromDateTime.date(), toDateTime.date()))

threshold = 32
worklogQuery = "worklogAuthor = {0} and worklogDate > {1} and worklogDate < {2}"

with open('teamMembers.json') as teamMemberFile:
    teamMembers = json.load(teamMemberFile)

# print(teamMembers)

for teamMember in teamMembers:
    print("")
    print('checking hours logged for {0}'.format(teamMember['name']))
    issuesWithTimeLogsInRange = getJiraData.runJiraItemQuery(
        worklogQuery.format(teamMember['jiraID'], fromDateTime.date(), toDateTime.date()))

    # print(issuesWithTimeLogsInRange)

    reportItems = []
    for issue in issuesWithTimeLogsInRange['issues']:
        reportItem = ReportItem.ReportItem()
        reportItem.key = issue['key']
        reportItems.append(reportItem)

    # print(reportItems)

    totalHoursSpent = 0

    for reportItem in reportItems:
        reportItem.hoursLogged = getJiraData.getHoursLoggedWithinDateRangeAndUser(
            fromDateTime, toDateTime, reportItem.key, teamMember['jiraID'])
        print("{0} hours spent on {1}".format(
            reportItem.hoursLogged, reportItem.key))
        totalHoursSpent = totalHoursSpent + reportItem.hoursLogged

    print("Total hours logged that week: {0}".format(totalHoursSpent))
    teamMember['reportItems'] = reportItems

    if totalHoursSpent < teamMember['threshold']:
        teamMember['sendNag'] = True
        print("Threshold not met.  Send nag email.")
        sendEmail(config.emailSender,
                  teamMember['emailAddress'], totalHoursSpent, teamMember['name'])
    else:
        teamMember['sendNag'] = False
        print("Threshold met.  Don't send nag email.")
