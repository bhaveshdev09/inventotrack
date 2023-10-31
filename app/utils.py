from threading import Thread
from .models import *
from django.conf import settings
import os
from django.core.mail import EmailMessage
from datetime import date
from zipfile import ZipFile
import csv
from django.contrib.auth import get_user_model


def check_user(email: str):
    """
    The function checks if a user with a given email exists in the database and returns the user object
    if found, otherwise returns None.

    :param email: The email parameter is a string that represents the email address of a user
    :type email: str
    :return: either an instance of the User model if a user with the specified email exists, or None if
    no user with the specified email exists.
    """
    try:
        user_model = get_user_model()
        return user_model.objects.get(email=email)
    except user_model.DoesNotExist:
        return None


class EmailThread(Thread):
    def __init__(self, subject, body, email, attachments=None):
        self.subject = subject
        self.body = body
        self.email = email
        self.attachments = attachments
        Thread.__init__(self)

    def run(self):
        from_email = settings.DEFAULT_FROM_EMAIL
        to = self.email

        if isinstance(to, str):
            e = EmailMessage(self.subject, self.body, from_email, [to])
        else:
            e = EmailMessage(self.subject, self.body, from_email, to)

        if self.attachments is not None:
            e.attach_file(self.attachments)
        e.send()


## Logic Incomplete @
def zipBarcodes():
    sku_file_paths = SKUItems.objects.all().values_list("sku_barcode_image", flat=True)
    with ZipFile("./media/AllBarcodes.zip", "w") as archive:
        for image_path in sku_file_paths:
            if image_path == "backup/":
                continue
            elif image_path is not None:
                archive.write(
                    os.path.join(settings.MEDIA_ROOT, image_path),
                    arcname=os.path.basename(image_path),
                )


def sendEmailReport():
    """send email to every user in database"""

    user_email = "bhavesh@farintsol.com"  # User.objects.values("email")
    # user_email_list = [i.get("email") for i in user_email]

    today_date = date.today().strftime("%Y-%m-%d")

    bypass_sku_data = ByPassModel.objects.filter(bypass_date=today_date)

    try:
        if bypass_sku_data.exists():
            with open("BypassData.csv", mode="w") as employee_file:
                writer = csv.writer(employee_file)
                writer.writerow(
                    [
                        "Invoice_no",
                        "Bypass S.K.U. Name",
                        "Bypass Against S.K.U. Name",
                        "Bypass Date",
                        "Bypass Time",
                    ]
                )

                bypass_data = ByPassModel.objects.filter(
                    bypass_date=today_date
                ).values()
                for each in bypass_data:
                    invoice_no = Invoice.objects.get(
                        id=each["bypass_invoice_no_id"]
                    ).invoice_no
                    bypass_sku_name = SKUItems.objects.get(
                        id=each["bypass_sku_name_id"]
                    ).sku_name
                    bypass_against_sku_name = SKUItems.objects.get(
                        id=each["bypass_against_sku_name_id"]
                    )
                    bypass_date = each["bypass_date"].strftime("%Y-%m-%d")
                    bypass_time = each["bypass_time"].strftime("%H:%M:%S %p")

                    bypass_data = (
                        invoice_no,
                        bypass_sku_name,
                        bypass_against_sku_name,
                        bypass_date,
                        bypass_time,
                    )
                    writer.writerow(bypass_data)

            EmailThread(
                "Bypass SKU List CSV data",
                "CSV file for Bypass SKU Items",
                [user_email],
                attachments="BypassData.csv",
            ).start()
        else:
            EmailThread(
                "Bypass SKU List CSV data",
                "There is no bypass SKU List generated today",
                [user_email],
            ).start()
    except Exception as e:
        print("Error in sendEmailReport -> ", e)


def mapBaseQty(filename="sku.csv"):
    """Map data from CSV file -> SKU Name and update SKU base qty"""
    with open(os.path.join(filename)) as csvfile:
        csvreader = csv.DictReader(csvfile)

        for i in csvreader:
            sku_item = i["ITEM"]
            is_sku = SKUItems.objects.filter(sku_name=sku_item)
            if is_sku.exists():
                fetch_sku = SKUItems.objects.get(sku_name=sku_item)
                fetch_sku.sku_base_qty = 1 if i["PACKING"] == "" else i["PACKING"]
                fetch_sku.save()
