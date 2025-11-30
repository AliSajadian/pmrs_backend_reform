"""
Models for the projects_files application.
"""
import datetime
import os
import django
from django.conf import settings
from django.db import models
from django.db.models import F, CharField, Value
from django.db.models.functions import Concat
from django.db.models.signals import pre_save, pre_delete, post_delete
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage

from contracts.models import Contract
from contracts.utils import gregorian_to_shamsi
from projects.models import ReportDate


# =========================================             
#        HSE REPORT DOCUMENTS MODEL
# ========================================= 
hse_fs = FileSystemStorage(location="D:\projects\cost_control\Pmrs_Files\Hse_Reports")

class HseReportDox(models.Model):
    """
    Hse report dox model for the projects_files application.
    """
    hsereportdoxid = models.AutoField(db_column='HseReportDoxID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_HseReportDox", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_HseReportDox", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True, default=django.utils.timezone.now)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    file = models.FileField(db_column='File', storage=hse_fs, max_length=250, null=True, unique=True)
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.

    def year(self):
        """
        Get the year for the Hse report dox.
        """
        return self.dateid.year

    def month(self):
        """
        Get the month for the Hse report dox.
        """
        return self.dateid.month
    
    def filename(self):
        """
        Get the filename for the Hse report dox.
        """
        if self.file:
            return self.file.name.split('/')[-1:][0]
        return ''
        
    class Meta:
        db_table = 'tblw_HseReportDox'

# @receiver(pre_save, sender=HseReportDox)
# def hseReport_file_pre_save(sender, instance, *args, **kwargs):
#     hseReportDox = HseReportDox.objects.all()
#     if len(hseReportDox) == 0:
#         return
#     # As it was not yet saved, we get the instance from DB with 
#     # the old file name to delete it. Which won't happen if it's a new instance
#     if instance and instance.hsereportdoxid and instance.file:
#         hseReportDox = HseReportDox.objects.get(hsereportdoxid=instance.hsereportdoxid)
#         if hseReportDox and hseReportDox.file and hseReportDox.file != instance.file:
#             storage, path = hseReportDox.file.storage, hseReportDox.file.path
#             if storage.exists(path):
#                 storage.delete(path)

@receiver(pre_delete, sender=HseReportDox)
def hseReport_file_pre_delete(sender, instance, *args, **kwargs):
    """
    Deletes image files on `post_delete` for the Hse report dox.
    """
    # Deletes image files on `post_delete`
    if instance.file:
        storage, path = instance.file.storage, instance.file.path
        if storage.exists(path):
            storage.delete(path)
      
      
# =========================================             
#         PROJECT CONTRACT MODEL
# =========================================             
projectDox_fs = FileSystemStorage(location="D:\projects\cost_control\Pmrs_Files\Project Contract")

class ProjectDox(models.Model):
    """
    Project dox model for the projects_files application.
    """
    projectdoxid = models.AutoField(db_column='ProjectDoxID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_ProjectDox", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_ProjectDox", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True, default=django.utils.timezone.now)  # Field name made lowercase.
    doctitle = models.PositiveSmallIntegerField(db_column='DocTitle', null=True)
    dockind = models.PositiveSmallIntegerField(db_column='DocKind', null=True)
    docno = models.PositiveSmallIntegerField(db_column='DocNo', null=True)
    file = models.FileField(db_column='File', storage=projectDox_fs, max_length=250, null=True, unique=True)
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.

    def filename(self):
        """
        Get the filename for the ProjectDox model.
        """
        if self.file:
            return self.file.name.split('/')[-1:][0]
        return ''
    
    class Meta:
        db_table = 'tblw_ProjectDox'

# @receiver(pre_save, sender=ProjectDox)
# def projectDox_file_pre_save(sender, instance, *args, **kwargs):
#     projectDox = ProjectDox.objects.all()
#     if len(projectDox) == 0:
#         return
#     # As it was not yet saved, we get the instance from DB with 
#     # the old file name to delete it. Which won't happen if it's a new instance
#     if instance and instance.projectdoxid and instance.file:
#         projectDox = ProjectDox.objects.get(projectdoxid=instance.projectdoxid)
#         if projectDox and projectDox.file and projectDox.file != instance.file:
#             storage, path = projectDox.file.storage, projectDox.file.path
#             if storage.exists(path):
#                 storage.delete(path)

@receiver(pre_delete, sender=ProjectDox)
def projectDox_file_pre_delete(sender, instance, *args, **kwargs):
    """ 
    Deletes image files on `post_delete` for the ProjectDox model.
    """
    # Deletes image files on `post_delete`
    if instance.file:
        storage, path = instance.file.storage, instance.file.path
        if storage.exists(path):
            storage.delete(path)


# =========================================             
#       PROJECT SUB CONTRACTS MODEL
# =========================================             
contractorDox_fs = FileSystemStorage(location="D:\projects\cost_control\Pmrs_Files\Project Sub Contracts")

class ContractDox(models.Model):
    """
    Contract dox model for the projects_files application.
    """
    contractdoxid = models.AutoField(db_column='ContractDoxID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_ContractDox", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    contracttitle = models.CharField(db_column='ContractTitle', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    contractor = models.CharField(db_column='Contractor', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    contractdate = models.DateField(db_column='ContractDate', blank=True, null=True)  # Field name made lowercase.
    contractno = models.CharField(db_column='ContractNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    riderno = models.SmallIntegerField(db_column='RiderNo', blank=True, null=True)  # Field name made lowercase.
    fileaddress = models.CharField(db_column='FileAddress', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    file = models.FileField(db_column='File', storage=contractorDox_fs, null=True, unique=True)

    def filename(self):
        """
        Get the filename for the ContractDox model.
        """
        if self.file:
            return self.file.name.split('/')[-1:][0]
        return ''
     
    class Meta:
        db_table = 'tblw_ContractDox'

# @receiver(pre_save, sender=ContractDox)
# def contractDox_file_pre_save(sender, instance, *args, **kwargs):
#     contractDox = ContractDox.objects.all()
#     if len(contractDox) == 0:
#         return
#     # As it was not yet saved, we get the instance from DB with 
#     # the old file name to delete it. Which won't happen if it's a new instance
#     if instance and instance.contractdoxid and instance.file:
#         contractDox = ContractDox.objects.get(contractdoxid=instance.contractdoxid)
#         if contractDox and contractDox.file and contractDox.file != instance.file:
#             storage, path = contractDox.file.storage, contractDox.file.path
#             if storage.exists(path):
#                 storage.delete(path)

@receiver(pre_delete, sender=ContractDox)
def contractDox_file_pre_delete(sender, instance, *args, **kwargs):
    """
    Deletes image files on `post_delete` for the ContractDox model.
    """
    # Deletes image files on `post_delete`
    if instance.file:
        storage, path = instance.file.storage, instance.file.path
        if storage.exists(path):
            storage.delete(path)


class ContractorDox(models.Model):
    """
    Contractor dox model for the projects_files application.
    """
    contractordoxid = models.AutoField(db_column='ContractorDoxId', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_ContractorDox", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    contractdate = models.DateField(db_column='ContractDate', blank=True, null=True, default=datetime.date.today)  # Field name made lowercase.
    contracttitle = models.CharField(db_column='ContractTitle', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')
    contractor = models.CharField(db_column='Contractor', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')
    contractno = models.CharField(db_column='ContractNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    riderno = models.PositiveSmallIntegerField(db_column='RiderNo')  # Field name made lowercase.
    file = models.FileField(db_column='File', storage=contractorDox_fs, max_length=250, null=True, unique=True)

    def contractshamsidate(self):
        """
        Get the contract shamsi date for the ContractorDox model.
        """
        return gregorian_to_shamsi(self.contractdate) if self.contractdate is not None else ''

    def filename(self):
        """
        Get the filename for the ContractorDox model.
        """
        if self.file:
            return self.file.name.split('/')[-1:][0]
        return ''
        
    class Meta:
        db_table = 'tblw_ContractorDox'

# @receiver(pre_save, sender=ContractorDox)
# def contractorDox_file_pre_save(sender, instance, *args, **kwargs):
#     contractorDox = ContractorDox.objects.all()
#     if len(contractorDox) == 0:
#         return
#     # As it was not yet saved, we get the instance from DB with 
#     # the old file name to delete it. Which won't happen if it's a new instance
#     if instance and instance.contractordoxid and instance.file:
#         contractorDoc = ContractorDox.objects.get(pk=instance.contractordoxid)
#         if contractorDoc and contractorDoc.file and contractorDoc.file != instance.file:
#             storage, path = contractorDoc.file.storage, contractorDoc.file.path
#             if storage.exists(path):
#                 storage.delete(path)
                    
@receiver(pre_delete, sender=ContractorDox)
def contractorDox_file_pre_delete(sender, instance, *args, **kwargs):
    """
    Deletes image files on `post_delete` for the ContractorDox model.
    """
    # Deletes image files on `post_delete`
    if instance.file:
        storage, path = instance.file.storage, instance.file.path
        if storage.exists(path):
            storage.delete(path)


# =========================================             
#      PROJECT MONTHLY REPORTS MODEL
# =========================================             
projectMonthlyDox_fs = FileSystemStorage(location="D:\projects\cost_control\Pmrs_Files\Project Monthly Reports")

class ProjectMonthlyDox(models.Model):
    """
    Project monthly dox model for the projects_files application.
    """
    projectmonthlydoxid = models.AutoField(db_column='ProjectMonthlyDoxId', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_ProjectMonthlyDox", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_ProjectMonthlyDox", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    file = models.FileField(db_column='File', storage=projectMonthlyDox_fs, max_length=250, null=True, unique=True)
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.

    def year(self):
        """
        Get the year for the ProjectMonthlyDox model.
        """
        return self.dateid.year

    def month(self):
        """
        Get the month for the ProjectMonthlyDox model.
        """
        return self.dateid.month

    def filename(self):
        """
        Get the filename for the ProjectMonthlyDox model.
        """
        if self.file:
            return self.file.name.split('/')[-1:][0]
        return ''
            
    class Meta:
        db_table = 'tblw_ProjectMonthlyDox'

# @receiver(pre_save, sender=ProjectMonthlyDox)
# def projectMonthlyDox_file_pre_save(sender, instance, *args, **kwargs):
#     projectMonthlyDox = ProjectMonthlyDox.objects.all()
#     if len(projectMonthlyDox) == 0:
#         return
#     # As it was not yet saved, we get the instance from DB with 
#     # the old file name to delete it. Which won't happen if it's a new instance
#     if instance and instance.projectmonthlydoxid and instance.file:
#         projectMonthlyDox = ProjectMonthlyDox.objects.get(projectmonthlydoxid=instance.projectmonthlydoxid)
#         if projectMonthlyDox and projectMonthlyDox.file and projectMonthlyDox.file != instance.file:
#             storage, path = projectMonthlyDox.file.storage, projectMonthlyDox.file.path
#             if storage.exists(path):
#                 storage.delete(path)

@receiver(pre_delete, sender=ProjectMonthlyDox)
def projectMonthlyDox_file_pre_delete(sender, instance, *args, **kwargs):
    """
    Deletes image files on `post_delete` for the ProjectMonthlyDox model.
    """
    # Deletes image files on `post_delete`
    if instance.file:
        storage, path = instance.file.storage, instance.file.path
        if storage.exists(path):
            storage.delete(path)


# =========================================             
#         INVOICE DOCUMENTS MODEL
# =========================================             
invoiceDox_fs = FileSystemStorage(location="D:\projects\cost_control\Pmrs_Files\Approved Invoices")

class InvoiceDox(models.Model):
    """
    Invoice dox model for the projects_files application.
    """
    invoicedoxid = models.AutoField(db_column='InvoiceDoxID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_Invoicedox", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_Invoicedox", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    invoicekind = models.SmallIntegerField(db_column='InvoiceKind')  # Field name made lowercase.
    invoiceno = models.IntegerField(db_column='InvoiceNo')  # Field name made lowercase.
    invoicedate = models.DateField(db_column='InvoiceDate')  # Field name made lowercase.
    senddate = models.DateField(db_column='SendDate', blank=True, null=True)  # Field name made lowercase.
    confirmdate = models.DateField(db_column='ConfirmDate', blank=True, null=True)  # Field name made lowercase.
    sgp_r = models.IntegerField(db_column='SGP_R', blank=True, null=True)  # Field name made lowercase.
    sgp_fc = models.BigIntegerField(db_column='SGP_FC', blank=True, null=True)  # Field name made lowercase.
    cgp_r = models.IntegerField(db_column='CGP_R', blank=True, null=True)  # Field name made lowercase.
    cgp_fc = models.BigIntegerField(db_column='CGP_FC', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    file = models.FileField(db_column='File', storage=invoiceDox_fs, null=True, unique=True)
    active = models.BooleanField(db_column='Active')  # Field name made lowercase.

    def invoiceshamsidate(self):
        """
        Get the invoice shamsi date for the InvoiceDox model.
        """
        return gregorian_to_shamsi(self.invoicedate) if self.invoicedate is not None else ''

    def sendshamsidate(self):
        """
        Get the send date for the InvoiceDox model.
        """
        return gregorian_to_shamsi(self.senddate) if self.senddate is not None else ''

    def confirmshamsidate(self):
        """
        Get the confirm date for the InvoiceDox model.
        """
        return gregorian_to_shamsi(self.confirmdate) if self.confirmdate is not None else ''

    def filename(self):
        """
        Get the filename for the InvoiceDox model.
        """
        if self.file:
            return self.file.name.split('/')[-1:][0]
        return ''
    
    class Meta:
        db_table = 'tblw_InvoiceDox'

# @receiver(pre_save, sender=InvoiceDox)
# def invoiceDox_file_pre_save(sender, instance, *args, **kwargs):
#     invoiceDox = InvoiceDox.objects.all()
#     if len(invoiceDox) == 0:
#         return
#     # As it was not yet saved, we get the instance from DB with 
#     # the old file name to delete it. Which won't happen if it's a new instance
#     if instance and instance.invoicedoxid and instance.file:
#         invoiceDoc = InvoiceDox.objects.get(pk=instance.invoicedoxid)
#         if invoiceDoc and invoiceDoc.file and invoiceDoc.file != instance.file:
#             storage, path = invoiceDoc.file.storage, invoiceDoc.file.path
#             if storage.exists(path):
#                 storage.delete(path)

@receiver(pre_delete, sender=InvoiceDox)
def invoiceDox_file_pre_delete(sender, instance, *args, **kwargs):
    """
    Deletes image files on `post_delete` for the InvoiceDox model.
    """
    # Deletes image files on `post_delete`
    if instance.file:
        storage, path = instance.file.storage, instance.file.path
        if storage.exists(path):
            storage.delete(path)


class ApprovedInvoiceDox(models.Model):
    """
    Approved invoice dox model for the projects_files application.
    """
    approvedinvoicedoxid = models.AutoField(db_column='ApprovedInvoiceDoxId', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_ApprovedInvoiceDox", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_ApprovedInvoiceDox", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    invoicekind = models.PositiveSmallIntegerField(db_column='InvoiceKind')
    invoiceno = models.PositiveSmallIntegerField(db_column='InvoiceNo')
    invoicedate = models.DateField(db_column='InvoiceDate')  # Field name made lowercase.
    senddate = models.DateField(db_column='SendDate', null=True)  # Field name made lowercase.
    confirmdate = models.DateField(db_column='ConfirmDate', null=True)  # Field name made lowercase.
    sgp_r = models.IntegerField(db_column='SGP_R', null=True)
    sgp_fc = models.BigIntegerField(db_column='SGP_FC', null=True)
    cgp_r = models.IntegerField(db_column='CGP_R', null=True)
    cgp_fc = models.BigIntegerField(db_column='CGP_FC', null=True)
    description = models.CharField(db_column='Description', max_length=250, null=True, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    file = models.FileField(db_column='File', storage=invoiceDox_fs, max_length=250, null=True)
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.

    def invoiceshamsidate(self):
        """
        Get the invoice shamsi date for the ApprovedInvoiceDox model.
        """
        return gregorian_to_shamsi(self.invoicedate) if self.invoicedate is not None else ''

    def sendshamsidate(self):
        """
        Get the send date for the ApprovedInvoiceDox model.
        """
        return gregorian_to_shamsi(self.senddate) if self.senddate is not None else ''

    def confirmshamsidate(self):
        """
        Get the confirm date for the ApprovedInvoiceDox model.
        """
        return gregorian_to_shamsi(self.confirmdate) if self.confirmdate is not None else ''

    def filename(self):
        """
        Get the filename for the ApprovedInvoiceDox model.
        """
        if self.file:
            return self.file.name.split('/')[-1:][0]
        return ''
        
    class Meta:
        db_table = 'tblw_ApprovedInvoiceDox'

# @receiver(pre_save, sender=ApprovedInvoiceDox)
# def approvedInvoiceDox_file_pre_save(sender, instance, *args, **kwargs):
#     projectMonthlyDox = ApprovedInvoiceDox.objects.all()
#     if len(projectMonthlyDox) == 0:
#         return
#     # As it was not yet saved, we get the instance from DB with 
#     # the old file name to delete it. Which won't happen if it's a new instance
#     if instance and instance.approvedinvoicedoxid and instance.file:
#         projectMonthlyDox = ApprovedInvoiceDox.objects.get(approvedinvoicedoxid=instance.approvedinvoicedoxid)
#         if projectMonthlyDox and projectMonthlyDox.file and projectMonthlyDox.file != instance.file:
#             storage, path = projectMonthlyDox.file.storage, projectMonthlyDox.file.path
#             if storage.exists(path):
#                 storage.delete(path)

@receiver(pre_delete, sender=ApprovedInvoiceDox)
def approvedInvoiceDox_file_pre_delete(sender, instance, *args, **kwargs):
    """
    Deletes image files on `post_delete` for the ApprovedInvoiceDox model.
    """
    # Deletes image files on `post_delete`
    if instance.file:
        storage, path = instance.file.storage, instance.file.path
        if storage.exists(path):
            storage.delete(path)


# =========================================             
#                ZONE MODEL
# ========================================= 
class Zone(models.Model):
    """
    Zone model for the projects_files application.
    """
    zoneid = models.AutoField(db_column='ZoneID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_Zone", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    zone = models.CharField(db_column='Zone', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        db_table = 'tblw_Zone'


# =========================================             
#             ZONE IMAGE MODEL
# ========================================= 
zoneImage_fs = FileSystemStorage(location="D:\projects\cost_control\Pmrs_Files\Constructions Pix")
class ProjectZoneImageQuerySet(models.query.QuerySet):
    """
    Project zone image query set for the projects_files application.
    """
    def allProjectZonesImages(self, dateId):
        """
        Get all project zones images for the ProjectZoneImageQuerySet model.
        """
        zoneImages1 = self.filter(dateid__lte=dateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img1', 'description1').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img1'), 
            description=F('description1')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description1', output_field=CharField()) 
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages2 = self.filter(dateid__lte=dateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img2', 'description2').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img2'), 
            description=F('description2')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description2', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages3 = self.filter(dateid__lte=dateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img3', 'description3').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img3'), 
            description=F('description3')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description3', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')

        return zoneImages1.union(zoneImages2).union(zoneImages3)   

    def allProjectZonesImagesEx(self, fromDateId, toDateId):
        """
        Get all project zones images for the ProjectZoneImageQuerySet model.
        """
        zoneImages1 = self.filter(dateid__gte=fromDateId, dateid__lte=toDateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img1', 'description1').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img1'), 
            description=F('description1')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description1', output_field=CharField()) 
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages2 = self.filter(dateid__gte=fromDateId, dateid__lte=toDateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img2', 'description2').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img2'), 
            description=F('description2')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description2', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages3 = self.filter(dateid__gte=fromDateId, dateid__lte=toDateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img3', 'description3').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img3'), 
            description=F('description3')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description3', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')

        return zoneImages1.union(zoneImages2).union(zoneImages3)   
       
    def projectAllZonesImages(self, contractId):
        """
        Get all project zones images for the ProjectZoneImageQuerySet model.
        """
        zoneImages1 = self.filter(zoneid__contractid__exact=contractId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img1', 'description1').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img1'), 
            description=F('description1')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description1', output_field=CharField()) 
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages2 = self.filter(zoneid__contractid__exact=contractId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img2', 'description2').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img2'), 
            description=F('description2')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description2', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages3 = self.filter(zoneid__contractid__exact=contractId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img3', 'description3').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img3'), 
            description=F('description3')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description3', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')

        return zoneImages1.union(zoneImages2).union(zoneImages3)   
    
    def selectedProjectAllZonesImages(self, contractsId, dateId):
        """
        Get all project zones images for the ProjectZoneImageQuerySet model.
        """
        zoneImages1 = self.filter(zoneid__contractid__in=contractsId, dateid__lte=dateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img1', 'description1').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img1'), 
            description=F('description1')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description1', output_field=CharField()) 
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages2 = self.filter(zoneid__contractid__in=contractsId, dateid__lte=dateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img2', 'description2').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img2'), 
            description=F('description2')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description2', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages3 = self.filter(zoneid__contractid__in=contractsId, dateid__lte=dateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img3', 'description3').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img3'), 
            description=F('description3')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description3', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')

        return zoneImages1.union(zoneImages2).union(zoneImages3)   
    
    def selectedProjectAllZonesImagesEx(self, contractsId, fromDateId, toDateId):
        """
        Get all project zones images for the ProjectZoneImageQuerySet model.
        """
        zoneImages1 = self.filter(zoneid__contractid__in=contractsId, dateid__gte=fromDateId, dateid__lte=toDateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img1', 'description1').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img1'), 
            description=F('description1')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description1', output_field=CharField()) 
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages2 = self.filter(zoneid__contractid__in=contractsId, dateid__gte=fromDateId, dateid__lte=toDateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img2', 'description2').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img2'), 
            description=F('description2')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description2', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages3 = self.filter(zoneid__contractid__in=contractsId, dateid__gte=fromDateId, dateid__lte=toDateId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img3', 'description3').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img3'), 
            description=F('description3')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description3', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')

        return zoneImages1.union(zoneImages2).union(zoneImages3)   
    
    def projectZoneImages(self, zoneId):
        """
        Get all project zones images for the ProjectZoneImageQuerySet model.
        """
        zoneImages1 = self.filter(zoneid__exact=zoneId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img1', 'description1').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img1'), 
            description=F('description1')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description1', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages2 = self.filter(zoneid__exact=zoneId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img2', 'description2').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img2'), 
            description=F('description2')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description2', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')
        zoneImages3 = self.filter(zoneid__exact=zoneId).values(
            'zoneid__contractid__contract', 'zoneid__zone', 'ppp', 'app', 'img3', 'description3').annotate(
            contract=F('zoneid__contractid__contract'), 
            zone=F('zoneid__zone'), 
            img=F('img3'), 
            description=F('description3')
            # description=Concat(Value(' { پروژه: '), 'zoneid__contractid__contract',  
            #                   Value(' } - { درصد پیشرفت برنامه ای: '), 'ppp', Value( ' } - { درصد پیشرفت واقعی: '), 'app', 
            #                   Value(' } - '), 'description1', output_field=CharField())
            ).values('contract', 'zone', 'ppp', 'app', 'img', 'description')

        return zoneImages1.union(zoneImages2).union(zoneImages3)        

class ProjectZoneImageManager(models.Manager):
    """
    Project zone image manager for the projects_files application.
    """
    def get_queryset(self):
        """
        Get the queryset for the ProjectZoneImageManager model.
        """
        return ProjectZoneImageQuerySet(self.model, using=self._db)

    def allProjectZonesImages(self, dateId):
        """
        Get all project zones images for the ProjectZoneImageManager model.
        """
        return self.get_queryset().allProjectZonesImages(dateId)

    def allProjectZonesImagesEx(self, fromDateId, toDateId):
        """
        Get all project zones images for the ProjectZoneImageManager model.
        """
        return self.get_queryset().allProjectZonesImagesEx(fromDateId, toDateId)

    def projectAllZonesImages(self, contractId):
        """
        Get all project zones images for the ProjectZoneImageManager model.
        """
        return self.get_queryset().projectAllZonesImages(contractId)

    def selectedProjectAllZonesImages(self, contractsId, dateId):
        """
        Get all project zones images for the ProjectZoneImageManager model.
        """
        return self.get_queryset().selectedProjectAllZonesImages(contractsId, dateId)

    def selectedProjectAllZonesImagesEx(self, contractsId, fromDateId, toDateId):
        """
        Get all project zones images for the ProjectZoneImageManager model.
        """
        return self.get_queryset().selectedProjectAllZonesImagesEx(contractsId, fromDateId, toDateId)

    def projectZoneImages(self, zoneId):
        """
        Get all project zones images for the ProjectZoneImageManager model.
        """
        return self.get_queryset().projectZoneImages(zoneId)        


class ZoneImage(models.Model):
    """
    Zone image model for the projects_files application.
    """
    zoneimageid = models.AutoField(db_column='ZoneImageID', primary_key=True)  # Field name made lowercase.
    zoneid = models.ForeignKey(Zone, related_name="Zone_Zoneimage", 
                                   on_delete=models.PROTECT, db_column='ZoneID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate, related_name="ReportDate", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.    
    ppp = models.DecimalField(db_column='PPP', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    app = models.DecimalField(db_column='APP', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    pic1 = models.CharField(db_column='Pic1', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    img1 = models.ImageField(db_column='Img1', upload_to='zone_images', max_length=250, blank=True, null=True, unique=True)
    description1 = models.CharField(db_column='Description1', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pic2 = models.CharField(db_column='Pic2', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    img2 = models.ImageField(db_column='Img2', upload_to='zone_images', max_length=250, blank=True, null=True, unique=True)
    description2 = models.CharField(db_column='Description2', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pic3 = models.CharField(db_column='Pic3', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    img3 = models.ImageField(db_column='Img3', upload_to='zone_images', max_length=250, blank=True, null=True, unique=True)
    description3 = models.CharField(db_column='Description3', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()
    projectZoneImages = ProjectZoneImageManager()
    
    def zone(self):
        """
        Get the zone for the ZoneImage model.
        """
        return self.zoneid.zone
    
    def contract(self):
        """
        Get the contract for the ZoneImage model.
        """
        return self.zoneid.contractid.contract
    
    def imagepath1(self):
        """
        Get the image path for the ZoneImage model.
        """
        if self.img1: 
            return self.img1.name.split('/')[-1:][0]
        return ''

    def imagepath2(self):
        """
        Get the image path for the ZoneImage model.
        """
        if self.img2:
            return self.img2.name.split('/')[-1:][0]
        return ''
    
    def imagepath3(self):
        """
        Get the image path for the ZoneImage model.
        """
        if self.img3:
            return self.img3.name.split('/')[-1:][0]
        # 
        return ''
    
    @property
    def explanation(self):
        """
        Get the explanation for the ZoneImage model.
        """
        return 'پروژه: %s - سازه: %s -  درصد پیشرفت برنامه ای: %s - درصد پیشرفت واقعی: %s - %s'  % (
            self.zoneid.contractid.contract,self.zoneid.zone, self.ppp, self.app, self.description)
    
    class Meta:
        db_table = 'tblw_ZoneImage'

# @receiver(pre_save, sender=ZoneImage)
# def zone_image_pre_save(sender, instance, *args, **kwargs):
#     zoneImages = ZoneImage.objects.all()
#     if len(zoneImages) == 0:
#         return
#     # As it was not yet saved, we get the instance from DB with 
#     # the old file name to delete it. Which won't happen if it's a new instance
#     if instance and instance.zoneimageid:
#         zoneImage = ZoneImage.objects.get(pk=instance.zoneimageid)
#         if instance.img1:
#             if zoneImage and zoneImage.img1 and zoneImage.img1 != instance.img1:
#                 storage, path = zoneImage.img1.storage, zoneImage.img1.path
#                 if storage.exists(path):
#                     storage.delete(path)
#         if instance.img2:
#             if zoneImage and zoneImage.img2 and zoneImage.img2 != instance.img2:
#                 storage, path = zoneImage.img2.storage, zoneImage.img2.path
#                 if storage.exists(path):
#                     storage.delete(path)
#         if instance.img3:
#             if zoneImage and zoneImage.img3 and zoneImage.img3 != instance.img3:
#                 storage, path = zoneImage.img3.storage, zoneImage.img3.path
#                 if storage.exists(path):
#                     storage.delete(path)
                                
@receiver(pre_delete, sender=ZoneImage)
def zone_image_pre_delete(sender, instance, *args, **kwargs):
    """
    Deletes image files on `post_delete` for the ZoneImage model.
    """
    # Deletes image files on `post_delete`
    if instance.img1:
        storage, path = instance.img1.storage, instance.img1.path
        if storage.exists(path):
            storage.delete(path)
    if instance.img2:
        storage, path = instance.img2.storage, instance.img2.path
        if storage.exists(path):
            storage.delete(path)
    if instance.img3:
        storage, path = instance.img3.storage, instance.img3.path
        if storage.exists(path):
            storage.delete(path)


#============================================================================
fs = FileSystemStorage(location="D:/projects/cost_control/files/projectsDox/hseDox")
def fileSystemStorage(instance, filename):
    """
    File system storage for the projects_files application.
    """
    location="D:/projects/cost_control/files/projectsDox/hseDox"
    fullname = os.path.join(location, filename)
    if os.path.exists(fullname):
        os.remove(fullname)
    fs = FileSystemStorage(location="D:\projects\cost_control\Pmrs Files\Hse Reports")
    return fs


class ReportDox(models.Model):
    """
    Report dox model for the projects_files application.
    """
    reportdoxid = models.AutoField(db_column='ReportDoxID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_ReportDox", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_ReportDox", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    doctype = models.SmallIntegerField(db_column='DocType')  # Field name made lowercase.
    doctitle = models.SmallIntegerField(db_column='DocTitle', blank=True, null=True)  # Field name made lowercase.
    dockind = models.SmallIntegerField(db_column='DocKind', blank=True, null=True)  # Field name made lowercase.
    docno = models.IntegerField(db_column='DocNo', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    file = models.FileField(db_column='File', storage=fs, null=True)
    address = models.CharField(db_column='Address', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'tblw_ReportDox'

@receiver(pre_save,  sender=ReportDox)
def attachment_file_update(sender, **kwargs):
    """
    Attachment file update for the ReportDox model.
    """
    reportDox = kwargs['instance']
    # As it was not yet saved, we get the instance from DB with 
    # the old file name to delete it. Which won't happen if it's a new instance
    if reportDox.contractid and reportDox.dateid:
        reportDox = ReportDox.objects.get(contractid=reportDox.contractid, dateid=reportDox.dateid)
        storage, path = reportDox.file.storage, reportDox.file.path
        storage.delete(path)


# =========================================             
#            REPORT VISIT MODEL
# ========================================= 
class ReportVisit(models.Model):
    """
    Report visit model for the projects_files application.
    """
    reportvisitid = models.AutoField(db_column='ReportVisitID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reportVisits", 
                                   on_delete=models.PROTECT, db_column='UserID')  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="reportVisits", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="reportVisits", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    financialinfo = models.BooleanField(default=False, db_column='FinancialInfo')  # Field name made lowercase.
    hse = models.BooleanField(default=False, db_column='HSE')  # Field name made lowercase.
    progressstate = models.BooleanField(default=False, db_column='ProgressState')  # Field name made lowercase.
    timeprogressstate = models.BooleanField(default=False, db_column='TimeProgressState')  # Field name made lowercase.
    invoice = models.BooleanField(default=False, db_column='Invoice')  # Field name made lowercase.
    financialinvoice = models.BooleanField(default=False, db_column='FinancialInvoice')  # Field name made lowercase.
    workvolume = models.BooleanField(default=False, db_column='WorkVolume')  # Field name made lowercase.
    pmsprogress = models.BooleanField(default=False, db_column='PMSProgress')  # Field name made lowercase.
    budget = models.BooleanField(default=False, db_column='Budget')  # Field name made lowercase.
    machinary = models.BooleanField(default=False, db_column='Machinary')  # Field name made lowercase.
    personel = models.BooleanField(default=False, db_column='Personel')  # Field name made lowercase.
    problems = models.BooleanField(default=False, db_column='Problems')  # Field name made lowercase.
    criticalactions = models.BooleanField(default=False, db_column='CriticalActions')  # Field name made lowercase.
    zoneimages = models.BooleanField(default=False, db_column='ZoneImages')  # Field name made lowercase.
    projectdox = models.BooleanField(default=False, db_column='ProjectDox')  # Field name made lowercase.
    durationdox = models.BooleanField(default=False, db_column='DurationDox')  # Field name made lowercase.
    dashboard_r = models.BooleanField(default=False, db_column='Dashboard_R')  # Field name made lowercase.
    dashboard_fc = models.BooleanField(default=False, db_column='Dashboard_FC')  # Field name made lowercase.
    imagereport = models.BooleanField(default=False, db_column='ImageReport')  # Field name made lowercase.

    def manager(self):
        """
        Get the manager for the ReportVisit model.
        """
        return '%s %s' % (self.userid.first_name, self.userid.last_name)     

    class Meta:
        db_table = 'tblw_ReportVisit'
        unique_together = (('userid', 'contractid', 'dateid'),)


# =========================================             
#            REPORT VISIT DATE MODEL
# ========================================= 
class ReportVisitdate(models.Model):
    """
    Report visit date model for the projects_files application.
    """
    visitreportdateid = models.AutoField(db_column='VisitReportDateID', primary_key=True)  # Field name made lowercase.
    visitreportid = models.ForeignKey(ReportVisit, related_name="ReportVisitdates", 
                                   on_delete=models.PROTECT, db_column='VisitReportID')  # Field name made lowercase.
    reportid = models.IntegerField(db_column='ReportID')  # Field name made lowercase.
    reportvisitdate = models.DateField(default=django.utils.timezone.now, db_column='ReportVisitDate')  # Field name made lowercase.

    class Meta:
        db_table = 'tblw_ReportVisitDate'




