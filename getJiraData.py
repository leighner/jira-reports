
import requests
import config
from requests.auth import HTTPBasicAuth
import json
from dateutil import parser


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


def getHoursLoggedWithinDateRange(fromDate, toDate, key):
    totalSecondsSpent = 0
    timeLogsForIssues = getWorkLogs(fromDate, key)
    for worklog in timeLogsForIssues['worklogs']:
        logDate = parser.parse(worklog['started'])
        if logDate >= fromDate and logDate <= toDate:
            totalSecondsSpent = totalSecondsSpent + worklog['timeSpentSeconds']
    return totalSecondsSpent / 3600
