"""
Service layer for the projects application.
Contains all business logic separated from API views.
"""
from django.db.models import Max, Q, Sum
from django.contrib.auth import get_user_model
from datetime import datetime

from contracts.models import Contract
from contracts.utils import gregorian_to_shamsi
from projects_files.utils import set_report_visit
from projects.models import (
    ReportDate, ReportConfirm, FinancialInfo, Hse, ProgressState,
    TimeprogressState, Invoice, FinancialInvoice, WorkVolume, 
    PmsProgress, Budgetcost, Problem, CriticalAction, 
    ContractReportDate, Machinary, ProjectPersonnel
)


class ReportDateService:
    """Service for managing report dates."""
    
    @staticmethod
    def get_and_create_report_dates():
        """
        Get report dates and create new ones if needed for each Persian month.
        Automatically creates records for months that are missing up to the last month.
        """
        max_date_id = ReportDate.objects.aggregate(Max('dateid'))['dateid__max']
        date = ReportDate.objects.get(pk=max_date_id)
        y1 = int(date.year)
        m1 = int(date.month)

        now = gregorian_to_shamsi(datetime.now())
        y2 = int(now[0:4])
        m2 = int(now[5:now.find('-', 5)])
        
        # Calculate last month
        if m2 > 1:
            m2 = m2 - 1
        else:
            m2 = 12
            y2 = y2 - 1
        
        # Determine if we need to create new records
        loop = 0
        if ((y2 - y1) > 1 or 
            ((y2 - y1) == 0 and (m2 - m1) > 0) or 
            ((y2 - y1) == 1 and (12 - m1 + m2 > 0))):
            loop = 1
        
        # Create missing report dates
        while loop == 1:
            if y2 == y1:
                m1 = m1 + 1
                date = ReportDate.objects.create(year=str(y1), month=str(m1))
                ReportDateService._create_contract_report_dates(date, y2, m2)
                
                if m2 == m1:
                    loop = 0
                    
            elif y2 - y1 > 0:
                m1 = m1 + 1
                if m1 > 12:
                    m1 = 1
                    y1 = y1 + 1
                
                date = ReportDate.objects.create(year=str(y1), month=str(m1))
                ReportDateService._create_contract_report_dates(date, y2, m2)
                
                if y2 == y1 and m2 == m1:
                    loop = 0
                            
        return ReportDate.objects.all().order_by('-dateid')
    
    @staticmethod
    def _create_contract_report_dates(date, y2, m2):
        """Create ContractReportDate entries for all active contracts."""
        contracts = Contract.objects.exclude(
            contract__exact='test'
        ).filter(iscompleted__exact=False)
        
        for contract in contracts:
            flag = ContractReportDate.objects.filter(
                contractid__exact=contract.contractid,
                dateid__year__exact=y2,
                dateid__month__exact=m2
            ).count()
            
            if flag == 0:
                ContractReportDate.objects.create(
                    contractid=contract, 
                    dateid=date
                )


class ReportConfirmService:
    """Service for managing report confirmations."""
    
    @staticmethod
    def get_confirmed_reports(contract_id, date_id):
        """Get all confirmed reports for a contract and date."""
        return ReportConfirm.objects.filter(
            Q(contractid__exact=contract_id, dateid__exact=date_id, user_c__gt=0) | 
            Q(contractid__exact=contract_id, dateid__exact=date_id, pm_c__gt=0)
        )
    
    @staticmethod
    def is_project_manager_confirmed(contract_id, date_id):
        """Check if project manager has confirmed the report."""
        objects = ReportConfirm.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id, 
            pm_c__gt=0
        )
        return objects[0] if objects.exists() else None
    
    @staticmethod
    def project_manager_confirm(contract_id, date_id, confirmed):
        """
        Confirm report by project manager.
        Returns updated confirmed reports or error code.
        """
        objects = ReportConfirm.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
        
        if objects.exists() and len(objects) == 15:
            for obj in objects:
                obj.pm_c = confirmed
                obj.pmconfirmdate = datetime.now()
                obj.save()
            
            return ReportConfirmService.get_confirmed_reports(contract_id, date_id)
        else:
            return None
    
    @staticmethod
    def is_coordinator_confirmed(contract_id, date_id, report_type):
        """Check if coordinator has confirmed the report."""
        objects = ReportConfirm.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id, 
            type__exact=report_type
        )
        return objects[0] if objects.exists() else None
    
    @staticmethod
    def coordinator_confirm(contract_id, date_id, user_id, confirmed, report_type):
        """Confirm report by coordinator."""
        objects = ReportConfirm.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id, 
            type__exact=report_type
        )
        obj = objects[0] if objects.exists() else None

        if obj is not None:
            obj.user_c = confirmed
            obj.userid = user_id
            obj.userconfirmdate = datetime.now()
            obj.save()
        else:
            contract = Contract.objects.get(pk=contract_id)
            date = ReportDate.objects.get(pk=date_id)
            user = get_user_model().objects.get(pk=user_id)
            ReportConfirm.objects.create(
                contractid=contract, 
                dateid=date, 
                userid=user,
                type=report_type, 
                user_c=confirmed, 
                userconfirmdate=datetime.now()
            )
        
        return ReportConfirmService.get_confirmed_reports(contract_id, date_id)


class FinancialInfoService:
    """Service for managing financial information."""
    
    @staticmethod
    def get_or_create_financial_info(user_id, contract_id, date_id, report_id):
        """Get or create financial info for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        exists = FinancialInfo.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).exists()

        if not exists:
            contract = Contract.objects.get(pk=contract_id)
            date = ReportDate.objects.get(pk=date_id)
            FinancialInfo.objects.update_or_create(
                contractid=contract,
                dateid=date
            )
        
        financial_infos = FinancialInfo.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
        return financial_infos.first()
    
    @staticmethod
    def get_financial_info_for_report(contract_id, date_id):
        """Get financial info for report."""
        financial_infos = FinancialInfo.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
        return financial_infos.first()
    
    @staticmethod
    def update_financial_info(financial_info_id, data):
        """Update financial info with provided data."""
        financial_info = FinancialInfo.objects.get(
            financialinfoid__exact=financial_info_id
        )
        
        # Update all financial info fields
        fields_to_update = [
            'lastclaimedinvoice_r', 'lastclaimedinvoice_fc', 'lci_no',
            'lastverifiedinvoice_r', 'lastverifiedinvoice_fc', 'lvi_no',
            'lastclaimedadjustmentinvoice_r', 'lastclaimedadjustmentinvoice_fc', 'lcai_no',
            'lastverifiedadjustmentinvoice_r', 'lastverifiedadjustmentinvoice_fc', 'lvai_no',
            'lastclaimedextraworkinvoice_r', 'lastclaimedextraworkinvoice_fc', 'lcewi_no',
            'lastverifiedextraworkinvoice_r', 'lastverifiedextraworkinvoice_fc', 'lvewi_no',
            'lastclaimbill_r', 'lastclaimbill_fc', 'lcb_no',
            'lastclaimbillverified_r', 'lastclaimbillverified_fc', 'lcbv_no',
            'lastclaimbillrecievedamount_r', 'lastclaimbillrecievedamount_fc',
            'cumulativeclientpayment_r', 'cumulativeclientpayment_fc',
            'clientprepaymentdeferment_r', 'clientprepaymentdeferment_fc',
            'estcost_r', 'estcost_fc',
            'estclientpayment_r', 'estclientpayment_fc',
            'estdebitcredit_r', 'estdebitcredit_fc'
        ]
        
        for field in fields_to_update:
            setattr(financial_info, field, data.get(field, 0))
        
        financial_info.save()
        
        # Update related invoices
        FinancialInfoService._update_related_invoices(
            data['contractid'], 
            data['dateid'], 
            data
        )
        
        return FinancialInfo.objects.filter(
            contractid__exact=data['contractid'], 
            dateid__exact=data['dateid']
        ).first()
    
    @staticmethod
    def _update_related_invoices(contract_id, date_id, data):
        """Update related invoice records."""
        invoice_r = Invoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id, 
            r__exact=True
        ).first()
        
        if invoice_r:
            invoice_r.aci_n_r = data.get('lastverifiedinvoice_r', 0)
            invoice_r.aca_n_r = data.get('lastverifiedadjustmentinvoice_r', 0)
            invoice_r.ew_n_r = data.get('lastverifiedextraworkinvoice_r', 0)
            invoice_r.icc_n_r = data.get('lastclaimedinvoice_r', 0)
            invoice_r.acc_n_r = data.get('lastclaimedadjustmentinvoice_r', 0)
            invoice_r.ewcc_n_r = data.get('lastclaimedextraworkinvoice_r', 0)
            invoice_r.save()
        
        invoice_fc = Invoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id, 
            r__exact=False
        ).first()
        
        if invoice_fc:
            invoice_fc.aci_n_fc = data.get('lastverifiedinvoice_fc', 0)
            invoice_fc.aca_n_fc = data.get('lastverifiedadjustmentinvoice_fc', 0)
            invoice_fc.ew_n_fc = data.get('lastverifiedextraworkinvoice_fc', 0)
            invoice_fc.icc_n_fc = data.get('lastclaimedinvoice_fc', 0)
            invoice_fc.acc_n_fc = data.get('lastclaimedadjustmentinvoice_fc', 0)
            invoice_fc.ewcc_n_fc = data.get('lastclaimedextraworkinvoice_fc', 0)
            invoice_fc.save()


class HseService:
    """Service for managing HSE (Health, Safety, Environment) data."""
    
    @staticmethod
    def get_or_create_hse(user_id, contract_id, date_id, report_id):
        """Get or create HSE data for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        exists = Hse.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).exists()

        if not exists:
            contract = Contract.objects.get(pk=contract_id)
            date = ReportDate.objects.get(pk=date_id)
            Hse.objects.update_or_create(
                contractid=contract,
                dateid=date,
                totaloperationdays=0,
                withouteventdays=0,
                deathno=0,
                woundno=0,
                disadvantageeventno=0
            )
        
        hses = Hse.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
        return hses.first()
    
    @staticmethod
    def get_hse_for_report(contract_id, date_id):
        """Get HSE data for report."""
        hses = Hse.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
        return hses.first()


class ProgressStateService:
    """Service for managing progress state data."""
    
    @staticmethod
    def get_or_create_progress_state(user_id, contract_id, date_id, report_id):
        """Get or create progress state for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        exists = ProgressState.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).exists()

        if not exists:
            contract = Contract.objects.get(pk=contract_id)
            date = ReportDate.objects.get(pk=date_id)
            ProgressState.objects.update_or_create(
                contractid=contract,
                dateid=date,
                defaults={
                    'plan_replan': '00',
                    'pp_e': 0, 'ap_e': 0,
                    'pp_p': 0, 'ap_p': 0,
                    'pp_c': 0, 'ap_c': 0,
                    'pp_t': 0, 'ap_t': 0,
                    'pr_t': 0, 'pfc_t': 0
                }
            )
        
        return ProgressState.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('dateid')
    
    @staticmethod
    def get_progress_state_for_report(contract_id, date_id):
        """Get progress state for report (last 6 records)."""
        return ProgressState.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('-dateid')[:6][::-1]


class TimeProgressStateService:
    """Service for managing time progress state data."""
    
    @staticmethod
    def get_or_create_time_progress_state(user_id, contract_id, date_id, report_id):
        """Get or create time progress state for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        exists = TimeprogressState.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).exists()

        if not exists:
            contract = Contract.objects.get(pk=contract_id)
            date = ReportDate.objects.get(pk=date_id)
            TimeprogressState.objects.update_or_create(
                contractid=contract,
                dateid=date,
                defaults={'plan_replan': '00'}
            )
        
        return TimeprogressState.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('dateid')


class InvoiceService:
    """Service for managing invoice data."""
    
    @staticmethod
    def get_or_create_invoices(user_id, contract_id, date_id, report_id):
        """Get or create invoices for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        exists = Invoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).exists()

        if not exists:
            contract = Contract.objects.get(pk=contract_id)
            date = ReportDate.objects.get(pk=date_id)
            financial_infos = FinancialInfo.objects.filter(
                contractid__exact=contract_id, 
                dateid__exact=date_id
            )
            
            InvoiceService._create_rials_invoice(
                contract, date, financial_infos.first() if financial_infos.exists() else None
            )
            InvoiceService._create_foreign_currency_invoice(
                contract, date, financial_infos.first() if financial_infos.exists() else None
            )
        
        return Invoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('dateid')
    
    @staticmethod
    def _create_rials_invoice(contract, date, financial_info):
        """Create invoice in Rials."""
        defaults = {
            'senddate': datetime.now(),
            'aci_g_r': 0,
            'aci_n_r': financial_info.lastverifiedinvoice_r if financial_info else 0,
            'aci_g_fc': None, 'aci_n_fc': None,
            'aca_g_r': 0,
            'aca_n_r': financial_info.lastverifiedadjustmentinvoice_r if financial_info else 0,
            'aca_g_fc': None, 'aca_n_fc': None,
            'ew_g_r': 0,
            'ew_n_r': financial_info.lastverifiedextraworkinvoice_r if financial_info else 0,
            'ew_g_fc': None, 'ew_n_fc': None,
            'icc_g_r': 0,
            'icc_n_r': financial_info.lastclaimedinvoice_r if financial_info else 0,
            'icc_g_fc': None, 'icc_n_fc': None,
            'acc_g_r': 0,
            'acc_n_r': financial_info.lastclaimedadjustmentinvoice_r if financial_info else 0,
            'acc_g_fc': None, 'acc_n_fc': None,
            'ewcc_g_r': 0,
            'ewcc_n_r': financial_info.lastclaimedextraworkinvoice_r if financial_info else 0,
            'ewcc_g_fc': None, 'ewcc_n_fc': None,
            'cvat_r': 0, 'cvat_fc': None,
            'cpi_r': 0, 'cpi_fc': None,
            'ccpi_a_r': 0, 'ccpi_a_fc': None,
            'ccpi_a_vat_r': 0, 'ccpi_a_vat_fc': None,
            'ccpi_a_vat_ew_r': 0, 'ccpi_a_vat_ew_fc': None,
            'cp_pp_r': 0, 'cp_pp_fc': None,
            'pp_pp_r': 0, 'pp_pp_fc': None,
            'm': False, 'description': None
        }
        Invoice.objects.update_or_create(
            contractid=contract,
            dateid=date,
            r=True,
            defaults=defaults
        )
    
    @staticmethod
    def _create_foreign_currency_invoice(contract, date, financial_info):
        """Create invoice in Foreign Currency."""
        defaults = {
            'senddate': datetime.now(),
            'aci_g_fc': 0,
            'aci_n_fc': financial_info.lastverifiedinvoice_fc if financial_info else 0,
            'aci_g_r': None, 'aci_n_r': None,
            'aca_g_fc': 0,
            'aca_n_fc': financial_info.lastverifiedadjustmentinvoice_fc if financial_info else 0,
            'aca_g_r': None, 'aca_n_r': None,
            'ew_g_fc': 0,
            'ew_n_fc': financial_info.lastverifiedextraworkinvoice_fc if financial_info else 0,
            'ew_g_r': None, 'ew_n_r': None,
            'icc_g_fc': 0,
            'icc_n_fc': financial_info.lastclaimedinvoice_fc if financial_info else 0,
            'icc_g_r': None, 'icc_n_r': None,
            'acc_g_fc': 0,
            'acc_n_fc': financial_info.lastclaimedadjustmentinvoice_fc if financial_info else 0,
            'acc_g_r': None, 'acc_n_r': None,
            'ewcc_g_fc': 0,
            'ewcc_n_fc': financial_info.lastclaimedextraworkinvoice_fc if financial_info else 0,
            'ewcc_g_r': None, 'ewcc_n_r': None,
            'cvat_fc': 0, 'cvat_r': None,
            'cpi_fc': 0, 'cpi_r': None,
            'ccpi_a_fc': 0, 'ccpi_a_r': None,
            'ccpi_a_vat_fc': 0, 'ccpi_a_vat_r': None,
            'ccpi_a_vat_ew_fc': 0, 'ccpi_a_vat_ew_r': None,
            'cp_pp_fc': 0, 'cp_pp_r': None,
            'pp_pp_fc': 0, 'pp_pp_r': None,
            'm': True, 'typevalue': None
        }
        FinancialInvoice.objects.update_or_create(
            contractid=contract,
            dateid=date,
            r=False,
            defaults=defaults
        )
    
    @staticmethod
    def get_financial_invoices_for_report(contract_id, date_id):
        """Get financial invoices for report (last 9 records)."""
        return FinancialInvoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('-dateid')[:9][::-1]


class WorkVolumeService:
    """Service for managing work volume data."""
    
    DEFAULT_WORK_TYPES = [
        "خاکبرداری(متر مکعب)",
        "خاکریزی(متر مکعب)",
        "بتن ریزی(متر مکعب)",
        "نصب اسکلت فلزی(تن)",
        "نصب تجهبزات داخلی(تن)",
        "نصب تجهیزات خارجی(تن)",
    ]
    
    @staticmethod
    def get_or_create_work_volumes(user_id, contract_id, date_id, report_id):
        """Get or create work volumes for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        contract = Contract.objects.get(pk=contract_id)
        date = ReportDate.objects.get(pk=date_id)

        record_count = WorkVolume.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).count()
        
        last_date_id = ReportDate.objects.filter(
            dateid__lt=date_id
        ).aggregate(Max('dateid'))['dateid__max']

        has_previous_data = WorkVolume.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=last_date_id
        ).count() > 1
        
        if record_count == 0:
            if not has_previous_data:
                WorkVolumeService._create_default_work_volumes(contract, date)
            else:
                WorkVolumeService._copy_previous_work_volumes(
                    contract, date, contract_id, last_date_id
                )
        
        return WorkVolume.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
    
    @staticmethod
    def _create_default_work_volumes(contract, date):
        """Create default work volume entries."""
        work_volumes = [
            WorkVolume(contractid=contract, dateid=date, work=work_type)
            for work_type in WorkVolumeService.DEFAULT_WORK_TYPES
        ]
        WorkVolume.objects.bulk_create(work_volumes)
    
    @staticmethod
    def _copy_previous_work_volumes(contract, date, contract_id, last_date_id):
        """Copy work volumes from previous period."""
        previous_volumes = WorkVolume.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=last_date_id
        )
        
        for volume in previous_volumes:
            WorkVolume.objects.create(
                contractid=contract,
                dateid=date,
                work=volume.work,
                planestimate=volume.planestimate,
                totalestimate=volume.totalestimate,
                executedsofar=volume.executedsofar
            )
    
    @staticmethod
    def get_work_volumes_for_report(contract_id, date_id):
        """Get work volumes for report."""
        return WorkVolume.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )


class PmsProgressService:
    """Service for managing PMS progress data."""
    
    DEFAULT_ITEMS = [
        "کل کارهای سیویل",
        "کل کارهای نصب",
        "نصب اسکلت فلزی",
        "بیل مکانیکی",
        "نصب تجهیزات مکانیکال",
        "نصب تجهیزات برق و ابزار دقیق",
        "کل نصب تجهیزات داخلی (بدون در نظرگیری اسکلت فلزی)",
        "کل نصب تجهیزات خارجی",
    ]
    
    @staticmethod
    def get_or_create_pms_progress(user_id, contract_id, date_id, report_id):
        """Get or create PMS progress for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        contract = Contract.objects.get(pk=contract_id)
        date = ReportDate.objects.get(pk=date_id)

        record_count = PmsProgress.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).count()
        
        last_date_id = ReportDate.objects.filter(
            dateid__lt=date_id
        ).aggregate(Max('dateid'))['dateid__max']

        has_previous_data = PmsProgress.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=last_date_id
        ).count() > 1
        
        if record_count == 0:
            if not has_previous_data:
                PmsProgressService._create_default_pms_progress(contract, date)
            else:
                PmsProgressService._copy_previous_pms_progress(
                    contract, date, contract_id, last_date_id
                )
        
        return PmsProgress.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
    
    @staticmethod
    def _create_default_pms_progress(contract, date):
        """Create default PMS progress entries."""
        pms_items = [
            PmsProgress(contractid=contract, dateid=date, item=item)
            for item in PmsProgressService.DEFAULT_ITEMS
        ]
        PmsProgress.objects.bulk_create(pms_items)
    
    @staticmethod
    def _copy_previous_pms_progress(contract, date, contract_id, last_date_id):
        """Copy PMS progress from previous period."""
        previous_progress = PmsProgress.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=last_date_id
        )
        
        for progress in previous_progress:
            PmsProgress.objects.create(
                contractid=contract,
                dateid=date,
                item=progress.item,
                lastplanprogress=progress.lastplanprogress,
                lastplanvirtualprogress=progress.lastplanvirtualprogress
            )
    
    @staticmethod
    def get_pms_progress_for_report(contract_id, date_id):
        """Get PMS progress for report."""
        return PmsProgress.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )


class BudgetCostService:
    """Service for managing budget cost data."""
    
    @staticmethod
    def get_or_create_budget_cost(user_id, contract_id, date_id, report_id):
        """Get or create budget cost for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        exists = Budgetcost.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).exists()

        if not exists:
            contract = Contract.objects.get(pk=contract_id)
            date = ReportDate.objects.get(pk=date_id)
            Budgetcost.objects.update_or_create(
                contractid=contract,
                dateid=date,
                defaults={
                    'bac_r': 0, 'bac_fc': 0,
                    'eac_r': 0, 'eac_fc': 0,
                    'ev_r': 0, 'ev_fc': 0,
                    'ac_r': 0, 'ac_fc': 0,
                    'description': ''
                }
            )

        return Budgetcost.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('dateid')
    
    @staticmethod
    def set_admin_description(contract_id, date_id, description):
        """Set admin description for budget cost."""
        budget = Budgetcost.objects.get(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
        budget.description = description
        budget.save()
    
    @staticmethod
    def get_budget_cost_for_report(contract_id, date_id):
        """Get budget costs for report (last 6 records)."""
        return Budgetcost.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('-dateid')[:6][::-1]


class MachineryService:
    """Service for managing machinery data."""
    
    DEFAULT_MACHINES = [
        "تاور کرین", "بولدوزر", "لودر", "بیل مکانیکی", "غلطک", "گریدر",
        "کمپرسی دو محور", "جرثقیل", "تراک میکسر", "تانکر آبپاش", "تراکتور",
        "پمپ بتن", "آمبولانس", "ماشین آتشنشانی", "لودر مینی بوس و اتوبوس",
        "انواع سواری", "دستگاه بچینگ", "دستگاه بلوک زنی", "دستگاه جدول زنی",
        "تانکر سوخت آب", "چکش مکانیکی"
    ]
    
    @staticmethod
    def get_or_create_machinery(user_id, contract_id, date_id, report_id):
        """Get or create machinery for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        contract = Contract.objects.get(pk=contract_id)
        date = ReportDate.objects.get(pk=date_id)
        
        record_count = Machinary.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).count()
        
        last_date_id = ReportDate.objects.filter(
            dateid__lt=date_id
        ).aggregate(Max('dateid'))['dateid__max']

        has_previous_data = Machinary.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=last_date_id
        ).exists()
        
        total_field_exist = False
        
        if record_count == 0:
            if not has_previous_data:
                MachineryService._create_default_machinery(contract, date)
            else:
                total_field_exist = MachineryService._copy_previous_machinery(
                    contract, date, contract_id, last_date_id
                )
        
        # Ensure total field exists and is calculated
        MachineryService._ensure_total_field(
            contract, date, contract_id, date_id, total_field_exist
        )
        
        return Machinary.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).order_by("priority", "machinaryid")
    
    @staticmethod
    def _create_default_machinery(contract, date):
        """Create default machinery entries."""
        machines = [
            Machinary(contractid=contract, dateid=date, machine=machine)
            for machine in MachineryService.DEFAULT_MACHINES
        ]
        machines.append(
            Machinary(contractid=contract, dateid=date, machine="جمع کل", priority=1)
        )
        Machinary.objects.bulk_create(machines)
    
    @staticmethod
    def _copy_previous_machinery(contract, date, contract_id, last_date_id):
        """Copy machinery from previous period."""
        previous_machinery = Machinary.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=last_date_id
        )
        
        total_field_exist = False
        for machinery in previous_machinery:
            if machinery.machine == "جمع کل":
                total_field_exist = True
            
            Machinary.objects.create(
                contractid=contract,
                dateid=date,
                machine=machinery.machine,
                activeno=machinery.activeno or 0,
                inactiveno=machinery.inactiveno or 0,
                priority=1 if machinery.machine == "جمع کل" else 0,
                description=machinery.description or ''
            )
        
        return total_field_exist
    
    @staticmethod
    def _ensure_total_field(contract, date, contract_id, date_id, total_field_exist):
        """Ensure total field exists and is calculated correctly."""
        machineries = Machinary.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
        
        if not total_field_exist:
            activeno = machineries.exclude(
                machine__exact="جمع کل"
            ).aggregate(Sum('activeno'))['activeno__sum']
            
            inactiveno = machineries.exclude(
                machine__exact="جمع کل"
            ).aggregate(Sum('inactiveno'))['inactiveno__sum']
            
            total_exists = machineries.filter(machine__exact="جمع کل").exists()
            
            if not total_exists:
                Machinary.objects.create(
                    contractid=contract,
                    dateid=date,
                    machine="جمع کل",
                    activeno=activeno or 0,
                    inactiveno=inactiveno or 0,
                    priority=1,
                    description=''
                )
            else:
                total = machineries.filter(machine__exact="جمع کل").first()
                total.activeno = activeno
                total.inactiveno = inactiveno
                total.save()
    
    @staticmethod
    def get_machinery_for_report(contract_id, date_id):
        """Get machinery for report."""
        return Machinary.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )


class ProjectPersonnelService:
    """Service for managing project personnel data."""
    
    @staticmethod
    def get_or_create_project_personnel(user_id, contract_id, date_id, report_id):
        """Get or create project personnel for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        exists = ProjectPersonnel.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).exists()

        if not exists:
            contract = Contract.objects.get(pk=contract_id)
            date = ReportDate.objects.get(pk=date_id)
            ProjectPersonnel.objects.update_or_create(
                contractid=contract,
                dateid=date,
                defaults={'dpno': 0, 'dcpno': 0, 'mepno': 0}
            )
        
        return ProjectPersonnel.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('dateid')
    
    @staticmethod
    def get_project_personnel_for_report(contract_id, date_id):
        """Get project personnel for report (last 9 records)."""
        return ProjectPersonnel.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('-dateid')[:9][::-1]


class ProblemService:
    """Service for managing problem data."""
    
    @staticmethod
    def get_problems(user_id, contract_id, date_id, report_id):
        """Get problems for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        return Problem.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
    
    @staticmethod
    def get_problems_for_report(contract_id, date_id):
        """Get problems for report."""
        return Problem.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )


class CriticalActionService:
    """Service for managing critical action data."""
    
    @staticmethod
    def get_critical_actions(user_id, contract_id, date_id, report_id):
        """Get critical actions for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        return CriticalAction.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
    
    @staticmethod
    def get_critical_actions_for_report(contract_id, date_id):
        """Get critical actions for report."""
        return CriticalAction.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
    
    @staticmethod
    def get_invoice_for_report_1(contract_id, date_id):
        """Get invoice for report (single record)."""
        invoices = Invoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )
        return invoices.first()
    
    @staticmethod
    def get_invoice_for_report_2(contract_id, date_id):
        """Get invoices for report (last 9 records)."""
        return Invoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('-dateid')[:9][::-1]


class FinancialInvoiceService:
    """Service for managing financial invoice data."""
    
    @staticmethod
    def get_or_create_financial_invoices(user_id, contract_id, date_id, report_id):
        """Get or create financial invoices for a contract and date."""
        set_report_visit(user_id, contract_id, date_id, report_id)
        
        exists = FinancialInvoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        ).exists()

        if not exists:
            contract = Contract.objects.get(pk=contract_id)
            date = ReportDate.objects.get(pk=date_id)
            financial_infos = FinancialInfo.objects.filter(
                contractid__exact=contract_id, 
                dateid__exact=date_id
            )
            
            FinancialInvoiceService._create_rials_financial_invoice(
                contract, date, financial_infos.first() if financial_infos.exists() else None
            )
            FinancialInvoiceService._create_foreign_currency_financial_invoice(
                contract, date, financial_infos.first() if financial_infos.exists() else None
            )
        
        return FinancialInvoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__lte=date_id
        ).order_by('dateid')
    
    @staticmethod
    def _create_rials_financial_invoice(contract, date, financial_info):
        """Create financial invoice in Rials."""
        defaults = {
            'senddate': datetime.now(),
            'invoicetype': 'T',
            'alino': None, 'almino': None,
            'aci_g_r': 0,
            'aci_n_r': financial_info.lastverifiedinvoice_r if financial_info else 0,
            'aci_g_fc': None, 'aci_n_fc': None,
            'aca_g_r': 0,
            'aca_n_r': financial_info.lastverifiedadjustmentinvoice_r if financial_info else 0,
            'aca_g_fc': None, 'aca_n_fc': None,
            'ew_g_r': 0,
            'ew_n_r': financial_info.lastverifiedextraworkinvoice_r if financial_info else 0,
            'ew_g_fc': None, 'ew_n_fc': None,
            'icc_g_r': 0,
            'icc_n_r': financial_info.lastclaimedinvoice_r if financial_info else 0,
            'icc_g_fc': None, 'icc_n_fc': None,
            'acc_g_r': 0,
            'acc_n_r': financial_info.lastclaimedadjustmentinvoice_r if financial_info else 0,
            'acc_g_fc': None, 'acc_n_fc': None,
            'ewcc_g_r': 0,
            'ewcc_n_r': financial_info.lastclaimedextraworkinvoice_r if financial_info else 0,
            'ewcc_g_fc': None, 'ewcc_n_fc': None,
            'cvat_r': 0, 'cvat_fc': None,
            'cpi_r': 0, 'cpi_fc': None,
            'ccpi_a_r': 0, 'ccpi_a_fc': None,
            'ccpi_a_vat_r': 0, 'ccpi_a_vat_fc': None,
            'ccpi_a_vat_ew_r': 0, 'ccpi_a_vat_ew_fc': None,
            'cp_pp_r': 0, 'cp_pp_fc': None,
            'pp_pp_r': 0, 'pp_pp_fc': None,
            'm': True, 'typevalue': None
        }
        FinancialInvoice.objects.update_or_create(
            contractid=contract,
            dateid=date,
            r=True,
            defaults=defaults
        )
    
    @staticmethod
    def _create_foreign_currency_financial_invoice(contract, date, financial_info):
        """Create financial invoice in Foreign Currency."""
        defaults = {
            'senddate': datetime.now(),
            'invoicetype': 'T',
            'alino': None, 'almino': None,
            'aci_g_fc': 0,
            'aci_n_fc': financial_info.lastverifiedinvoice_fc if financial_info else 0,
            'aci_g_r': None, 'aci_n_r': None,
            'aca_g_fc': 0,
            'aca_n_fc': financial_info.lastverifiedadjustmentinvoice_fc if financial_info else 0,
            'aca_g_r': None, 'aca_n_r': None,
            'ew_g_fc': 0,
            'ew_n_fc': financial_info.lastverifiedextraworkinvoice_fc if financial_info else 0,
            'ew_g_r': None, 'ew_n_r': None,
            'icc_g_fc': 0,
            'icc_n_fc': financial_info.lastclaimedinvoice_fc if financial_info else 0,
            'icc_g_r': None, 'icc_n_r': None,
            'acc_g_fc': 0,
            'acc_n_fc': financial_info.lastclaimedadjustmentinvoice_fc if financial_info else 0,
            'acc_g_r': None, 'acc_n_r': None,
            'ewcc_g_fc': 0,
            'ewcc_n_fc': financial_info.lastclaimedextraworkinvoice_fc if financial_info else 0,
            'ewcc_g_r': None, 'ewcc_n_r': None,
            'cvat_fc': 0, 'cvat_r': None,
            'cpi_fc': 0, 'cpi_r': None,
            'ccpi_a_fc': 0, 'ccpi_a_r': None,
            'ccpi_a_vat_fc': 0, 'ccpi_a_vat_r': None,
            'ccpi_a_vat_ew_fc': 0, 'ccpi_a_vat_ew_r': None,
            'cp_pp_fc': 0, 'cp_pp_r': None,
            'pp_pp_fc': 0, 'pp_pp_r': None,
            'm': True, 'typevalue': None
        }

        FinancialInvoice.objects.update_or_create(
            contractid=contract,
            dateid=date,
            r=False,
            defaults=defaults
        )
    
    @staticmethod       
    def get_financial_invoice_for_report(contract_id, date_id):
        """Get financial invoice for report."""
        return FinancialInvoice.objects.filter(
            contractid__exact=contract_id, 
            dateid__exact=date_id
        )