from commonScripts import ReportItem, getJiraData
from sanityCheckScripts import WarningItem

# find all custom dev items
customDevIssuesJQL = 'issuetype = "Custom Dev" and status in ("To Do", "In Progress", "Waiting For Release")'
customDevIssues = getJiraData.runJiraItemQuery(customDevIssuesJQL)

# pull out data for the script
reportItems = []
epicKeys = []

for issue in customDevIssues['issues']:
    reportItem = ReportItem.ReportItem()
    reportItem.key = issue['key']
    reportItem.status = issue['fields']['status']['name']
    reportItem.labels = issue['fields']['labels']
    reportItem.summary = issue['fields']['summary']
    if issue['fields']['customfield_10032']:
        for customer in issue['fields']['customfield_10032']:
            reportItem.customers.append(customer['value'])
    if issue['fields']['customfield_10014']:
        reportItem.epicLink = issue['fields']['customfield_10014']
        epicKeys.append(reportItem.epicLink)
    reportItems.append(reportItem)

# for reportItem in reportItems:
#    print(reportItem)

warnings = []

# scan for warnings on the custom dev items themselves
for reportItem in reportItems:
    if reportItem.status != "To Do" and not reportItem.epicLink:
        warning = WarningItem.WarningItem()
        warning.warningDescription = 'No epic associated with custom dev item.'
        warning.warningValue = reportItem.key
        warnings.append(warning)
    if reportItem.customers.__len__ == 0:
        warning = WarningItem.WarningItem()
        warning.warningDescription = 'No customer associated with custom dev item.'
        warning.warningValue = reportItem.key
        warnings.append(warning)

# find epic parents of the custom dev items
parentEpicIssuesJQL = 'issuekey in ({0})'.format(", ".join(epicKeys))
parentEpicIssues = getJiraData.runJiraItemQuery(parentEpicIssuesJQL)
epicItems = []

for issue in parentEpicIssues['issues']:
    reportItem = ReportItem.ReportItem()
    reportItem.key = issue['key']
    reportItem.status = issue['fields']['status']['name']
    reportItem.labels = issue['fields']['labels']
    reportItem.summary = issue['fields']['summary']
    if issue['fields']['customfield_10032']:
        for customer in issue['fields']['customfield_10032']:
            reportItem.customers.append(customer['value'])
    epicItems.append(reportItem)

# scan for warnings on the epic items
for reportItem in epicItems:
    if reportItem.customers.__len__ == 0:
        warning = WarningItem.WarningItem()
        warning.warningDescription = 'No customer associated with epic item.'
        warning.warningValue = reportItem.key
        warnings.append(warning)
    if not "XCharge" in reportItem.labels:
        warning = WarningItem.WarningItem()
        warning.warningDescription = 'XCharge label not present on epic item.'
        warning.warningValue = reportItem.key
        warnings.append(warning)

# find children of custom dev epics
childrenOfEpicIssuesJQL = '"Epic Link" in ({0})'.format(", ".join(epicKeys))
childrenOfEpicIssues = getJiraData.runJiraItemQuery(childrenOfEpicIssuesJQL)
childItems = []

for issue in childrenOfEpicIssues['issues']:
    reportItem = ReportItem.ReportItem()
    reportItem.key = issue['key']
    reportItem.status = issue['fields']['status']['name']
    reportItem.labels = issue['fields']['labels']
    reportItem.summary = issue['fields']['summary']
    if issue['fields']['customfield_10032']:
        for customer in issue['fields']['customfield_10032']:
            reportItem.customers.append(customer['value'])
    if issue['fields']['customfield_10014']:
        reportItem.epicLink = issue['fields']['customfield_10014']
    childItems.append(reportItem)

# scan for warnings on the epic items
for reportItem in childItems:
    if reportItem.customers.__len__ == 0:
        warning = WarningItem.WarningItem()
        warning.warningDescription = 'No customer associated with child item.'
        warning.warningValue = reportItem.key
        warnings.append(warning)
    if not "XCharge" in reportItem.labels:
        warning = WarningItem.WarningItem()
        warning.warningDescription = 'XCharge label not present on child item.'
        warning.warningValue = reportItem.key
        warnings.append(warning)

for warning in warnings:
    print(warning)
