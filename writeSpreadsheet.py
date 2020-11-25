import xlsxwriter
import os


def generateSpreadSheet(filename, reportItems, fromDate, toDate):
    filename = 'CrossChargeReport.xlsx'
    if os.path.exists(filename):
        os.remove(filename)
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    # add styles
    bold = workbook.add_format({'bold': True})

    row = 1
    col = 0
    totalTimeSpent = 0
    totalTimeRemaining = 0

    # write content of tables
    for reportItem in reportItems:
        worksheet.write(row, 0, reportItem.key)
        worksheet.write(row, 1, reportItem.summary)
        worksheet.write(row, 2, reportItem.parent)
        worksheet.write(row, 3, reportItem.customer)
        worksheet.write(row, 4, reportItem.status)
        worksheet.write(row, 5, reportItem.remainingEstimate)
        worksheet.write(row, 6, reportItem.hoursLogged)
        row += 1
        if reportItem.remainingEstimate:
            totalTimeRemaining += reportItem.remainingEstimate
        totalTimeSpent += reportItem.hoursLogged

    # put it in a table with headers
    worksheet.add_table(0, 0, row, 6, {
        'header_row': True,
        'columns': [
            {'header': 'Key'},
            {'header': 'Summary'},
            {'header': 'Parent'},
            {'header': 'Customer'},
            {'header': 'Status'},
            {'header': 'Hours Remaining', 'total_function': 'sum'},
            {'header': 'Hours Spent', 'total_function': 'sum'}],
        'total_row': True})

    # write disclaimer
    row += 2
    worksheet.write(
        row, 0, 'Contains cross-charge from {0} through {1} inclusive.'.format(str(fromDate), str(toDate)), bold)

    workbook.close()
