import smtplib
import config
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def sendEmail(fromAddress, toList, hoursLogged):
    """ Sends a nag email. """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "You forgot to log your time!"
    msg['From'] = fromAddress
    msg['To'] = toList
    msg['CC'] = fromAddress

    htmlMessage = """ \
<html>
    <head></head>
    <body>
        <h2>Please log your time</h2>
        <p>You only logged {0} hours in the last week.</p>
        <p>We need accurate logging data to help us make informed decisions as an R&D group.</p>
        <p>Please log last week's hours before anything else today.</p>
        <p>Cheers,</p>
        <strong>RG!</strong>
    </body>
</html>
"""

    richHtmlMessage = MIMEText(htmlMessage.format(hoursLogged), 'html')
    msg.attach(richHtmlMessage)

    attachments = []

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    with smtplib.SMTP(config.emailServerDNS, config.emailServerPort) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(config.emailUsername, config.emailPassword)
        server.sendmail(config.emailSender,
                        config.emailReceiver, msg.as_string())

#sendEmail(config.emailSender, config.emailReceiver, 20)
