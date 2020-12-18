
import requests
import config
from requests.auth import HTTPBasicAuth
import json
from dateutil import parser
from commonScripts import ReportItem


baseURL = config.jiraUrl
searchURL = baseURL + "/rest/api/3/search"
issueURL = baseURL + "/rest/api/3/issue/CIS-120/worklog"
issueWorkLogsURL = baseURL + "/rest/api/3/issue/{0}/worklog"


auth = HTTPBasicAuth(config.jiraUsername, config.jiraPassword)

headers = {
    "Accept": "application/json"
}


def runJiraItemQuery(query):
    queryString = query
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
    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
    )
    return json.loads(response.text)


def getHoursLoggedWithinDateRangeAndUser(fromDate, toDate, key, author):
    totalSecondsSpent = 0
    timeLogsForIssues = getWorkLogs(fromDate, key)
    for worklog in timeLogsForIssues['worklogs']:
        if worklog['author']['accountId'] == author:
            logDate = parser.parse(worklog['started'])
            if logDate >= fromDate and logDate <= toDate:
                totalSecondsSpent = totalSecondsSpent + \
                    worklog['timeSpentSeconds']
    return totalSecondsSpent / 3600


def getHoursLoggedWithinDateRange(fromDate, toDate, key):
    totalSecondsSpent = 0
    timeLogsForIssues = getWorkLogs(fromDate, key)
    for worklog in timeLogsForIssues['worklogs']:
        logDate = parser.parse(worklog['started'])
        if logDate >= fromDate and logDate <= toDate:
            totalSecondsSpent = totalSecondsSpent + worklog['timeSpentSeconds']
    return totalSecondsSpent / 3600


def parseJiraIssues(issueArray):
    issues = []

    for issue in issueArray['issues']:
        reportItem = ReportItem.ReportItem()
        reportItem.key = issue['key']
        reportItem.status = issue['fields']['status']['name']
        reportItem.labels = issue['fields']['labels']
        reportItem.summary = issue['fields']['summary']
        reportItem.issueType = issue['fields']['issuetype']['name']
        if issue['fields']['customfield_10032']:
            for customer in issue['fields']['customfield_10032']:
                reportItem.customers.append(customer['value'])
        if issue['fields']['customfield_10014']:
            reportItem.epicLink = issue['fields']['customfield_10014']
        issues.append(reportItem)

    return issues
