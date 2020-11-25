class ReportItem:
    key = ''
    hoursLogged = 0
    customer = ''
    summary = ''
    status = ''
    remainingEstimate = 0
    parent = ''

    def __str__(self):
        return 'key: {0} summary: {1} customer: {2} status: {3} parent: {4} hoursLogged: {5} estimate: {6}'.format(
            self.key, self.summary, self.customer, self.status, self.parent, str(self.hoursLogged), str(self.remainingEstimate))
