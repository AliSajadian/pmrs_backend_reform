from rest_framework import serializers

from contracts.models import EpcCorporation
from projects.models import *


#=========== Contract Serializers ============
class ReportDateSerializerEx(serializers.ModelSerializer):
    shamsiDate = serializers.ReadOnlyField()
    class Meta:
        model = ReportDate
        fields = ('dateid', 'year', 'month', 'shamsiDate')
        

class ReportConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportConfirm
        fields = '__all__'  

class ReportsConfirmedSerializer(serializers.ModelSerializer):
    userconfirmshamsidate = serializers.ReadOnlyField()
    pmconfirmshamsidate = serializers.ReadOnlyField()
    userconfirmer = serializers.ReadOnlyField() 
    
    class Meta:
        model = ReportConfirm
        fields = ("userconfirmer", "type", "user_c", "pm_c", "userconfirmshamsidate", "pmconfirmshamsidate") 

        
class SystemAdministratorReportConfirmSerializer(serializers.ModelSerializer):
    saconfirmshamsidate = serializers.ReadOnlyField()
    userconfirmer = serializers.ReadOnlyField() 

    class Meta:
        model = ReportConfirm
        fields = ("userconfirmer", "sa_c", "saconfirmshamsidate")
        
class ProjectManagerReportConfirmSerializer(serializers.ModelSerializer):
    pmconfirmshamsidate = serializers.ReadOnlyField()
    userconfirmer = serializers.ReadOnlyField() 

    class Meta:
        model = ReportConfirm
        fields = ("userconfirmer", "pm_c", "pmconfirmshamsidate") 
        
class CoordinatorReportConfirmSerializer(serializers.ModelSerializer):
    userconfirmshamsidate = serializers.ReadOnlyField()
    userconfirmer = serializers.ReadOnlyField() 
    
    class Meta:
        model = ReportConfirm
        fields = ("userconfirmer", "user_c", "userconfirmshamsidate") 

                
class FinancialInfoSerializer(serializers.ModelSerializer):
    # isconfirmed = serializers.ReadOnlyField()
    # confirmdate = serializers.ReadOnlyField()

    class Meta:
        model = FinancialInfo
        fields = '__all__'
        # fields = ("hseid", "contractid", "dateid", "totaloperationdays", "withouteventdays", "deathno", "lastverifiedinvoice_r", 
        #           "lastverifiedinvoice_fc", "lvi_no", "lastclaimedadjustmentinvoice_r", "lastclaimedadjustmentinvoice_fc", "lcai_no", 
        #           "lastverifiedadjustmentinvoice_r", "lastverifiedadjustmentinvoice_fc", "lvai_no", "lastclaimedextraworkinvoice_r", 
        #           "lastclaimedextraworkinvoice_fc", "lcewi_no", "lastverifiedextraworkinvoice_r", "lastverifiedextraworkinvoice_fc", 
        #           "lvewi_no", "lastclaimbill_r", "lastclaimbill_fc", "lcb_no", "lastclaimbillverified_r", "lastclaimbillverified_fc", 
        #           "lcbv_no", "lastclaimbillrecievedamount_r", "lastclaimbillrecievedamount_fc", "cumulativeclientpayment_r", 
        #           "cumulativeclientpayment_fc", "clientprepaymentdeferment_r", "clientprepaymentdeferment_fc", "estcost_r", "estcost_fc", 
        #           "estclientpayment_r", "estclientpayment_fc", "estdebitcredit_r", "estdebitcredit_fc", "isconfirmed", "confirmdate")

class FinancialInfoReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialInfo
        fields = ("estdebitcredit_r", "estcost_r", "estclientpayment_r")


class HseSerializer(serializers.ModelSerializer):
    # isconfirmed = serializers.ReadOnlyField()
    # confirmdate = serializers.ReadOnlyField()

    class Meta:
        model = Hse
        fields = '__all__'
        # fields = ("financialinfoid", "contractid", "dateid", "", "lastclaimedinvoice_r", "lastclaimedinvoice_fc", 
        #           "lci_no", "woundno", "disadvantageeventno", "isconfirmed", "confirmdate")
         
class HseReportSerializer(serializers.ModelSerializer):
    totaldeathno = serializers.ReadOnlyField()
    totalwoundno = serializers.ReadOnlyField()
    totaldisadvantageeventno = serializers.ReadOnlyField()
    
    class Meta:
        model = Hse
        fields = ('totaldeathno', 'totalwoundno', 'totaldisadvantageeventno', 'withouteventdays','totaloperationdays')

         
class ProgressStateSerializer(serializers.ModelSerializer):
    # row_number = serializers.ReadOnlyField() , "row_number"
    year = serializers.ReadOnlyField()
    month = serializers.ReadOnlyField()
    
    # def validate(self, data):
    #     pp_e = data['pp_e']
    #     ap_e = data['ap_e']
    #     pp_p = data['pp_p']
    #     ap_p = data['ap_p']
    #     pp_c = data['pp_c']
    #     ap_c = data['ap_c']
    #     pp_t = data['pp_t']
    #     ap_t = data['ap_t']
    #     pr_t = data['pr_t']
    #     pfc_t = data['pfc_t']

    #     if pp_e and int(pp_e) < 0:
    #         raise serializers.ValidationError('پیشرفت برنامه ای بخش مهندسی منفی نمی شود')
    #     elif ap_e and int(ap_e) < 0:
    #         raise serializers.ValidationError('پیشرفت واقعی بخش مهندسی منفی نمی شود')
    #     elif pp_p and int(pp_p) < 0:
    #         raise serializers.ValidationError('پیشرفت برنامه ای بخش تدارک منفی نمی شود')
    #     elif ap_p and int(ap_p) < 0:
    #         raise serializers.ValidationError('پیشرفت واقعی بخش تدارک منفی نمی شود')
    #     elif pp_c and int(pp_c) < 0:
    #         raise serializers.ValidationError('پیشرفت برنامه ای بخش اجرا منفی نمی شود')
    #     elif ap_c and int(ap_c) < 0:
    #         raise serializers.ValidationError('پیشرفت واقعی بخش اجرا منفی نمی شود')
    #     elif pp_t and int(pp_t) < 0:
    #         raise serializers.ValidationError('پیشرفت برنامه ای کل پروژه منفی نمی شود')
    #     elif ap_t and int(ap_t) < 0:
    #         raise serializers.ValidationError('پیشرفت واقعی کل پروژه منفی نمی شود')        
    #     elif pr_t and int(pr_t) < 0:
    #         raise serializers.ValidationError('پیشرفت ریالی منفی نمی شود')
    #     elif pfc_t and int(pfc_t) < 0:
    #         raise serializers.ValidationError('پیشرفت ارزی منفی نمی شود')        
    #     return data

    class Meta:
        model = ProgressState
        fields = ("progressstateid", "contractid", "dateid", "plan_replan", "pp_e", "ap_e", "pp_p", "ap_p", 
                  "pp_c", "ap_c", "pp_t", "ap_t", "pr_t", "pfc_t", "year", "month")         

class ProgressStateReportSerializer(serializers.ModelSerializer):
    persian6Month = serializers.ReadOnlyField()

    class Meta:
        model = ProgressState
        fields = ("pp_e", "ap_e", "pp_p", "ap_p", "pp_c", "ap_c", "pp_t", "ap_t", "pr_t", "pfc_t", "persian6Month")
                        
class TimeProgressStateSerializer(serializers.ModelSerializer):
    year = serializers.ReadOnlyField()
    month = serializers.ReadOnlyField()
    eep_shamsiDate = serializers.ReadOnlyField()
    eee_shamsiDate = serializers.ReadOnlyField()
    epp_shamsiDate = serializers.ReadOnlyField()
    epe_shamsiDate = serializers.ReadOnlyField()
    ecp_shamsiDate = serializers.ReadOnlyField()
    ece_shamsiDate = serializers.ReadOnlyField()
    epjp_shamsiDate = serializers.ReadOnlyField()
    epje_shamsiDate = serializers.ReadOnlyField()
    
    AsfaltTous_E = serializers.ReadOnlyField()
    AsfaltTous_P = serializers.ReadOnlyField()
    AsfaltTous_C = serializers.ReadOnlyField()
    
    class Meta:
        model = TimeprogressState
        fields = ("timeprogressstateid", "contractid", "dateid", "plan_replan", "eep_date", "eee_date", 
                    "epp_date", "epe_date", "ecp_date", "ece_date", "epjp_date", "epje_date", "year", "month",
                    "eep_shamsiDate", "eee_shamsiDate", "epp_shamsiDate", "epe_shamsiDate", "ecp_shamsiDate", 
                    "ece_shamsiDate", "epjp_shamsiDate", "epje_shamsiDate", "AsfaltTous_E", "AsfaltTous_P", 
                    "AsfaltTous_C")


class InvoiceSerializer(serializers.ModelSerializer):
    # sendshamsidate = serializers.ReadOnlyField() 
    year = serializers.ReadOnlyField()
    month = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = ("invoiceid", "contractid", "dateid", "year", "month", "aci_g_r", "aci_g_fc", "aca_g_r", 
                  "aca_g_fc", "ew_g_r", "ew_g_fc", "icc_g_r", "icc_g_fc", "acc_g_r", "acc_g_fc", "ewcc_g_r", "ewcc_g_fc", 
                  "aci_n_r", "aci_n_fc", "aca_n_r", "aca_n_fc", "ew_n_r", "ew_n_fc", "icc_n_r", "icc_n_fc", 
                  "acc_n_r", "acc_n_fc", "ewcc_n_r", "ewcc_n_fc", "cvat_r", "cvat_fc", "cpi_r", "cpi_fc", 
                  "ccpi_a_r", "ccpi_a_fc", "ccpi_a_vat_r", "ccpi_a_vat_fc", "ccpi_a_vat_ew_r", "ccpi_a_vat_ew_fc", 
                  "cp_pp_r", "cp_pp_fc", "pp_pp_r", "pp_pp_fc", "r", "m", "description")

class InvoiceReport1Serializer(serializers.ModelSerializer):
    confirmedInvoiceAmounts = serializers.ReadOnlyField()
    sentInvoiceAmounts = serializers.ReadOnlyField()
    receivePercent = serializers.ReadOnlyField()
    allReceived = serializers.ReadOnlyField()
    confirmedAmount = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = ("allReceived", "cp_pp_r", "confirmedAmount", "pp_pp_r", "cvat_r", 
                  "confirmedInvoiceAmounts", "sentInvoiceAmounts", "aci_g_r", "icc_g_r", "aca_g_r", "acc_g_r", "ew_g_r", "ewcc_g_r",
                  "receivePercent")

class InvoiceReport2Serializer(serializers.ModelSerializer):
    confirmedAmount = serializers.ReadOnlyField()
    totalCumulativeReceiveAmount = serializers.ReadOnlyField()
    persianMonth = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = ("confirmedAmount", "persianMonth", "totalCumulativeReceiveAmount")


class FinancialInvoiceSerializer(serializers.ModelSerializer):
    year = serializers.ReadOnlyField()
    month = serializers.ReadOnlyField()

    class Meta:
        model = FinancialInvoice
        fields = ("invoiceid", "contractid", "dateid", "year", "month", "invoicetype", "alino", "almino", 
                   "aci_g_r", "aci_g_fc", "aca_g_r", "aca_g_fc", "ew_g_r", "ew_g_fc", "icc_g_r", "icc_g_fc", "acc_g_r", 
                   "acc_g_fc", "ewcc_g_r", "ewcc_g_fc", "aci_n_r", "aci_n_fc", "aca_n_r", "aca_n_fc", "ew_n_r", 
                   "ew_n_fc", "icc_n_r", "icc_n_fc", "acc_n_r", "acc_n_fc", "ewcc_n_r", "ewcc_n_fc", "cvat_r", 
                   "cvat_fc", "cpi_r", "cpi_fc", "ccpi_a_r", "ccpi_a_fc", "ccpi_a_vat_r", "ccpi_a_vat_fc", "ccpi_a_vat_ew_r", 
                   "ccpi_a_vat_ew_fc", "cp_pp_r", "cp_pp_fc", "pp_pp_r", "pp_pp_fc", "r", "m", "typevalue")

class FinancialInvoiceReportSerializer(serializers.ModelSerializer):
    financialDepartmentConfirmedAmount = serializers.IntegerField()
    persianMonth = serializers.ReadOnlyField()
    
    class Meta:
        model = FinancialInvoice
        fields = ("financialDepartmentConfirmedAmount", "persianMonth")


class WorkvolumeSerializer(serializers.ModelSerializer):
    # row_number = serializers.ReadOnlyField() , "row_number"

    class Meta:
        model = WorkVolume
        fields = ("workvolumeid", "contractid", "dateid", "work", "planestimate", 
                  "totalestimate", "executedsofar")

    
class PmsprogressSerializer(serializers.ModelSerializer):
    # row_number = serializers.ReadOnlyField() , "row_number"

    class Meta:
        model = PmsProgress
        fields = ("pmsprogressid", "contractid", "dateid", "item", "lastplanprogress", 
                  "lastplanvirtualprogress")


class BudgetCostSerializer(serializers.ModelSerializer):
    # row_number = serializers.ReadOnlyField() , "row_number"
    year = serializers.ReadOnlyField()
    month = serializers.ReadOnlyField()
    isConfirmed = serializers.ReadOnlyField()

    class Meta:
        model = Budgetcost
        fields = ("budgetcostid", "contractid", "dateid", "bac_r", "bac_fc", "eac_r", "eac_fc", "ev_r", 
                  "ev_fc", "ac_r", "ac_fc", "description", "year", "month", "isConfirmed")

class BudgetCostReportSerializer(serializers.ModelSerializer):
    persianMonth = serializers.ReadOnlyField()
    class Meta:
        model = Budgetcost
        fields = ("contractid", "dateid", "bac_r", "bac_fc", "eac_r", "eac_fc", "description", "persianMonth")


class MachinerySerializer(serializers.ModelSerializer):
    # row_number = serializers.ReadOnlyField() , "row_number"

    class Meta:
        model = Machinary
        fields = ("machinaryid", "contractid", "dateid", "machine", "activeno", 
                  "inactiveno", "priority", "description")


class ProjectPersonalSerializer(serializers.ModelSerializer):
    # cotno = serializers.ReadOnlyField()
    # wstno = serializers.ReadOnlyField()
    year = serializers.ReadOnlyField()
    month = serializers.ReadOnlyField()

    # row_number = serializers.ReadOnlyField() , "row_number"
    class Meta:
        model = ProjectPersonnel
        fields = ("projectpersonelid", "contractid", "dateid", "copmpno", "coepno", "coppno", 
                  "cocpno", "wscpno", "wscaopno", "wsaopno", "dpno", "mepno", "description", "year", "month")

class ProjectPersonalReportSerializer(serializers.ModelSerializer):
    persianMonth = serializers.ReadOnlyField()

    class Meta:
        model = ProjectPersonnel
        fields = ("dpno", "dcpno", "mepno", "persianMonth")


class ProblemSerializer(serializers.ModelSerializer):
    # row_number = serializers.ReadOnlyField() , "row_number"

    class Meta:
        model = Problem
        fields = ("problemid", "contractid", "dateid", "problem")


class CriticalActionSerializer(serializers.ModelSerializer):
    # row_number = serializers.ReadOnlyField() , "row_number"
    
    class Meta:
        model = CriticalAction
        fields = ("criticalactionid", "contractid", "dateid", "criticalaction")
