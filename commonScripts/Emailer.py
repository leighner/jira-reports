import smtplib
import config
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def sendEmail(fromAddress, toList, subject, htmlBody, ccList='', filePaths=''):
    """ Sends an email with optional filepath attachments. """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromAddress
    msg['To'] = toList
    if ccList:
        msg['CC'] = ccList

    richHtmlMessage = MIMEText(htmlBody, 'html')
    msg.attach(richHtmlMessage)

    attachments = []

    if filePaths:
        if type(filePaths) is list:
            for filePath in filePaths:
                attachmentPart = MIMEBase('application', 'octet-stream')
                attachmentPart.set_payload(open(filePath, "rb").read())
                encoders.encode_base64(attachmentPart)
                attachmentPart.add_header(
                    'Content-Disposition', 'attachment; filename="{0}"'.format(filePath))

                msg.attach(attachmentPart)
        else:
            attachmentPart = MIMEBase('application', 'octet-stream')
            attachmentPart.set_payload(open(filePaths, "rb").read())
            encoders.encode_base64(attachmentPart)
            attachmentPart.add_header(
                'Content-Disposition', 'attachment; filename="{0}"'.format(filePaths))

            msg.attach(attachmentPart)

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    with smtplib.SMTP(config.emailServerDNS, config.emailServerPort) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(config.emailUsername, config.emailPassword)
        server.sendmail(config.emailSender,
                        config.emailReceiver, msg.as_string())


# sendEmail(config.emailSender, config.emailReceiver, [
#          "CrossChargeReport.xlsx", "CrossChargeReport2.xlsx"])
