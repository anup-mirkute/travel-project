import mailtrap as mt


class EmailService:
    @staticmethod
    async def send_email(to_email: str, subject: str, body: str):
        mail = mt.Mail(
            sender=mt.Address(email="hello@demomailtrap.co", name="Mailtrap Test"),
            to=[mt.Address(email=to_email)],
            subject=subject,
            text=body,
            category="Integration Test",
        )

        client = mt.MailtrapClient(token="da055c23f34e14e4ff30181a99189273")
        response = client.send(mail)
        return response