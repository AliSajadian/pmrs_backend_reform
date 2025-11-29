"""
Unit tests for projects serializers.
Tests serialization, deserialization, and validation.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

from projects.models import (
    ReportDate, ReportConfirm, FinancialInfo, Hse, ProgressState,
    TimeprogressState, Invoice, FinancialInvoice, WorkVolume,
    PmsProgress, Budgetcost, Machinary, ProjectPersonnel,
    Problem, CriticalAction
)
from projects.serializers import (
    ReportDateSerializerEx, ReportConfirmSerializer, ReportsConfirmedSerializer,
    ProjectManagerReportConfirmSerializer, CoordinatorReportConfirmSerializer,
    FinancialInfoSerializer, FinancialInfoReportSerializer, HseSerializer,
    HseReportSerializer, ProgressStateSerializer, ProgressStateReportSerializer,
    TimeProgressStateSerializer, InvoiceSerializer, InvoiceReport1Serializer,
    InvoiceReport2Serializer, FinancialInvoiceSerializer,
    FinancialInvoiceReportSerializer, WorkvolumeSerializer,
    PmsprogressSerializer, BudgetCostSerializer, BudgetCostReportSerializer,
    MachinerySerializer, ProjectPersonalSerializer,
    ProjectPersonalReportSerializer, ProblemSerializer, CriticalActionSerializer
)
from contracts.models import Contract


class ReportDateSerializerTest(TestCase):
    """Test ReportDate serializer."""
    
    def test_serialization_includes_shamsi_date(self):
        """Test that serialization includes shamsi date field."""
        report_date = ReportDate.objects.create(
            year='1403',
            month='05'
        )
        
        serializer = ReportDateSerializerEx(report_date)
        data = serializer.data
        
        self.assertIn('shamsiDate', data)
        self.assertEqual(data['shamsiDate'], '1403-05')
        self.assertEqual(data['year'], '1403')
        self.assertEqual(data['month'], '05')
    
    def test_serialization_multiple_dates(self):
        """Test serializing multiple report dates."""
        ReportDate.objects.create(year='1403', month='01')
        ReportDate.objects.create(year='1403', month='02')
        ReportDate.objects.create(year='1403', month='03')
        
        dates = ReportDate.objects.all()
        serializer = ReportDateSerializerEx(dates, many=True)
        
        self.assertEqual(len(serializer.data), 3)


class ReportConfirmSerializerTest(TestCase):
    """Test ReportConfirm serializers."""
    
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
    
    def test_reports_confirmed_serializer_includes_user_info(self):
        """Test that ReportsConfirmedSerializer includes user information."""
        report_confirm = ReportConfirm.objects.create(
            contractid=self.contract,
            dateid=self.date,
            userid=self.user,
            type=1,
            user_c=True,
            pm_c=False,
            userconfirmdate=date(2024, 3, 21)
        )
        
        serializer = ReportsConfirmedSerializer(report_confirm)
        data = serializer.data
        
        self.assertIn('userconfirmer', data)
        self.assertEqual(data['userconfirmer'], 'Test User')
        self.assertIn('userconfirmshamsidate', data)
        self.assertIn('pmconfirmshamsidate', data)
    
    def test_project_manager_serializer(self):
        """Test ProjectManagerReportConfirmSerializer."""
        report_confirm = ReportConfirm.objects.create(
            contractid=self.contract,
            dateid=self.date,
            userid=self.user,
            type=1,
            pm_c=True,
            pmconfirmdate=date(2024, 3, 21)
        )
        
        serializer = ProjectManagerReportConfirmSerializer(report_confirm)
        data = serializer.data
        
        self.assertIn('pm_c', data)
        self.assertIn('pmconfirmshamsidate', data)
    
    def test_coordinator_serializer(self):
        """Test CoordinatorReportConfirmSerializer."""
        report_confirm = ReportConfirm.objects.create(
            contractid=self.contract,
            dateid=self.date,
            userid=self.user,
            type=1,
            user_c=True,
            userconfirmdate=date(2024, 3, 21)
        )
        
        serializer = CoordinatorReportConfirmSerializer(report_confirm)
        data = serializer.data
        
        self.assertIn('user_c', data)
        self.assertIn('userconfirmshamsidate', data)


class FinancialInfoSerializerTest(TestCase):
    """Test FinancialInfo serializers."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    def test_serialization_all_fields(self):
        """Test that all fields are serialized."""
        financial_info = FinancialInfo.objects.create(
            contractid=self.contract,
            dateid=self.date,
            lastclaimedinvoice_r=5000,
            lastclaimedinvoice_fc=100,
            lci_no=5
        )
        
        serializer = FinancialInfoSerializer(financial_info)
        data = serializer.data
        
        self.assertEqual(data['lastclaimedinvoice_r'], 5000)
        self.assertEqual(data['lastclaimedinvoice_fc'], 100)
        self.assertEqual(data['lci_no'], 5)
    
    def test_deserialization_valid_data(self):
        """Test deserializing valid data."""
        data = {
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'lastclaimedinvoice_r': 5000,
            'lastclaimedinvoice_fc': 100,
            'lci_no': 5
        }
        
        serializer = FinancialInfoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_financial_info_report_serializer(self):
        """Test FinancialInfoReportSerializer with limited fields."""
        financial_info = FinancialInfo.objects.create(
            contractid=self.contract,
            dateid=self.date,
            estdebitcredit_r=1000,
            estcost_r=50000,
            estclientpayment_r=45000
        )
        
        serializer = FinancialInfoReportSerializer(financial_info)
        data = serializer.data
        
        # Should only have 3 fields
        self.assertEqual(len(data), 3)
        self.assertIn('estdebitcredit_r', data)
        self.assertIn('estcost_r', data)
        self.assertIn('estclientpayment_r', data)


class HseSerializerTest(TestCase):
    """Test HSE serializers."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date1 = ReportDate.objects.create(year='1403', month='01')
        self.date2 = ReportDate.objects.create(year='1403', month='02')
    
    def test_hse_serialization(self):
        """Test HSE serialization."""
        hse = Hse.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            totaloperationdays=30,
            withouteventdays=28,
            deathno=0,
            woundno=2,
            disadvantageeventno=1
        )
        
        serializer = HseSerializer(hse)
        data = serializer.data
        
        self.assertEqual(data['totaloperationdays'], 30)
        self.assertEqual(data['woundno'], 2)
    
    def test_hse_report_serializer_includes_totals(self):
        """Test that HseReportSerializer includes cumulative totals."""
        Hse.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            totaloperationdays=30,
            deathno=1,
            woundno=2,
            disadvantageeventno=1
        )
        hse2 = Hse.objects.create(
            contractid=self.contract,
            dateid=self.date2,
            totaloperationdays=30,
            withouteventdays=29,
            deathno=0,
            woundno=1,
            disadvantageeventno=0
        )
        
        serializer = HseReportSerializer(hse2)
        data = serializer.data
        
        self.assertIn('totaldeathno', data)
        self.assertIn('totalwoundno', data)
        self.assertIn('totaldisadvantageeventno', data)
        self.assertEqual(data['totaldeathno'], 1)
        self.assertEqual(data['totalwoundno'], 3)


class ProgressStateSerializerTest(TestCase):
    """Test ProgressState serializers."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='05')
    
    def test_serialization_includes_year_month(self):
        """Test that serialization includes year and month."""
        progress = ProgressState.objects.create(
            contractid=self.contract,
            dateid=self.date,
            plan_replan='00',
            pp_e=Decimal('10.50'),
            ap_e=Decimal('9.50'),
            pp_p=Decimal('8.00'),
            ap_p=Decimal('7.50'),
            pp_c=Decimal('5.00'),
            ap_c=Decimal('4.50'),
            pp_t=Decimal('23.50'),
            ap_t=Decimal('21.50'),
            pr_t=Decimal('20.00'),
            pfc_t=Decimal('15.00')
        )
        
        serializer = ProgressStateSerializer(progress)
        data = serializer.data
        
        self.assertIn('year', data)
        self.assertIn('month', data)
        self.assertEqual(data['year'], '1403')
        self.assertEqual(data['month'], '05')
    
    def test_progress_state_report_serializer(self):
        """Test ProgressStateReportSerializer."""
        progress = ProgressState.objects.create(
            contractid=self.contract,
            dateid=self.date,
            plan_replan='00',
            pp_e=Decimal('10.50'),
            ap_e=Decimal('9.50'),
            pp_p=Decimal('8.00'),
            ap_p=Decimal('7.50'),
            pp_c=Decimal('5.00'),
            ap_c=Decimal('4.50'),
            pp_t=Decimal('23.50'),
            ap_t=Decimal('21.50'),
            pr_t=Decimal('20.00'),
            pfc_t=Decimal('15.00')
        )
        
        serializer = ProgressStateReportSerializer(progress)
        data = serializer.data
        
        self.assertIn('persian6Month', data)
        self.assertEqual(data['persian6Month'], 'مرداد')


class InvoiceSerializerTest(TestCase):
    """Test Invoice serializers."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='03')
    
    def test_invoice_serialization(self):
        """Test Invoice serialization."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True,
            aci_g_r=1000,
            aca_g_r=200,
            ew_g_r=300
        )
        
        serializer = InvoiceSerializer(invoice)
        data = serializer.data
        
        self.assertEqual(data['aci_g_r'], 1000)
        self.assertIn('year', data)
        self.assertIn('month', data)
    
    def test_invoice_report1_serializer_includes_calculations(self):
        """Test InvoiceReport1Serializer includes calculated fields."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True,
            aci_g_r=1000,
            aca_g_r=200,
            ew_g_r=300,
            icc_g_r=1200,
            acc_g_r=250,
            ewcc_g_r=350,
            ccpi_a_vat_ew_r=5000,
            cvat_r=500,
            aci_n_r=3000,
            aca_n_r=600,
            ew_n_r=400
        )
        
        serializer = InvoiceReport1Serializer(invoice)
        data = serializer.data
        
        self.assertIn('confirmedInvoiceAmounts', data)
        self.assertIn('sentInvoiceAmounts', data)
        self.assertIn('receivePercent', data)
        self.assertEqual(data['confirmedInvoiceAmounts'], 1500)
        self.assertEqual(data['sentInvoiceAmounts'], 1800)
    
    def test_invoice_report2_serializer(self):
        """Test InvoiceReport2Serializer."""
        invoice = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True,
            aci_n_r=1000,
            aca_n_r=200,
            ew_n_r=300
        )
        
        serializer = InvoiceReport2Serializer(invoice)
        data = serializer.data
        
        self.assertIn('confirmedAmount', data)
        self.assertIn('persianMonth', data)
        self.assertEqual(data['persianMonth'], 'خرداد')


class WorkVolumeSerializerTest(TestCase):
    """Test WorkVolume serializer."""
    
    def test_serialization(self):
        """Test WorkVolume serialization."""
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
        
        serializer = WorkvolumeSerializer(work_volume)
        data = serializer.data
        
        self.assertEqual(data['work'], "خاکبرداری(متر مکعب)")
        self.assertEqual(data['planestimate'], 1000)
        self.assertEqual(data['executedsofar'], 800)


class PmsProgressSerializerTest(TestCase):
    """Test PmsProgress serializer."""
    
    def test_serialization(self):
        """Test PmsProgress serialization."""
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
        
        serializer = PmsprogressSerializer(pms)
        data = serializer.data
        
        self.assertEqual(data['item'], "کل کارهای سیویل")
        self.assertEqual(data['lastplanprogress'], 75)


class BudgetCostSerializerTest(TestCase):
    """Test BudgetCost serializers."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='10')
    
    def test_serialization_includes_year_month(self):
        """Test that serialization includes year and month."""
        budget = Budgetcost.objects.create(
            contractid=self.contract,
            dateid=self.date,
            bac_r=1000000,
            eac_r=950000,
            ev_r=500000,
            ac_r=480000
        )
        
        serializer = BudgetCostSerializer(budget)
        data = serializer.data
        
        self.assertIn('year', data)
        self.assertIn('month', data)
        self.assertEqual(data['year'], '1403')
        self.assertEqual(data['month'], '10')
    
    def test_budget_cost_report_serializer(self):
        """Test BudgetCostReportSerializer."""
        budget = Budgetcost.objects.create(
            contractid=self.contract,
            dateid=self.date,
            bac_r=1000000,
            eac_r=950000,
            description="Test description"
        )
        
        serializer = BudgetCostReportSerializer(budget)
        data = serializer.data
        
        self.assertIn('persianMonth', data)
        self.assertEqual(data['persianMonth'], 'دی')
        self.assertIn('description', data)


class MachinerySerializerTest(TestCase):
    """Test Machinery serializer."""
    
    def test_serialization(self):
        """Test Machinery serialization."""
        contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        date = ReportDate.objects.create(year='1403', month='01')
        
        machinery = Machinary.objects.create(
            contractid=contract,
            dateid=date,
            machine="تاور کرین",
            activeno=5,
            inactiveno=2,
            priority=False,
            description="Test machinery"
        )
        
        serializer = MachinerySerializer(machinery)
        data = serializer.data
        
        self.assertEqual(data['machine'], "تاور کرین")
        self.assertEqual(data['activeno'], 5)
        self.assertEqual(data['inactiveno'], 2)
        self.assertEqual(data['priority'], False)


class ProjectPersonnelSerializerTest(TestCase):
    """Test ProjectPersonnel serializers."""
    
    def setUp(self):
        """Set up test data."""
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='02')
    
    def test_serialization_includes_calculated_fields(self):
        """Test that serialization includes calculated total fields."""
        personnel = ProjectPersonnel.objects.create(
            contractid=self.contract,
            dateid=self.date,
            copmpno=5,
            coepno=3,
            coppno=2,
            cocpno=4,
            wscpno=6,
            wscaopno=3,
            wsaopno=2,
            dpno=10,
            dcpno=5,
            mepno=8
        )
        
        serializer = ProjectPersonalSerializer(personnel)
        data = serializer.data
        
        self.assertIn('cotno', data)
        self.assertIn('wstno', data)
        self.assertIn('year', data)
        self.assertIn('month', data)
    
    def test_project_personnel_report_serializer(self):
        """Test ProjectPersonalReportSerializer."""
        personnel = ProjectPersonnel.objects.create(
            contractid=self.contract,
            dateid=self.date,
            dpno=10,
            dcpno=5,
            mepno=8
        )
        
        serializer = ProjectPersonalReportSerializer(personnel)
        data = serializer.data
        
        self.assertIn('persianMonth', data)
        self.assertEqual(data['persianMonth'], 'اردیبهشت')


class ProblemSerializerTest(TestCase):
    """Test Problem serializer."""
    
    def test_serialization(self):
        """Test Problem serialization."""
        contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        date = ReportDate.objects.create(year='1403', month='01')
        
        problem = Problem.objects.create(
            contractid=contract,
            dateid=date,
            problem="Test problem description"
        )
        
        serializer = ProblemSerializer(problem)
        data = serializer.data
        
        self.assertEqual(data['problem'], "Test problem description")
        self.assertIn('contractid', data)
        self.assertIn('dateid', data)


class CriticalActionSerializerTest(TestCase):
    """Test CriticalAction serializer."""
    
    def test_serialization(self):
        """Test CriticalAction serialization."""
        contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        date = ReportDate.objects.create(year='1403', month='01')
        
        action = CriticalAction.objects.create(
            contractid=contract,
            dateid=date,
            criticalaction="Test critical action"
        )
        
        serializer = CriticalActionSerializer(action)
        data = serializer.data
        
        self.assertEqual(data['criticalaction'], "Test critical action")
        self.assertIn('contractid', data)
        self.assertIn('dateid', data)


# Run tests with: python manage.py test projects.tests.test_serializers