"""
Models for the projects application.
"""
from django.db import models
from django.db.models import F, Sum, Max
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber
from django.dispatch import receiver
from django.utils import timezone

from django.conf import settings
from contracts.models import Contract, EpcCorporation
from contracts.services import GregorianToShamsi, GregorianToShamsiShow


class ReportDate(models.Model):
    """
    Report date model for the projects application.
    """
    dateid = models.AutoField(db_column='DateID', primary_key=True)  # Field name made lowercase.
    year = models.CharField(db_column='Year', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    month = models.CharField(db_column='Month', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    def shamsiDate(self):
        """
        Get the shamsi date for the report date.
        """
        return '%s-%s' % (self.year, self.month)
    # GregorianToShamsi(self.date)
    
    class Meta:
        db_table = 'tblw_ReportDate'
        
        
class ContractReportDate(models.Model):
    """
    Contract report date model for the projects application.
    """
    contractid = models.ForeignKey(Contract, related_name="Contract_ContractReportDate", on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate, related_name="ReportDate_ContractReportDate", on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.

    class Meta:
        db_table = 'tbl_JContractReportDate'
        verbose_name = 'Contract_ReportDate'
        verbose_name_plural = 'Contract_ReportDates'
        
        
class ReportConfirm(models.Model):
    """
    Report confirm model for the projects application.
    """
    reportconfirmid = models.AutoField(db_column='ReportConfirmID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="reportConfirms", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate, related_name="reportConfirms", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    userid = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reportConfirms", 
                                   on_delete=models.PROTECT, db_column='UserID')  # Field name made lowercase.
    type = models.SmallIntegerField(db_column='Type', blank=True, null=True)  # Field name made lowercase.
    user_c = models.BooleanField(db_column='User_C', blank=True, null=True)  # Field name made lowercase.
    pm_c = models.BooleanField(db_column='PM_C', blank=True, null=True)  # Field name made lowercase.
    sa_c = models.BooleanField(db_column='SA_C', blank=True, null=True)  # Field name made lowercase.
    userconfirmdate = models.DateField(db_column='UserConfirmDate', blank=True, null=True)  # Field name made lowercase.
    pmconfirmdate = models.DateField(db_column='PMConfirmDate', blank=True, null=True)  # Field name made lowercase.
    saconfirmdate = models.DateField(db_column='SAConfirmDate', blank=True, null=True)  # Field name made lowercase.

    def userconfirmer(self):
        """
        Get the user confirm date for the report confirm.
        """
        return '%s %s' % (self.userid.first_name, self.userid.last_name)     
       
    def userconfirmshamsidate(self):
        """
        Get the shamsi date for the user confirm date.
        """
        return GregorianToShamsiShow(self.userconfirmdate) if self.userconfirmdate is not None else ''
 
    def pmconfirmshamsidate(self):
        """
        Get the shamsi date for the pm confirm date.
        """
        return GregorianToShamsiShow(self.pmconfirmdate) if self.pmconfirmdate is not None else ''

    def saconfirmshamsidate(self):
        """
        Get the shamsi date for the sa confirm date.
        """
        return GregorianToShamsiShow(self.saconfirmdate) if self.saconfirmdate is not None else ''
    
    class Meta:
        db_table = 'tblw_ReportConfirm'
    
        
class BudgetCostManager(models.Manager):
    """
    Budget cost manager for the projects application.
    """
    def get_queryset(self):
        result = (
            super().get_queryset().order_by("budgetcostid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("budgetcostid")]
                )
            )
            .values("budgetcostid", "contractid", "dateid", "bac_r", "bac_fc", 
                    "eac_r", "eac_fc", "ev_r", "ev_fc", "ac_r", "ac_fc", "description", "row_number")
        )
        """
        Get the budget cost for the contract month.
        """
        return result


class Budgetcost(models.Model):
    """
    Budget cost model for the projects application.
    """
    budgetcostid = models.AutoField(db_column='BudgetCostID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_BudgetCost", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_BudgetCost", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    bac_r = models.BigIntegerField(db_column='BAC_R', blank=True, null=True)  # Field name made lowercase.
    bac_fc = models.BigIntegerField(db_column='BAC_FC', blank=True, null=True)  # Field name made lowercase.
    eac_r = models.BigIntegerField(db_column='EAC_R', blank=True, null=True)  # Field name made lowercase.
    eac_fc = models.BigIntegerField(db_column='EAC_FC', blank=True, null=True)  # Field name made lowercase.
    ev_r = models.BigIntegerField(db_column='EV_R', blank=True, null=True)  # Field name made lowercase.
    ev_fc = models.BigIntegerField(db_column='EV_FC', blank=True, null=True)  # Field name made lowercase.
    ac_r = models.BigIntegerField(db_column='AC_R', blank=True, null=True)  # Field name made lowercase.
    ac_fc = models.BigIntegerField(db_column='AC_FC', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=250, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = BudgetCostManager()

    def year(self):
        """
        Get the year for the budget cost.
        """
        return self.dateid.year
    
    def month(self):
        """
        Get the month for the budget cost.
        """
        return self.dateid.month
        
    def persianMonth(self):
        """
        Get the persian month for the budget cost.
        """
        month = int(self.dateid.month)
        if(month < 7):
            if(month < 4):
                if(month == 1):
                    return 'فروردین'
                elif(month == 2):
                    return 'اردیبهشت'
                elif(month == 3):
                    return 'خرداد'
            else:
                if(month == 4):
                    return 'تیر'        
                elif(month == 5):
                    return 'مرداد'
                elif(month == 6):
                    return 'شهریور' 
        else:     
            if(month < 10):
                if(month == 7):
                    return 'مهر'        
                elif(month == 8):
                    return 'آبان'        
                elif(month == 9):
                    return 'آذر'
            else:
                if(month == 10):
                    return 'دی'        
                elif(month == 11):
                    return 'بهمن'        
                elif(month == 12):
                    return 'اسفند'
         
        
    class Meta:
        db_table = 'tblw_BudgetCost'


class CriticalActionManager(models.Manager):
    """
    Critical action manager for the projects application.
    """
    def get_queryset(self):
        result = (
            super().get_queryset().order_by("criticalactionid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("criticalactionid")]
                )
            )
            .values("criticalactionid", "contractid", "dateid", "criticalaction", "row_number")
        )
        return result


class CriticalAction(models.Model):
    """
    Critical action model for the projects application.
    """
    criticalactionid = models.AutoField(db_column='CriticalActionID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_CriticalAction", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_CriticalAction", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    criticalaction = models.CharField(db_column='CriticalAction', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = CriticalActionManager()

    class Meta:
        db_table = 'tblw_CriticalAction'


class DateConversion(models.Model):
    """
    Date conversion model for the projects application.
    """
    monthid = models.IntegerField(db_column='MonthID')  # Field name made lowercase.
    month = models.CharField(db_column='Month', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        db_table = 'tblw_DateConversion'


class FinancialInfo(models.Model):
    """
    Financial info model for the projects application.
    """
    financialinfoid = models.AutoField(db_column='FinancialInfoID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_Financialinfo", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_Financialinfo", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    lastclaimedinvoice_r = models.BigIntegerField(db_column='LastClaimedInvoice_r', blank=True, null=True)  # Field name made lowercase.
    lastclaimedinvoice_fc = models.BigIntegerField(db_column='LastClaimedInvoice_FC', blank=True, null=True)  # Field name made lowercase.
    lci_no = models.SmallIntegerField(db_column='LCI_No', blank=True, null=True)  # Field name made lowercase.
    lastverifiedinvoice_r = models.BigIntegerField(db_column='LastVerifiedInvoice_R', blank=True, null=True)  # Field name made lowercase.
    lastverifiedinvoice_fc = models.BigIntegerField(db_column='LastVerifiedInvoice_FC', blank=True, null=True)  # Field name made lowercase.
    lvi_no = models.SmallIntegerField(db_column='LVI_No', blank=True, null=True)  # Field name made lowercase.
    lastclaimedadjustmentinvoice_r = models.BigIntegerField(db_column='LastClaimedAdjustmentInvoice_R', blank=True, null=True)  # Field name made lowercase.
    lastclaimedadjustmentinvoice_fc = models.BigIntegerField(db_column='LastClaimedAdjustmentInvoice_FC', blank=True, null=True)  # Field name made lowercase.
    lcai_no = models.SmallIntegerField(db_column='LCAI_No', blank=True, null=True)  # Field name made lowercase.
    lastverifiedadjustmentinvoice_r = models.BigIntegerField(db_column='LastVerifiedAdjustmentInvoice_R', blank=True, null=True)  # Field name made lowercase.
    lastverifiedadjustmentinvoice_fc = models.BigIntegerField(db_column='LastVerifiedAdjustmentInvoice_FC', blank=True, null=True)  # Field name made lowercase.
    lvai_no = models.SmallIntegerField(db_column='LVAI_No', blank=True, null=True)  # Field name made lowercase.
    lastclaimedextraworkinvoice_r = models.BigIntegerField(db_column='LastClaimedExtraWorkInvoice_R', blank=True, null=True)  # Field name made lowercase.
    lastclaimedextraworkinvoice_fc = models.BigIntegerField(db_column='LastClaimedExtraWorkInvoice_FC', blank=True, null=True)  # Field name made lowercase.
    lcewi_no = models.SmallIntegerField(db_column='LCEWI_No', blank=True, null=True)  # Field name made lowercase.
    lastverifiedextraworkinvoice_r = models.BigIntegerField(db_column='LastVerifiedExtraWorkInvoice_R', blank=True, null=True)  # Field name made lowercase.
    lastverifiedextraworkinvoice_fc = models.BigIntegerField(db_column='LastVerifiedExtraWorkInvoice_FC', blank=True, null=True)  # Field name made lowercase.
    lvewi_no = models.SmallIntegerField(db_column='LVEWI_No', blank=True, null=True)  # Field name made lowercase.
    lastclaimbill_r = models.BigIntegerField(db_column='LastClaimBill_R', blank=True, null=True)  # Field name made lowercase.
    lastclaimbill_fc = models.BigIntegerField(db_column='LastClaimBill_FC', blank=True, null=True)  # Field name made lowercase.
    lcb_no = models.SmallIntegerField(db_column='LCB_No', blank=True, null=True)  # Field name made lowercase.
    lastclaimbillverified_r = models.BigIntegerField(db_column='LastClaimBillVerified_R', blank=True, null=True)  # Field name made lowercase.
    lastclaimbillverified_fc = models.BigIntegerField(db_column='LastClaimBillVerified_FC', blank=True, null=True)  # Field name made lowercase.
    lcbv_no = models.SmallIntegerField(db_column='LCBV_No', blank=True, null=True)  # Field name made lowercase.
    lastclaimbillrecievedamount_r = models.BigIntegerField(db_column='LastClaimBillRecievedAmount_R', blank=True, null=True)  # Field name made lowercase.
    lastclaimbillrecievedamount_fc = models.BigIntegerField(db_column='LastClaimBillRecievedAmount_FC', blank=True, null=True)  # Field name made lowercase.
    cumulativeclientpayment_r = models.BigIntegerField(db_column='CumulativeClientPayment_R', blank=True, null=True)  # Field name made lowercase.
    cumulativeclientpayment_fc = models.BigIntegerField(db_column='CumulativeClientPayment_FC', blank=True, null=True)  # Field name made lowercase.
    clientprepaymentdeferment_r = models.BigIntegerField(db_column='ClientPrepaymentDeferment_R', blank=True, null=True)  # Field name made lowercase.
    clientprepaymentdeferment_fc = models.BigIntegerField(db_column='ClientPrepaymentDeferment_FC', blank=True, null=True)  # Field name made lowercase.
    estcost_r = models.BigIntegerField(db_column='EstCost_R', blank=True, null=True)  # Field name made lowercase.
    estcost_fc = models.BigIntegerField(db_column='EstCost_FC', blank=True, null=True)  # Field name made lowercase.
    estclientpayment_r = models.BigIntegerField(db_column='EstClientPayment_R', blank=True, null=True)  # Field name made lowercase.
    estclientpayment_fc = models.BigIntegerField(db_column='EstClientPayment_FC', blank=True, null=True)  # Field name made lowercase.
    estdebitcredit_r = models.BigIntegerField(db_column='EstDebitCredit_R', blank=True, null=True)  # Field name made lowercase.
    estdebitcredit_fc = models.BigIntegerField(db_column='EstDebitCredit_FC', blank=True, null=True)  # Field name made lowercase.

    def isconfirmed(self):
        """
        Get the is confirmed for the financial info.
        """
        rc = ReportConfirm.objects.filter(contractid__exact=self.contractid, dateid__exact=self.dateid, type__exact=1)[0]
        return rc.user_c or 0 if rc is not None else 0    
    
    def confirmdate(self):
        """
        Get the confirm date for the financial info.
        """
        rc = ReportConfirm.objects.filter(contractid__exact=self.contractid, dateid__exact=self.dateid, type__exact=1)[0]
        return GregorianToShamsi(rc.userconfirmdate) or '' if rc is not None else ''

    class Meta:
        db_table = 'tblw_FinancialInfo'


class Hse(models.Model):
    """
    HSE model for the projects application.
    """
    hseid = models.AutoField(db_column='HSEID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_Hse", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_Hse", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    totaloperationdays = models.IntegerField(db_column='TotalOperationDays', blank=True, null=True)  # Field name made lowercase.
    withouteventdays = models.IntegerField(db_column='WithoutEventDays', blank=True, null=True)  # Field name made lowercase.
    deathno = models.IntegerField(db_column='DeathNo', blank=True, null=True)  # Field name made lowercase.
    woundno = models.IntegerField(db_column='WoundNo', blank=True, null=True)  # Field name made lowercase.
    disadvantageeventno = models.IntegerField(db_column='DisadnantageEventNo', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()

    def totaldeathno(self):
        """
        Get the total death no for the HSE.
        """
        deathno_sum = Hse.objects.filter(contractid__exact=self.contractid, 
                                         dateid__lte=self.dateid).aggregate(Sum('deathno'))['deathno__sum']
        return deathno_sum

    def totalwoundno(self):
        """
        Get the total wound no for the HSE.
        """
        woundno_sum = Hse.objects.filter(contractid__exact=self.contractid, 
                                         dateid__lte=self.dateid).aggregate(Sum('woundno'))['woundno__sum']
        return woundno_sum
    
    def totaldisadvantageeventno(self):
        """
        Get the total disadvantage event no for the HSE.
        """
        disadvantageeventno_sum = Hse.objects.filter(contractid__exact=self.contractid, 
                                         dateid__lte=self.dateid).aggregate(Sum('disadvantageeventno'))['disadvantageeventno__sum']
        return disadvantageeventno_sum
            
    def isconfirmed(self):
        """
        Get the is confirmed for the HSE.
        """
        rc = ReportConfirm.objects.filter(contractid__exact=self.contractid, dateid__exact=self.dateid, type__exact=2)[0]
        return rc.user_c or 0 if rc is not None else 0    
    
    def confirmdate(self):
        """
        Get the confirm date for the HSE.
        """
        rc = ReportConfirm.objects.filter(contractid__exact=self.contractid, dateid__exact=self.dateid, type__exact=2)[0]
        return GregorianToShamsi(rc.userconfirmdate) or '' if rc is not None else ''
    
    class Meta:
        db_table = 'tblw_HSE'


class InvoiceManager(models.Manager):
    """
    Invoice manager for the projects application.
    """
    def get_queryset(self):
        """
        Get the queryset for the invoice.
        """
        result = (
            super().get_queryset().order_by("invoiceid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("invoiceid")]
                )
            )
            .values("invoiceid", "contractid", "dateid", "senddate", "aci_g_r", "aci_g_fc", "aca_g_r", "aca_g_fc", 
                    "ew_g_r", "ew_g_fc", "icc_g_r", "icc_g_fc", "acc_g_r", "acc_g_fc", "ewcc_g_r", "ewcc_g_fc", 
                    "aci_n_r", "aci_n_fc", "aca_n_r", "aca_n_fc", "ew_n_r", "ew_n_fc", "icc_n_r", "icc_n_fc", 
                    "acc_n_r", "acc_n_fc", "ewcc_n_r", "ewcc_n_fc", "cvat_r", "cvat_fc", "cpi_r", "cpi_fc", 
                    "ccpi_a_r", "ccpi_a_fc", "ccpi_a_vat_r", "ccpi_a_vat_fc", "ccpi_a_vat_ew_r", "ccpi_a_vat_ew_fc", 
                    "cp_pp_r", "cp_pp_fc", "pp_pp_r", "pp_pp_fc", "r", "m", "description", "row_number")
        )
        return result


class Invoice(models.Model):
    """
    Invoice model for the projects application.
    """
    invoiceid = models.AutoField(db_column='InvoiceID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_Invoice", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_Invoice", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    senddate = models.DateTimeField(db_column='SendDate', default=timezone.now, blank=True, null=True)  # Field name made lowercase.
    aci_g_r = models.BigIntegerField(db_column='ACI_G_R', blank=True, null=True)  # Field name made lowercase.
    aci_g_fc = models.BigIntegerField(db_column='ACI_G_FC', blank=True, null=True)  # Field name made lowercase.
    aca_g_r = models.BigIntegerField(db_column='ACA_G_R', blank=True, null=True)  # Field name made lowercase.
    aca_g_fc = models.BigIntegerField(db_column='ACA_G_FC', blank=True, null=True)  # Field name made lowercase.
    ew_g_r = models.BigIntegerField(db_column='EW_G_R', blank=True, null=True)  # Field name made lowercase.
    ew_g_fc = models.BigIntegerField(db_column='EW_G_FC', blank=True, null=True)  # Field name made lowercase.
    icc_g_r = models.BigIntegerField(db_column='ICC_G_R', blank=True, null=True)  # Field name made lowercase.
    icc_g_fc = models.BigIntegerField(db_column='ICC_G_FC', blank=True, null=True)  # Field name made lowercase.
    acc_g_r = models.BigIntegerField(db_column='ACC_G_R', blank=True, null=True)  # Field name made lowercase.
    acc_g_fc = models.BigIntegerField(db_column='ACC_G_FC', blank=True, null=True)  # Field name made lowercase.
    ewcc_g_r = models.BigIntegerField(db_column='EWCC_G_R', blank=True, null=True)  # Field name made lowercase.
    ewcc_g_fc = models.BigIntegerField(db_column='EWCC_G_FC', blank=True, null=True)  # Field name made lowercase.
    aci_n_r = models.BigIntegerField(db_column='ACI_N_R', blank=True, null=True)  # Field name made lowercase.
    aci_n_fc = models.BigIntegerField(db_column='ACI_N_FC', blank=True, null=True)  # Field name made lowercase.
    aca_n_r = models.BigIntegerField(db_column='ACA_N_R', blank=True, null=True)  # Field name made lowercase.
    aca_n_fc = models.BigIntegerField(db_column='ACA_N_FC', blank=True, null=True)  # Field name made lowercase.
    icc_n_r = models.BigIntegerField(db_column='ICC_N_R', blank=True, null=True)  # Field name made lowercase.
    icc_n_fc = models.BigIntegerField(db_column='ICC_N_FC', blank=True, null=True)  # Field name made lowercase.
    acc_n_r = models.BigIntegerField(db_column='ACC_N_R', blank=True, null=True)  # Field name made lowercase.
    acc_n_fc = models.BigIntegerField(db_column='ACC_N_FC', blank=True, null=True)  # Field name made lowercase.
    ewcc_n_r = models.BigIntegerField(db_column='EWCC_N_R', blank=True, null=True)  # Field name made lowercase.
    ewcc_n_fc = models.BigIntegerField(db_column='EWCC_N_FC', blank=True, null=True)  # Field name made lowercase.
    ew_n_r = models.BigIntegerField(db_column='EW_N_R', blank=True, null=True)  # Field name made lowercase.
    ew_n_fc = models.BigIntegerField(db_column='EW_N_FC', blank=True, null=True)  # Field name made lowercase.
    cvat_r = models.BigIntegerField(db_column='CVAT_R', blank=True, null=True)  # Field name made lowercase.
    cvat_fc = models.BigIntegerField(db_column='CVAT_FC', blank=True, null=True)  # Field name made lowercase.
    cpi_r = models.BigIntegerField(db_column='CPI_R', blank=True, null=True)  # Field name made lowercase.
    cpi_fc = models.BigIntegerField(db_column='CPI_FC', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_r = models.BigIntegerField(db_column='CCPI_A_R', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_fc = models.BigIntegerField(db_column='CCPI_A_FC', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_vat_r = models.BigIntegerField(db_column='CCPI_A_VAT_R', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_vat_fc = models.BigIntegerField(db_column='CCPI_A_VAT_FC', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_vat_ew_r = models.BigIntegerField(db_column='CCPI_A_VAT_EW_R', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_vat_ew_fc = models.BigIntegerField(db_column='CCPI_A_VAT_EW_FC', blank=True, null=True)  # Field name made lowercase.
    cp_pp_r = models.BigIntegerField(db_column='CP_PP_R', blank=True, null=True)  # Field name made lowercase.
    cp_pp_fc = models.BigIntegerField(db_column='CP_PP_FC', blank=True, null=True)  # Field name made lowercase.
    pp_pp_r = models.BigIntegerField(db_column='PP_PP_R', blank=True, null=True)  # Field name made lowercase.
    pp_pp_fc = models.BigIntegerField(db_column='PP_PP_FC', blank=True, null=True)  # Field name made lowercase.
    r = models.BooleanField(db_column='R', blank=True, null=True)  # Field name made lowercase.
    m = models.BooleanField(db_column='M', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = InvoiceManager()

    def year(self):
        """
        Get the year for the invoice.
        """
        return self.dateid.year
    
    def month(self):
        """
        Get the month for the invoice.
        """
        return self.dateid.month
    
    def sendshamsidate(self):
        """
        Get the send date for the invoice.
        """
        return GregorianToShamsi(self.senddate) if self.senddate is not None else ''

    def confirmedInvoiceAmounts(self):
        """
        Get the confirmed invoice amounts for the invoice.
        """
        return (self.aci_g_r or 0) + (self.aca_g_r or 0) + (self.ew_g_r or 0)
 
    def sentInvoiceAmounts(self):
        """
        Get the sent invoice amounts for the invoice.
        """
        return (self.icc_g_r or 0) + (self.acc_g_r or 0) + (self.ewcc_g_r or 0)

    def allReceived(self):
        """
        Get the all received for the invoice.
        """
        a = ((self.ccpi_a_vat_ew_r or 0) - (self.cvat_r or 0))
        return a

    def confirmedAmount(self):
        """
        Get the confirmed amount for the invoice.
        """
        b = ((self.aci_n_r or 0) + (self.aca_n_r or 0) + (self.ew_n_r or 0)) 
        return b 

    def receivePercent(self):
        """
        Get the receive percent for the invoice.
        """
        a = ((self.ccpi_a_vat_ew_r or 0) - (self.cvat_r or 0))
        b = ((self.aci_n_r or 0) + (self.aca_n_r or 0) + (self.ew_n_r or 0)) 
        return 0 if b == 0 else (a / b) * 100

    def totalCumulativeReceiveAmount(self):
        """
        Get the total cumulative receive amount for the invoice.
        """
        financialInfos = FinancialInfo.objects.filter(contractid__exact=self.contractid, dateid__exact=self.dateid)
        financialInfo = financialInfos[0] if financialInfos and len(financialInfos) > 0 else None
        lastclaimbill = financialInfo.lastclaimbill_r if financialInfo else 0
        
        return (self.ccpi_a_vat_ew_r or 0) + (lastclaimbill or 0)
        
    def persianMonth(self):
        """
        Get the persian month for the invoice.
        """
        month = int(self.dateid.month)
        if(month < 7):
            if(month < 4):
                if(month == 1):
                    return 'فروردین'
                elif(month == 2):
                    return 'اردیبهشت'
                elif(month == 3):
                    return 'خرداد'
            else:
                if(month == 4):
                    return 'تیر'        
                elif(month == 5):
                    return 'مرداد'
                elif(month == 6):
                    return 'شهریور' 
        else:     
            if(month < 10):
                if(month == 7):
                    return 'مهر'        
                elif(month == 8):
                    return 'آبان'        
                elif(month == 9):
                    return 'آذر'
            else:
                if(month == 10):
                    return 'دی'        
                elif(month == 11):
                    return 'بهمن'        
                elif(month == 12):
                    return 'اسفند'
            
    class Meta:
        db_table = 'tblw_Invoice'


class InvoiceExManager(models.Manager):
    """
    Invoice ex manager for the projects application.
    """
    def get_queryset(self):
        result = (
            super().get_queryset().order_by("invoiceid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("invoiceid")]
                )
            )
            .values("invoiceid", "contractid", "dateid", "senddate", "invoicetype", "alino", "almino", "aci_g_r", 
                    "aci_g_fc", "aca_g_r", "aca_g_fc", "ew_g_r", "ew_g_fc", "icc_g_r", "icc_g_fc", "acc_g_r", 
                    "acc_g_fc", "ewcc_g_r", "ewcc_g_fc", "aci_n_r", "aci_n_fc", "aca_n_r", "aca_n_fc", "ew_n_r", 
                    "ew_n_fc", "icc_n_r", "icc_n_fc", "acc_n_r", "acc_n_fc", "ewcc_n_r", "ewcc_n_fc", "cvat_r", 
                    "cvat_fc", "cpi_r", "cpi_fc", "ccpi_a_r", "ccpi_a_fc", "ccpi_a_vat_r", "ccpi_a_vat_fc", 
                    "ccpi_a_vat_ew_r", "ccpi_a_vat_ew_fc", "cp_pp_r", "cp_pp_fc", "pp_pp_r", "pp_pp_fc", "r", "m", 
                    "typevalue", "row_number")
        )
        return result


class FinancialInvoice(models.Model):
    """
    Financial invoice model for the projects application.
    """
    invoiceid = models.AutoField(db_column='InvoiceID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_InvoiceEx", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_InvoiceEx", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    senddate = models.DateTimeField(db_column='SendDate', default=timezone.now, blank=True, null=True)  # Field name made lowercase.
    invoicetype = models.CharField(db_column='InvoiceType', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    alino = models.IntegerField(db_column='ALINo', blank=True, null=True)  # Field name made lowercase.
    almino = models.IntegerField(db_column='ALMINo', blank=True, null=True)  # Field name made lowercase.
    aci_g_r = models.BigIntegerField(db_column='ACI_G_R', blank=True, null=True)  # Field name made lowercase.
    aci_g_fc = models.BigIntegerField(db_column='ACI_G_FC', blank=True, null=True)  # Field name made lowercase.
    aca_g_r = models.BigIntegerField(db_column='ACA_G_R', blank=True, null=True)  # Field name made lowercase.
    aca_g_fc = models.BigIntegerField(db_column='ACA_G_FC', blank=True, null=True)  # Field name made lowercase.
    ew_g_r = models.BigIntegerField(db_column='EW_G_R', blank=True, null=True)  # Field name made lowercase.
    ew_g_fc = models.BigIntegerField(db_column='EW_G_FC', blank=True, null=True)  # Field name made lowercase.
    icc_g_r = models.BigIntegerField(db_column='ICC_G_R', blank=True, null=True)  # Field name made lowercase.
    icc_g_fc = models.BigIntegerField(db_column='ICC_G_FC', blank=True, null=True)  # Field name made lowercase.
    acc_g_r = models.BigIntegerField(db_column='ACC_G_R', blank=True, null=True)  # Field name made lowercase.
    acc_g_fc = models.BigIntegerField(db_column='ACC_G_FC', blank=True, null=True)  # Field name made lowercase.
    ewcc_g_r = models.BigIntegerField(db_column='EWCC_G_R', blank=True, null=True)  # Field name made lowercase.
    ewcc_g_fc = models.BigIntegerField(db_column='EWCC_G_FC', blank=True, null=True)  # Field name made lowercase.
    aci_n_r = models.BigIntegerField(db_column='ACI_N_R', blank=True, null=True)  # Field name made lowercase.
    aci_n_fc = models.BigIntegerField(db_column='ACI_N_FC', blank=True, null=True)  # Field name made lowercase.
    aca_n_r = models.BigIntegerField(db_column='ACA_N_R', blank=True, null=True)  # Field name made lowercase.
    aca_n_fc = models.BigIntegerField(db_column='ACA_N_FC', blank=True, null=True)  # Field name made lowercase.
    icc_n_r = models.BigIntegerField(db_column='ICC_N_R', blank=True, null=True)  # Field name made lowercase.
    icc_n_fc = models.BigIntegerField(db_column='ICC_N_FC', blank=True, null=True)  # Field name made lowercase.
    acc_n_r = models.BigIntegerField(db_column='ACC_N_R', blank=True, null=True)  # Field name made lowercase.
    acc_n_fc = models.BigIntegerField(db_column='ACC_N_FC', blank=True, null=True)  # Field name made lowercase.
    ewcc_n_r = models.BigIntegerField(db_column='EWCC_N_R', blank=True, null=True)  # Field name made lowercase.
    ewcc_n_fc = models.BigIntegerField(db_column='EWCC_N_FC', blank=True, null=True)  # Field name made lowercase.
    ew_n_r = models.BigIntegerField(db_column='EW_N_R', blank=True, null=True)  # Field name made lowercase.
    ew_n_fc = models.BigIntegerField(db_column='EW_N_FC', blank=True, null=True)  # Field name made lowercase.
    cvat_r = models.BigIntegerField(db_column='CVAT_R', blank=True, null=True)  # Field name made lowercase.
    cvat_fc = models.BigIntegerField(db_column='CVAT_FC', blank=True, null=True)  # Field name made lowercase.
    cpi_r = models.BigIntegerField(db_column='CPI_R', blank=True, null=True)  # Field name made lowercase.
    cpi_fc = models.BigIntegerField(db_column='CPI_FC', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_r = models.BigIntegerField(db_column='CCPI_A_R', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_fc = models.BigIntegerField(db_column='CCPI_A_FC', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_vat_r = models.BigIntegerField(db_column='CCPI_A_VAT_R', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_vat_fc = models.BigIntegerField(db_column='CCPI_A_VAT_FC', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_vat_ew_r = models.BigIntegerField(db_column='CCPI_A_VAT_EW_R', blank=True, null=True)  # Field name made lowercase.
    ccpi_a_vat_ew_fc = models.BigIntegerField(db_column='CCPI_A_VAT_EW_FC', blank=True, null=True)  # Field name made lowercase.
    cp_pp_r = models.BigIntegerField(db_column='CP_PP_R', blank=True, null=True)  # Field name made lowercase.
    cp_pp_fc = models.BigIntegerField(db_column='CP_PP_FC', blank=True, null=True)  # Field name made lowercase.
    pp_pp_r = models.BigIntegerField(db_column='PP_PP_R', blank=True, null=True)  # Field name made lowercase.
    pp_pp_fc = models.BigIntegerField(db_column='PP_PP_FC', blank=True, null=True)  # Field name made lowercase.
    r = models.BooleanField(db_column='R', blank=True, null=True)  # Field name made lowercase.
    m = models.BooleanField(db_column='M', blank=True, null=True)  # Field name made lowercase.
    typevalue = models.SmallIntegerField(db_column='TypeValue', blank=True, null=True)  # Field name made lowercase.

    def year(self):
        """
        Get the year for the financial invoice.
        """
        return self.dateid.year
    
    def month(self):
        """
        Get the month for the financial invoice.
        """
        return self.dateid.month
    
    def sendshamsidate(self):
        """
        Get the send shamsi date for the financial invoice.
        """
        return GregorianToShamsi(self.senddate) if self.senddate is not None else ''

    def confirmedInvoiceAmounts(self):
        """
        Get the confirmed invoice amounts for the financial invoice.
        """
        return (self.aci_g_r or 0) + (self.aca_g_r or 0) + (self.ew_g_r or 0)
 
    def sentInvoiceAmounts(self):
        """
        Get the sent invoice amounts for the financial invoice.
        """
        return (self.icc_g_r or 0) + (self.acc_g_r or 0) + (self.ewcc_g_r or 0)

    def allReceived(self):
        """
        Get the all received for the financial invoice.
        """
        a = ((self.ccpi_a_vat_ew_r or 0) - (self.cvat_r or 0))
        return a

    def confirmedAmount(self):
        """
        Get the confirmed amount for the financial invoice.
        """
        b = ((self.aci_n_r or 0) + (self.aca_n_r or 0) + (self.ew_n_r or 0)) 
        return b 

    def receivePercent(self):
        """
        Get the receive percent for the financial invoice.
        """
        a = ((self.ccpi_a_vat_ew_r or 0) - (self.cvat_r or 0))
        b = ((self.aci_n_r or 0) + (self.aca_n_r or 0) + (self.ew_n_r or 0)) 
        return 0 if b == 0 else (a / b) * 100

    def totalCumulativeReceiveAmount(self):
        """
        Get the total cumulative receive amount for the financial invoice.
        """
        financialInfos = FinancialInfo.objects.filter(contractid__exact=self.contractid, dateid__exact=self.dateid)
        financialInfo = financialInfos[0] if financialInfos and len(financialInfos) > 0 else None
        lastclaimbill = financialInfo.lastclaimbill_r if financialInfo else 0
        
        return (self.ccpi_a_vat_ew_r or 0) + (lastclaimbill or 0)
        
    def persianMonth(self):
        """
        Get the persian month for the financial invoice.
        """
        month = int(self.dateid.month)
        if(month < 7):
            if(month < 4):
                if(month == 1):
                    return 'فروردین'
                elif(month == 2):
                    return 'اردیبهشت'
                elif(month == 3):
                    return 'خرداد'
            else:
                if(month == 4):
                    return 'تیر'        
                elif(month == 5):
                    return 'مرداد'
                elif(month == 6):
                    return 'شهریور' 
        else:     
            if(month < 10):
                if(month == 7):
                    return 'مهر'        
                elif(month == 8):
                    return 'آبان'        
                elif(month == 9):
                    return 'آذر'
            else:
                if(month == 10):
                    return 'دی'        
                elif(month == 11):
                    return 'بهمن'        
                elif(month == 12):
                    return 'اسفند'
            

        return GregorianToShamsi(self.senddate) if self.senddate is not None else ''
    
    class Meta:
        db_table = 'tblw_InvoiceEx'

    
class MachineryManager(models.Manager):
    """
    Machinery manager for the projects application.
    """
    def get_queryset(self):
        """
        Get the queryset for the machinery.
        """
        result = (
            super().get_queryset().order_by("machinaryid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("machinaryid")]
                )
            )
            .values("machinaryid", "contractid", "dateid", "machine", "activeno", "inactiveno", "description", "row_number")
        )
        return result

        
class Machinary(models.Model):
    """
    Machinery model for the projects application.
    """
    machinaryid = models.AutoField(db_column='MachinaryID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_Machinery", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_Machinery", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    machine = models.CharField(db_column='Machine', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    activeno = models.IntegerField(db_column='ActiveNo', default=0)  # Field name made lowercase.
    inactiveno = models.IntegerField(db_column='InactiveNo', default=0)  # Field name made lowercase.
    priority = models.BooleanField(db_column='Priority', default=False, null=True)
    description = models.CharField(db_column='Description', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = MachineryManager()

    class Meta:
        db_table = 'tblw_Machinary'


class PmsprogressManager(models.Manager):
    """
    Pmsprogress manager for the projects application.
    """
    def get_queryset(self):
        """
        Get the queryset for the pmsprogress.
        """
        result = (
            super().get_queryset().order_by("pmsprogressid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("pmsprogressid")]
                )
            )
            .values("pmsprogressid", "contractid", "dateid", "item", "lastplanprogress", "lastplanvirtualprogress", "row_number")
        )
        return result


class PmsProgress(models.Model):
    """
    Pmsprogress model for the projects application.
    """
    pmsprogressid = models.AutoField(db_column='PMSProgressID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_Pmsprogress", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_Pmsprogress", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    lastplanprogress = models.IntegerField(db_column='LastPlanProgress', blank=True, null=True)  # Field name made lowercase.
    lastplanvirtualprogress = models.IntegerField(db_column='LastPlanVirtualProgress', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = PmsprogressManager()

    class Meta:
        db_table = 'tblw_PMSProgress'


class ProblemManager(models.Manager):
    """
    Problem manager for the projects application.
    """
    def get_queryset(self):
        """
        Get the queryset for the problem.
        """
        result = (
            # __contractid __dateid
            super().get_queryset().order_by("problemid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("problemid")]
                )
            )
            .values("problemid", "contractid", "dateid", "problem", "row_number")
        )
        return result


class Problem(models.Model):
    """
    Problem model for the projects application.
    """
    problemid = models.AutoField(db_column='ProblemID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_Problem", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_Problem", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    problem = models.CharField(db_column='Problem', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = ProblemManager()
    
    class Meta:
        db_table = 'tblw_Problem'


class ProgressStateManager(models.Manager):
    """
    Progress state manager for the projects application.
    """
    def get_queryset(self):
        """
        Get the queryset for the progress state.
        """
        result = (
            super().get_queryset().order_by("progressstateid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("progressstateid")]
                )
            )
            .values("progressstateid", "contractid", "dateid", "plan_replan", "pp_e", "ap_e", "pp_p", 
                    "ap_p", "pp_c", "ap_c", "pp_t", "ap_t", "pr_t", "pfc_t", "row_number")
        )
        return result


class ProgressState(models.Model):
    """
    Progress state model for the projects application.
    """
    progressstateid = models.AutoField(db_column='ProgressStateID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_ProgressState", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_ProgressState", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    plan_replan = models.CharField(db_column='Plan_Replan', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    pp_e = models.DecimalField(db_column='PP_E', max_digits=6, decimal_places=2)  # Field name made lowercase.
    ap_e = models.DecimalField(db_column='AP_E', max_digits=6, decimal_places=2)  # Field name made lowercase.
    pp_p = models.DecimalField(db_column='PP_P', max_digits=6, decimal_places=2)  # Field name made lowercase.
    ap_p = models.DecimalField(db_column='AP_P', max_digits=6, decimal_places=2)  # Field name made lowercase.
    pp_c = models.DecimalField(db_column='PP_C', max_digits=6, decimal_places=2)  # Field name made lowercase.
    ap_c = models.DecimalField(db_column='AP_C', max_digits=6, decimal_places=2)  # Field name made lowercase.
    pp_t = models.DecimalField(db_column='PP_T', max_digits=6, decimal_places=2)  # Field name made lowercase.
    ap_t = models.DecimalField(db_column='AP_T', max_digits=6, decimal_places=2)  # Field name made lowercase.
    pr_t = models.DecimalField(db_column='PR_T', max_digits=6, decimal_places=2)  # Field name made lowercase.
    pfc_t = models.DecimalField(db_column='PFC_T', max_digits=6, decimal_places=2)  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = ProgressStateManager()

    def year(self):
        """
        Get the year for the progress state.
        """
        return self.dateid.year
    
    def month(self):
        """
        Get the month for the progress state.
        """
        return self.dateid.month
    
    def persian6Month(self):
        """
        Get the persian 6 month for the progress state.
        """
        month = int(self.dateid.month)
        if(month < 7):
            if(month < 4):
                if(month == 1):
                    return 'فروردین'
                elif(month == 2):
                    return 'اردیبهشت'
                elif(month == 3):
                    return 'خرداد'
            else:
                if(month == 4):
                    return 'تیر'        
                elif(month == 5):
                    return 'مرداد'
                elif(month == 6):
                    return 'شهریور' 
        else:     
            if(month < 10):
                if(month == 7):
                    return 'مهر'        
                elif(month == 8):
                    return 'آبان'        
                elif(month == 9):
                    return 'آذر'
            else:
                if(month == 10):
                    return 'دی'        
                elif(month == 11):
                    return 'بهمن'        
                elif(month == 12):
                    return 'اسفند'
          
    def approximateProjectFinishShamsiDate(self):
        """
        Get the approximate project finish shamsi date for the progress state.
        """
        ece_date__max = TimeprogressState.objects.filter(
            contractid__exact=self.contractid).aggregate(Max('ece_date'))['ece_date__max']

        if ece_date__max is None:
            return ''
        else:
            return GregorianToShamsi(ece_date__max)
        
    class Meta:
        db_table = 'tblw_ProgressState'


class ProjectPersonalManager(models.Manager):
    """
    Project personal manager for the projects application.
    """
    def get_queryset(self):
        """
        Get the queryset for the project personal.
        """
        result = (
            super().get_queryset().order_by("projectpersonelid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("projectpersonelid")]
                )
            )
            .values("projectpersonelid", "contractid", "dateid", "dpno", "dcpno", "mepno", "description", "row_number")
        )
        return result


class ProjectPersonnel(models.Model):
    """
    Project personal model for the projects application.
    """
    projectpersonelid = models.AutoField(db_column='ProjectPersonelID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_ProjectPersonal", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate, related_name="ReportDate_ProjectPersonal", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.
    
    copmpno = models.IntegerField(db_column='CentralOfficeProjectManagerPersonalNo', default=0)
    coepno = models.IntegerField(db_column='CentralOfficeEngineeringPersonalNo', default=0)
    coppno = models.IntegerField(db_column='CentralOfficeProcurementPersonalNo', default=0)
    cocpno = models.IntegerField(db_column='CentralOfficeConstructionPersonalNo', default=0)
    wscpno = models.IntegerField(db_column='WorkshopConstructionPersonalNo', default=0)
    wscaopno = models.IntegerField(db_column='WorkshopContractorAdministrativeOfficePersonalNo', default=0)
    wsaopno = models.IntegerField(db_column='WorkshopAdministrativeOfficePersonalNo', default=0)
    
    dpno = models.IntegerField(db_column='DPNo')  # Field name made lowercase.
    dcpno = models.IntegerField(db_column='DCPNo')  # Field name made lowercase.
    mepno = models.IntegerField(db_column='MEPNo')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = ProjectPersonalManager()

    def year(self):
        """
        Get the year for the project personal.
        """
        return self.dateid.year
    
    def month(self):
        """
        Get the month for the project personal.
        """
        return self.dateid.month
    
    def persianMonth(self):
        """
        Get the persian month for the project personal.
        """
        month = int(self.dateid.month)
        if(month < 7):
            if(month < 4):
                if(month == 1):
                    return 'فروردین'
                elif(month == 2):
                    return 'اردیبهشت'
                elif(month == 3):
                    return 'خرداد'
            else:
                if(month == 4):
                    return 'تیر'        
                elif(month == 5):
                    return 'مرداد'
                elif(month == 6):
                    return 'شهریور' 
        else:     
            if(month < 10):
                if(month == 7):
                    return 'مهر'        
                elif(month == 8):
                    return 'آبان'        
                elif(month == 9):
                    return 'آذر'
            else:
                if(month == 10):
                    return 'دی'        
                elif(month == 11):
                    return 'بهمن'        
                elif(month == 12):
                    return 'اسفند'
                        
    def cotno(self):
        """
        Get the cotno for the project personal.
        """
        return ((self.copmpno or 0) + (self.coepno or 0) + (self.coppno or 0) + (self.cocpno or 0)) if self.dateid.dateid > 1126 else (self.dpno or 0) 

    def wstno(self):
        """
        Get the wstno for the project personal.
        """
        return ((self.wscpno or 0) + (self.wscaopno or 0) + (self.wsaopno or 0)) if self.dateid.dateid > 1126 else (self.mepno or 0) 

    class Meta:
        db_table = 'tblw_ProjectPersonel'


class TimeProgressStateManager(models.Manager):
    """
    Time progress state manager for the projects application.
    """
    def get_queryset(self):
        """
        Get the queryset for the time progress state.
        """
        result = (
            super().get_queryset().order_by("timeprogressstateid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("timeprogressstateid")]
                )
            )
            .values("timeprogressstateid", "contractid", "dateid", "plan_replan", "eep_date", 
                    "eee_date", "epp_date", "epe_date", "ecp_date", "ece_date", "epjp_date", "epje_date", "row_number")
        )
        return result


class TimeprogressState(models.Model):
    """
    Time progress state model for the projects application.
    """
    timeprogressstateid = models.AutoField(db_column='TimeProgressStateID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_TimeProgressState", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_TimeProgressState", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.    
    plan_replan = models.CharField(db_column='Plan_Replan', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    eep_date = models.DateField(db_column='EEP_Date', blank=True, null=True)  # Field name made lowercase.
    eee_date = models.DateField(db_column='EEE_Date', blank=True, null=True)  # Field name made lowercase.
    epp_date = models.DateField(db_column='EPP_Date', blank=True, null=True)  # Field name made lowercase.
    epe_date = models.DateField(db_column='EPE_Date', blank=True, null=True)  # Field name made lowercase.
    ecp_date = models.DateField(db_column='ECP_Date', blank=True, null=True)  # Field name made lowercase.
    ece_date = models.DateField(db_column='ECE_Date', blank=True, null=True)  # Field name made lowercase.
    epjp_date = models.DateField(db_column='EPjP_Date', blank=True, null=True)  # Field name made lowercase.
    epje_date = models.DateField(db_column='EPjE_Date', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = TimeProgressStateManager()
    
    def AsfaltTous_E(self):
        """
        Get the AsfaltTous_E for the time progress state.
        """
        objects = EpcCorporation.objects.filter(contractid=self.contractid, companyid=7)
        return True if len(objects) > 0 and objects[0].e_percent > 0 else False
    
    def AsfaltTous_P(self):
        """
        Get the AsfaltTous_P for the time progress state.
        """
        objects = EpcCorporation.objects.filter(contractid=self.contractid, companyid=7)
        return True if len(objects) > 0 and objects[0].p_percent > 0 else False
    
    def AsfaltTous_C(self):
        """
        Get the AsfaltTous_C for the time progress state.
        """
        objects = EpcCorporation.objects.filter(contractid=self.contractid, companyid=7)
        return True if len(objects) > 0 and objects[0].c_percent > 0 else False
    
    def year(self):
        """
        Get the year for the time progress state.
        """
        return self.dateid.year 
        # if self.dateid and self.dateid.year else ''
    
    def month(self):
        """
        Get the month for the time progress state.
        """
        return self.dateid.month if self.dateid and self.dateid.month else ''
    
    def eep_shamsiDate(self):
        """
        Get the eep_shamsiDate for the time progress state.
        """
        return GregorianToShamsi(self.eep_date) if self.eep_date is not None else ''           

    def eee_shamsiDate(self):
        """
        Get the eee_shamsiDate for the time progress state.
        """
        return GregorianToShamsi(self.eee_date) if self.eee_date is not None else ''           

    def epp_shamsiDate(self):
        """
        Get the epp_shamsiDate for the time progress state.
        """
        return GregorianToShamsi(self.epp_date) if self.epp_date is not None else ''           

    def epe_shamsiDate(self):
        """
        Get the epe_shamsiDate for the time progress state.
        """
        return GregorianToShamsi(self.epe_date) if self.epe_date is not None else ''           

    def ecp_shamsiDate(self):
        """
        Get the ecp_shamsiDate for the time progress state.
        """
        return GregorianToShamsi(self.ecp_date) if self.ecp_date is not None else ''           

    def ece_shamsiDate(self):
        """
        Get the ece_shamsiDate for the time progress state.
        """
        return GregorianToShamsi(self.ece_date) if self.ece_date is not None else ''           

    def epjp_shamsiDate(self):
        """
        Get the epjp_shamsiDate for the time progress state.
        """
        return GregorianToShamsi(self.epjp_date) if self.epjp_date is not None else ''           

    def epje_shamsiDate(self):
        """
        Get the epje_shamsiDate for the time progress state.
        """
        return GregorianToShamsi(self.epje_date) if self.epje_date is not None else ''           

    class Meta:
        db_table = 'tblw_TimeProgressState'


class WorkvolumeManager(models.Manager):    
    """
    Workvolume manager for the projects application.
    """
    def get_queryset(self):
        """
        Get the queryset for the workvolume.
        """
        result = (
            super().get_queryset().order_by("workvolumeid", "contractid", "dateid")
            .annotate(
                row_number=Window(
                    expression=RowNumber(), partition_by=[F("contractid")], order_by=[F("workvolumeid")]
                )
            )
            .values("workvolumeid", "contractid", "dateid", "work", "planestimate", "totalestimate", "executedsofar", "row_number")
        )
        return result


class WorkVolume(models.Model):
    """
    Workvolume model for the projects application.
    """
    workvolumeid = models.AutoField(db_column='WorkVolumeID', primary_key=True)  # Field name made lowercase.
    contractid = models.ForeignKey(Contract, related_name="Contract_WorkVolume", 
                                   on_delete=models.PROTECT, db_column='ContractID')  # Field name made lowercase.
    dateid = models.ForeignKey(ReportDate,  related_name="ReportDate_WorkVolume", 
                                   on_delete=models.PROTECT, db_column='DateID')  # Field name made lowercase.    
    work = models.CharField(db_column='Work', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    planestimate = models.IntegerField(db_column='PlanEstimate', blank=True, null=True)  # Field name made lowercase.
    totalestimate = models.IntegerField(db_column='TotalEstimate', blank=True, null=True)  # Field name made lowercase.
    executedsofar = models.IntegerField(db_column='ExecutedSoFar', blank=True, null=True)  # Field name made lowercase.

    objects = models.Manager()
    row_number_objects = WorkvolumeManager()
    
    class Meta:
        db_table = 'tblw_WorkVolume'

