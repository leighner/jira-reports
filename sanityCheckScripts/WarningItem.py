import json


class WarningItem:
    warningDescription = ''
    warningValue = ''
    criticality = 0

    def __str__(self):
        return 'warningDescription: {0} warningValue: {1} criticality: {2}'.format(
            self.warningDescription, self.warningValue, self.criticality)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
