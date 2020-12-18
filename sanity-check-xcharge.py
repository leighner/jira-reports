from commonScripts import ReportItem, getJiraData
from sanityCheckScripts import WarningItem
from commonScripts.getJiraData import parseJiraIssues

# find all custom dev items
customDevIssuesJQL = 'issuetype = "Custom Dev" and status in ("To Do", "In Progress", "Waiting For Release")'
customDevIssues = getJiraData.runJiraItemQuery(customDevIssuesJQL)

# pull out data for the script
reportItems = parseJiraIssues(customDevIssues)
issuesWithEpicLink = list(filter(lambda x: x.epicLink, reportItems))
epicKeys = list(map(lambda x: x.epicLink, issuesWithEpicLink))

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
epicItems = parseJiraIssues(parentEpicIssues)

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
childItems = parseJiraIssues(childrenOfEpicIssues)

# scan for warnings on the epic items
for reportItem in childItems:
    if not reportItem.issueType == 'Custom Dev':
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
