from __future__ import annotations
from dataclasses import dataclass
import random


PHISHING_TEMPLATES = [
    ("IT@gmail.com",    "Your password expires today. Click here to reset it."),
    ("HR@gmail.com", "You have an urgent document to sign. Act now."),
    ("CEO@yahoo.com",           "I need you to process a wire transfer immediately."),
    ("IT@hotmail.com",   "Unusual login detected. Verify your account now."),
    ("Payroll@compiny.com",       "Your direct deposit info needs to be updated."),
]

LEGITIMATE_TEMPLATES = [
    ("IT@company.net",    "Scheduled maintenance this Sunday 2–4am."),
    ("HR@company.net", "Reminder: annual reviews are due next Friday."),
    ("CEO@company.net",           "Great work on the Q1 results everyone!"),
    ("IT@company.net",   "Your VPN certificate has been renewed successfully."),
    ("Payroll@company.net",       "March payslips are now available in the portal."),
]


@dataclass
class PhishingMessage:
    sender: str
    body: str
    is_phishing: bool

    @staticmethod
    def generate(phishing_probability: float = 0.5) -> PhishingMessage:
        """
        Generate a message. Higher phishing_probability = more phishing messages.
        """
        if random.random() < phishing_probability:
            sender, body = random.choice(PHISHING_TEMPLATES)
            return PhishingMessage(sender=sender, body=body, is_phishing=True)
        else:
            sender, body = random.choice(LEGITIMATE_TEMPLATES)
            return PhishingMessage(sender=sender, body=body, is_phishing=False)

    def display(self) -> None:
        print(f"\n  From:    {self.sender}")
        print(f"  Message: {self.body}")
