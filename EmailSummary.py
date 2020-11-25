import smtplib
import config
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def sendEmail(fromAddress, toList, filePaths):
    """ Sends the cross charge report as an attachment. """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Cross Charge Report"
    msg['From'] = fromAddress
    msg['To'] = toList
    msg['CC'] = fromAddress

    htmlMessage = """ \
<html>
    <head></head>
    <body>
        <h2>It's cross charge report time again!</h2>
        <p>Please review the contents of this cross charge report and send me any corrections within 24 hours.</p>
        <p>If there are no corrections, this cross charge report will be sent out at that time.</p>
        <p>Cheers,</p>
        <strong>RG!</strong>
    </body>
</html>
"""
    richHtmlMessage = MIMEText(htmlMessage, 'html')
    msg.attach(richHtmlMessage)

    attachments = []

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


sendEmail(config.emailSender, config.emailReceiver, [
          "CrossChargeReport.xlsx", "CrossChargeReport2.xlsx"])
