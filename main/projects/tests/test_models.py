"""
Unit tests for projects models.
Tests model methods, properties, and custom manager methods.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime, date

from projects.models import (
    ReportDate, ReportConfirm, FinancialInfo, Hse, ProgressState,
    TimeprogressState, Invoice, FinancialInvoice, WorkVolume,
    PmsProgress, Budgetcost, Machinary, ProjectPersonnel,
    Problem, CriticalAction
)
from contracts.models import Contract


class ReportDateModelTest(TestCase):
    """Test ReportDate model."""
    
    def test_shamsi_date_format(self):
        """Test that shamsi date is formatted correctly."""
        report_date = ReportDate.objects.create(
            year='1403',
            month='05'
        )
        
        self.assertEqual(report_date.shamsiDate(), '1403-05')
    
    def test_report_date_creation(self):
        """Test creating a report date."""
        report_date = ReportDate.objects.create(
            year='1403',
            month='01'
        )
        
        self.assertEqual(report_date.year, '1403')
        self.assertEqual(report_date.month, '01')


class ReportConfirmModelTest(TestCase):
    """Test ReportConfirm model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    def test_userconfirmer_returns_full_name(self):
        """Test that userconfirmer returns user's full name."""
        report_confirm = ReportConfirm.objects.create(
            contractid=self.contract,
            dateid=self.date,
            userid=self.user,
            type=1
        )
        
        self.assertEqual(report_confirm.userconfirmer(), 'Test User')
    
    def test_user_confirm_date_conversion(self):
        """Test user confirm date conversion to Shamsi."""
        report_confirm = ReportConfirm.objects.create(
            contractid=self.contract,
            dateid=self.date,
            userid=self.user,
            type=1,
            userconfirmdate=date(2024, 3, 21)  # First day of Persian year
        )
        
        shamsi_date = report_confirm.userconfirmshamsidate()
        self.assertIsNotNone(shamsi_date)


class HseModelTest(TestCase):
    """Test HSE model."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date1 = ReportDate.objects.create(year='1403', month='01')
        self.date2 = ReportDate.objects.create(year='1403', month='02')
        self.date3 = ReportDate.objects.create(year='1403', month='03')
    
    def test_total_death_no_calculation(self):
        """Test cumulative death count calculation."""
        Hse.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            deathno=2
        )
        Hse.objects.create(
            contractid=self.contract,
            dateid=self.date2,
            deathno=1
        )
        hse3 = Hse.objects.create(
            contractid=self.contract,
            dateid=self.date3,
            deathno=0
        )
        
        self.assertEqual(hse3.totaldeathno(), 3)
    
    def test_total_wound_no_calculation(self):
        """Test cumulative wound count calculation."""
        Hse.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            woundno=5
        )
        Hse.objects.create(
            contractid=self.contract,
            dateid=self.date2,
            woundno=3
        )
        hse3 = Hse.objects.create(
            contractid=self.contract,
            dateid=self.date3,
            woundno=2
        )
        
        self.assertEqual(hse3.totalwoundno(), 10)
    
    def test_total_disadvantage_event_no_calculation(self):
        """Test cumulative disadvantage event count calculation."""
        Hse.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            disadvantageeventno=4
        )
        Hse.objects.create(
            contractid=self.contract,
            dateid=self.date2,
            disadvantageeventno=2
        )
        hse3 = Hse.objects.create(
            contractid=self.contract,
            dateid=self.date3,
            disadvantageeventno=1
        )
        
        self.assertEqual(hse3.totaldisadvantageeventno(), 7)


class InvoiceModelTest(TestCase):
    """Test Invoice model."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='05')
    
    def test_confirmed_invoice_amounts_calculation(self):
        """Test calculation of confirmed invoice amounts."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True,
            aci_g_r=1000,
            aca_g_r=200,
            ew_g_r=300
        )
        
        self.assertEqual(invoice.confirmedInvoiceAmounts(), 1500)
    
    def test_sent_invoice_amounts_calculation(self):
        """Test calculation of sent invoice amounts."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True,
            icc_g_r=1200,
            acc_g_r=250,
            ewcc_g_r=350
        )
        
        self.assertEqual(invoice.sentInvoiceAmounts(), 1800)
    
    def test_all_received_calculation(self):
        """Test calculation of all received amounts."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True,
            ccpi_a_vat_ew_r=5000,
            cvat_r=500
        )
        
        self.assertEqual(invoice.allReceived(), 4500)
    
    def test_confirmed_amount_calculation(self):
        """Test calculation of confirmed amount."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True,
            aci_n_r=1000,
            aca_n_r=200,
            ew_n_r=300
        )
        
        self.assertEqual(invoice.confirmedAmount(), 1500)
    
    def test_receive_percent_calculation(self):
        """Test calculation of receive percentage."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True,
            ccpi_a_vat_ew_r=5000,
            cvat_r=500,
            aci_n_r=3000,
            aca_n_r=600,
            ew_n_r=400
        )
        
        # (5000 - 500) / (3000 + 600 + 400) * 100 = 112.5%
        self.assertEqual(invoice.receivePercent(), 112.5)
    
    def test_receive_percent_zero_division(self):
        """Test that receive percent handles zero division."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True,
            ccpi_a_vat_ew_r=5000,
            cvat_r=500,
            aci_n_r=0,
            aca_n_r=0,
            ew_n_r=0
        )
        
        self.assertEqual(invoice.receivePercent(), 0)
    
    def test_persian_month_conversion(self):
        """Test Persian month name conversion."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True
        )
        
        self.assertEqual(invoice.persianMonth(), 'مرداد')


class ProgressStateModelTest(TestCase):
    """Test ProgressState model."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='07')
    
    def test_year_property(self):
        """Test year property."""
        progress = ProgressState.objects.create(
            contractid=self.contract,
            dateid=self.date,
            plan_replan='00',
            pp_e=10.5,
            ap_e=9.5,
            pp_p=8.0,
            ap_p=7.5,
            pp_c=5.0,
            ap_c=4.5,
            pp_t=23.5,
            ap_t=21.5,
            pr_t=20.0,
            pfc_t=15.0
        )
        
        self.assertEqual(progress.year(), '1403')
    
    def test_month_property(self):
        """Test month property."""
        progress = ProgressState.objects.create(
            contractid=self.contract,
            dateid=self.date,
            plan_replan='00',
            pp_e=10.5,
            ap_e=9.5,
            pp_p=8.0,
            ap_p=7.5,
            pp_c=5.0,
            ap_c=4.5,
            pp_t=23.5,
            ap_t=21.5,
            pr_t=20.0,
            pfc_t=15.0
        )
        
        self.assertEqual(progress.month(), '07')
    
    def test_persian_6_month_conversion(self):
        """Test Persian 6-month name conversion."""
        progress = ProgressState.objects.create(
            contractid=self.contract,
            dateid=self.date,
            plan_replan='00',
            pp_e=10.5,
            ap_e=9.5,
            pp_p=8.0,
            ap_p=7.5,
            pp_c=5.0,
            ap_c=4.5,
            pp_t=23.5,
            ap_t=21.5,
            pr_t=20.0,
            pfc_t=15.0
        )
        
        self.assertEqual(progress.persian6Month(), 'مهر')


class ProjectPersonnelModelTest(TestCase):
    """Test ProjectPersonnel model."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        # Date after 1126 to test new field logic
        self.date_new = ReportDate.objects.create(year='1403', month='01')
        self.date_new.dateid = 1127
        self.date_new.save()
        
        # Date before 1126 to test old field logic
        self.date_old = ReportDate.objects.create(year='1402', month='12')
        self.date_old.dateid = 1125
        self.date_old.save()
    
    def test_cotno_calculation_new_fields(self):
        """Test central office total number calculation for new data structure."""
        personnel = ProjectPersonnel.objects.create(
            contractid=self.contract,
            dateid=self.date_new,
            copmpno=5,
            coepno=3,
            coppno=2,
            cocpno=4,
            dpno=10,
            dcpno=5,
            mepno=8
        )
        
        # Should use new fields: copmpno + coepno + coppno + cocpno = 14
        self.assertEqual(personnel.cotno(), 14)
    
    def test_cotno_calculation_old_fields(self):
        """Test central office total number calculation for old data structure."""
        personnel = ProjectPersonnel.objects.create(
            contractid=self.contract,
            dateid=self.date_old,
            copmpno=5,
            coepno=3,
            coppno=2,
            cocpno=4,
            dpno=10,
            dcpno=5,
            mepno=8
        )
        
        # Should use old field: dpno = 10
        self.assertEqual(personnel.cotno(), 10)
    
    def test_wstno_calculation_new_fields(self):
        """Test workshop total number calculation for new data structure."""
        personnel = ProjectPersonnel.objects.create(
            contractid=self.contract,
            dateid=self.date_new,
            wscpno=6,
            wscaopno=3,
            wsaopno=2,
            dpno=10,
            dcpno=5,
            mepno=8
        )
        
        # Should use new fields: wscpno + wscaopno + wsaopno = 11
        self.assertEqual(personnel.wstno(), 11)
    
    def test_wstno_calculation_old_fields(self):
        """Test workshop total number calculation for old data structure."""
        personnel = ProjectPersonnel.objects.create(
            contractid=self.contract,
            dateid=self.date_old,
            wscpno=6,
            wscaopno=3,
            wsaopno=2,
            dpno=10,
            dcpno=5,
            mepno=8
        )
        
        # Should use old field: mepno = 8
        self.assertEqual(personnel.wstno(), 8)
    
    def test_persian_month_conversion(self):
        """Test Persian month name conversion."""
        personnel = ProjectPersonnel.objects.create(
            contractid=self.contract,
            dateid=self.date_new,
            dpno=10,
            dcpno=5,
            mepno=8
        )
        
        self.assertEqual(personnel.persianMonth(), 'فروردین')


class BudgetcostModelTest(TestCase):
    """Test Budgetcost model."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='03')
    
    def test_year_property(self):
        """Test year property."""
        budget = Budgetcost.objects.create(
            contractid=self.contract,
            dateid=self.date,
            bac_r=1000000,
            eac_r=950000
        )
        
        self.assertEqual(budget.year(), '1403')
    
    def test_month_property(self):
        """Test month property."""
        budget = Budgetcost.objects.create(
            contractid=self.contract,
            dateid=self.date,
            bac_r=1000000,
            eac_r=950000
        )
        
        self.assertEqual(budget.month(), '03')
    
    def test_persian_month_conversion(self):
        """Test Persian month name conversion."""
        budget = Budgetcost.objects.create(
            contractid=self.contract,
            dateid=self.date,
            bac_r=1000000,
            eac_r=950000
        )
        
        self.assertEqual(budget.persianMonth(), 'خرداد')


class MachineryModelTest(TestCase):
    """Test Machinery model."""
    
    def test_machinery_creation_with_defaults(self):
        """Test creating machinery with default values."""
        contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        date = ReportDate.objects.create(year='1403', month='01')
        
        machinery = Machinary.objects.create(
            contractid=contract,
            dateid=date,
            machine="تاور کرین"
        )
        
        self.assertEqual(machinery.activeno, 0)
        self.assertEqual(machinery.inactiveno, 0)
        self.assertEqual(machinery.priority, False)
    
    def test_machinery_total_row_priority(self):
        """Test that total row has priority set."""
        contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        date = ReportDate.objects.create(year='1403', month='01')
        
        total = Machinary.objects.create(
            contractid=contract,
            dateid=date,
            machine="جمع کل",
            priority=True,
            activeno=10,
            inactiveno=3
        )
        
        self.assertTrue(total.priority)


class WorkVolumeModelTest(TestCase):
    """Test WorkVolume model."""
    
    def test_work_volume_creation(self):
        """Test creating a work volume entry."""
        contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        date = ReportDate.objects.create(year='1403', month='01')
        
        work_volume = WorkVolume.objects.create(
            contractid=contract,
            dateid=date,
            work="خاکبرداری(متر مکعب)",
            planestimate=1000,
            totalestimate=1200,
            executedsofar=800
        )
        
        self.assertEqual(work_volume.work, "خاکبرداری(متر مکعب)")
        self.assertEqual(work_volume.planestimate, 1000)
        self.assertEqual(work_volume.executedsofar, 800)


class PmsProgressModelTest(TestCase):
    """Test PmsProgress model."""
    
    def test_pmsprogress_creation(self):
        """Test creating a PMS progress entry."""
        contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        date = ReportDate.objects.create(year='1403', month='01')
        
        pms = PmsProgress.objects.create(
            contractid=contract,
            dateid=date,
            item="کل کارهای سیویل",
            lastplanprogress=75,
            lastplanvirtualprogress=80
        )
        
        self.assertEqual(pms.item, "کل کارهای سیویل")
        self.assertEqual(pms.lastplanprogress, 75)


# Run tests with: python manage.py test projects.tests.test_models