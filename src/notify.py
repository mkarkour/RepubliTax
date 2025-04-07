import logging
import random
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Sender:
    def __init__(self,
                 sender: str,
                 sender_pwd: str,
                 smtp_port: int = 465,
                 smtp_address: str = 'smtp.gmail.com') -> None:
        """
        Initialize sender object

        Args:
            sender (str): Email address that represents the sender.
            sender_pwd (str): Email password of the sender.
            smtp_port (int, optional): Smtp Port which is used.
                                       Defaults to 465.
            smtp_address (str, optional): Smpt address type that is used.
                                          Defaults to 'smtp.gmail.com'.
        """
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s',
                                           '%m-%d-%Y %H:%M:%S')
        # self.setup_logger()

        self.sender = sender
        self.sender_pwd = sender_pwd
        self.smtp_port = smtp_port
        self.smtp_address = smtp_address

    def send(self, receiver: str, sending: str) -> None:
        """
        This method allows you to send a message to a specific receiver and with a
        specific message type. This message has a predefined template that will be used.

        Args:
            receiver (str): Email address of the receiver.
            sending (str): Message that you want to send.
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = "[Probo's message] Video's Game Review Message"
        message["From"] = self.sender
        message["To"] = receiver
        adjective = ["beautiful",
                     "brilliant",
                     "brave",
                     "courageous",
                     "admirable",
                     "persevering",
                     "impartial",
                     "methodical",
                     "divine",
                     "pleasant",
                     "Poseidon"]

        baseline = '''
        <html>
        <body>
        <h4>Hello M.,<br>
        How are you today?<br>
        I would like to inform you that I find you {a}.</h4>
        <p>As requested, here is the list of currently available budget-friendly games
        that might interest you:</p>
        <table align="center"   hspace=10 vspace=6 border=1 frame=hsides rules=rows>
        <tr bgcolor="#800080">
            <th>Name</th>
            <th>Price</th>
            <th>Promo</th>
            <th>Link</th>
        </tr>
        {s}
        </table>
        <h4>Kind regards,<br>
        Probo</h4>
        </body>
        </html>
        '''.format(a=random.choice(adjective), s=sending)
        html_mime = MIMEText(baseline, 'html')
        message.attach(html_mime)

        ctxt = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_address, self.smtp_port, context=ctxt) as server:
            server.login(self.sender, self.sender_pwd)
            server.sendmail(self.sender, receiver, message.as_string())
        self.logger.info("Email perferctly send")
