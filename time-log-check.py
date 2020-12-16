import json
from dateutil import parser
import config
import datetime
import pytz
from commonScripts import Emailer, ReportItem, getJiraData

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
htmlMessage = """ \
<html>
    <head></head>
    <body>
        <p>Hi {0},</p>
        <br/>
        <p>You only logged <strong>{1}</strong> hours in the last week.</p>
        <h2>Please log your time now.</h2>
        <p>We need accurate logging data to help us make informed decisions as an R&D group.</p>
        <p>Please log the last week's hours before doing anything else today.</p>
        <p><a href="https://northstarutilities.atlassian.net/wiki/spaces/PROC/pages/96534543/Time+Logging+Policy">Click here for information on our time logging policy.</a></p>
        <br/>
        <p>Thanks,</p>
        <strong>RG!</strong>
    </body>
</html>
"""

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

        Emailer.sendEmail(config.emailSender, teamMember['emailAddress'], "You forgot to log your time!", htmlMessage.format(
            teamMember['name'], totalHoursSpent), config.emailSender)
    else:
        teamMember['sendNag'] = False
        print("Threshold met.  Don't send nag email.")
