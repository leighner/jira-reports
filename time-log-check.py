import json
import getJiraData
import ReportItem
from dateutil import parser

fromDate = "2020-10-27"
toDate = "2020-11-25"
worklogQuery = "worklogAuthor = {0} and worklogDate > {1} and worklogDate < {2}"

with open('teamMembers.json') as teamMemberFile:
    teamMembers = json.load(teamMemberFile)

# print(teamMembers)


for teamMember in teamMembers:
    issuesWithTimeLogsInRange = getJiraData.runJiraItemQuery(
        worklogQuery.format(teamMember['jiraID'], fromDate, toDate))

    # print(issuesWithTimeLogsInRange)

    reportItems = []
    for issue in issuesWithTimeLogsInRange['issues']:
        reportItem = ReportItem.ReportItem()
        reportItem.key = issue['key']
        reportItems.append(reportItem)

    # print(reportItems)

    fromDateTime = parser.parse(fromDate + 'T00:00:00.000-0400')
    toDateTime = parser.parse(toDate + 'T00:00:00.000-0400')

    for reportItem in reportItems:
        reportItem.hoursLogged = getJiraData.getHoursLoggedWithinDateRangeAndUser(
            fromDateTime, toDateTime, reportItem.key, teamMember['jiraID'])
        print("{0} hours spent on {1}".format(
            reportItem.hoursLogged, reportItem.key))
