"""
Unit tests for projects services.
Tests business logic without HTTP overhead.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from projects.services import (
    FinancialInfoService, 
    ReportConfirmService,
    WorkVolumeService,
    MachineryService
)
from projects.models import (
    FinancialInfo, Contract, ReportDate, 
    Invoice, ReportConfirm, WorkVolume, Machinary
)


class FinancialInfoServiceTest(TestCase):
    """Test FinancialInfoService business logic."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract',
            iscompleted=False
        )
        self.date = ReportDate.objects.create(
            year='1403',
            month='01'
        )
    
    @patch('projects.services.SetReportVisit')
    def test_get_or_create_financial_info_creates_new_record(self, mock_visit):
        """Test that financial info is created when it doesn't exist."""
        # Arrange
        self.assertFalse(
            FinancialInfo.objects.filter(
                contractid=self.contract,
                dateid=self.date
            ).exists()
        )
        
        # Act
        result = FinancialInfoService.get_or_create_financial_info(
            user_id=self.user.pk,
            contract_id=self.contract.pk,
            date_id=self.date.pk,
            report_id=1
        )
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.contractid, self.contract)
        self.assertEqual(result.dateid, self.date)
        mock_visit.assert_called_once_with(
            self.user.pk, self.contract.pk, self.date.pk, 1
        )
    
    @patch('projects.services.SetReportVisit')
    def test_get_or_create_financial_info_returns_existing_record(self, mock_visit):
        """Test that existing financial info is returned without creating new."""
        # Arrange
        existing = FinancialInfo.objects.create(
            contractid=self.contract,
            dateid=self.date
        )
        
        # Act
        result = FinancialInfoService.get_or_create_financial_info(
            user_id=self.user.pk,
            contract_id=self.contract.pk,
            date_id=self.date.pk,
            report_id=1
        )
        
        # Assert
        self.assertEqual(result.financialinfoid, existing.financialinfoid)
        self.assertEqual(FinancialInfo.objects.count(), 1)
    
    def test_update_financial_info_updates_all_fields(self):
        """Test that all financial info fields are updated correctly."""
        # Arrange
        financial_info = FinancialInfo.objects.create(
            contractid=self.contract,
            dateid=self.date,
            lastclaimedinvoice_r=1000,
            lastverifiedinvoice_r=800
        )
        
        data = {
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'lastclaimedinvoice_r': 5000,
            'lastclaimedinvoice_fc': 100,
            'lci_no': 5,
            'lastverifiedinvoice_r': 4500,
            'lastverifiedinvoice_fc': 90,
            'lvi_no': 4,
            'lastclaimedadjustmentinvoice_r': 200,
            'lastclaimedadjustmentinvoice_fc': 20,
            'lcai_no': 2,
            'lastverifiedadjustmentinvoice_r': 180,
            'lastverifiedadjustmentinvoice_fc': 18,
            'lvai_no': 2,
            'lastclaimedextraworkinvoice_r': 300,
            'lastclaimedextraworkinvoice_fc': 30,
            'lcewi_no': 3,
            'lastverifiedextraworkinvoice_r': 280,
            'lastverifiedextraworkinvoice_fc': 28,
            'lvewi_no': 3,
            'lastclaimbill_r': 6000,
            'lastclaimbill_fc': 120,
            'lcb_no': 6,
            'lastclaimbillverified_r': 5500,
            'lastclaimbillverified_fc': 110,
            'lcbv_no': 5,
            'lastclaimbillrecievedamount_r': 5000,
            'lastclaimbillrecievedamount_fc': 100,
            'cumulativeclientpayment_r': 5000,
            'cumulativeclientpayment_fc': 100,
            'clientprepaymentdeferment_r': 500,
            'clientprepaymentdeferment_fc': 10,
            'estcost_r': 10000,
            'estcost_fc': 200,
            'estclientpayment_r': 9000,
            'estclientpayment_fc': 180,
            'estdebitcredit_r': 1000,
            'estdebitcredit_fc': 20,
        }
        
        # Act
        result = FinancialInfoService.update_financial_info(
            financial_info.financialinfoid, data
        )
        
        # Assert
        self.assertEqual(result.lastclaimedinvoice_r, 5000)
        self.assertEqual(result.lastverifiedinvoice_r, 4500)
        self.assertEqual(result.lci_no, 5)
        self.assertEqual(result.estcost_r, 10000)
    
    def test_update_financial_info_updates_related_invoices(self):
        """Test that related invoices are updated when financial info changes."""
        # Arrange
        financial_info = FinancialInfo.objects.create(
            contractid=self.contract,
            dateid=self.date
        )
        invoice_r = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=True
        )
        invoice_fc = Invoice.objects.create(
            contractid=self.contract,
            dateid=self.date,
            r=False
        )
        
        data = {
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'lastverifiedinvoice_r': 4500,
            'lastverifiedinvoice_fc': 90,
            'lastclaimedinvoice_r': 5000,
            'lastclaimedinvoice_fc': 100,
            'lastverifiedadjustmentinvoice_r': 180,
            'lastverifiedadjustmentinvoice_fc': 18,
            'lastclaimedadjustmentinvoice_r': 200,
            'lastclaimedadjustmentinvoice_fc': 20,
            'lastverifiedextraworkinvoice_r': 280,
            'lastverifiedextraworkinvoice_fc': 28,
            'lastclaimedextraworkinvoice_r': 300,
            'lastclaimedextraworkinvoice_fc': 30,
            # ... other fields with default 0
            'lci_no': 0, 'lvi_no': 0, 'lcai_no': 0, 'lvai_no': 0,
            'lcewi_no': 0, 'lvewi_no': 0, 'lcb_no': 0, 'lcbv_no': 0,
            'lastclaimbill_r': 0, 'lastclaimbill_fc': 0,
            'lastclaimbillverified_r': 0, 'lastclaimbillverified_fc': 0,
            'lastclaimbillrecievedamount_r': 0, 'lastclaimbillrecievedamount_fc': 0,
            'cumulativeclientpayment_r': 0, 'cumulativeclientpayment_fc': 0,
            'clientprepaymentdeferment_r': 0, 'clientprepaymentdeferment_fc': 0,
            'estcost_r': 0, 'estcost_fc': 0,
            'estclientpayment_r': 0, 'estclientpayment_fc': 0,
            'estdebitcredit_r': 0, 'estdebitcredit_fc': 0,
        }
        
        # Act
        FinancialInfoService.update_financial_info(
            financial_info.financialinfoid, data
        )
        
        # Assert
        invoice_r.refresh_from_db()
        invoice_fc.refresh_from_db()
        
        self.assertEqual(invoice_r.aci_n_r, 4500)
        self.assertEqual(invoice_r.icc_n_r, 5000)
        self.assertEqual(invoice_fc.aci_n_fc, 90)
        self.assertEqual(invoice_fc.icc_n_fc, 100)


class ReportConfirmServiceTest(TestCase):
    """Test ReportConfirmService business logic."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(
            year='1403',
            month='01'
        )
    
    def test_get_confirmed_reports_returns_confirmed_only(self):
        """Test that only confirmed reports are returned."""
        # Arrange
        ReportConfirm.objects.create(
            contractid=self.contract,
            dateid=self.date,
            userid=self.user,
            type=1,
            user_c=1
        )
        ReportConfirm.objects.create(
            contractid=self.contract,
            dateid=self.date,
            userid=self.user,
            type=2,
            user_c=0  # Not confirmed
        )
        
        # Act
        result = ReportConfirmService.get_confirmed_reports(
            self.contract.pk, self.date.pk
        )
        
        # Assert
        self.assertEqual(result.count(), 1)
    
    def test_project_manager_confirm_updates_all_records(self):
        """Test that PM confirmation updates all 15 report types."""
        # Arrange
        for i in range(1, 16):
            ReportConfirm.objects.create(
                contractid=self.contract,
                dateid=self.date,
                userid=self.user,
                type=i,
                pm_c=0
            )
        
        # Act
        result = ReportConfirmService.project_manager_confirm(
            self.contract.pk, self.date.pk, 1
        )
        
        # Assert
        self.assertIsNotNone(result)
        confirmed_count = ReportConfirm.objects.filter(
            contractid=self.contract,
            dateid=self.date,
            pm_c=1
        ).count()
        self.assertEqual(confirmed_count, 15)
    
    def test_project_manager_confirm_returns_none_if_not_15_records(self):
        """Test that PM confirmation fails if not exactly 15 records exist."""
        # Arrange - Create only 10 records
        for i in range(1, 11):
            ReportConfirm.objects.create(
                contractid=self.contract,
                dateid=self.date,
                userid=self.user,
                type=i
            )
        
        # Act
        result = ReportConfirmService.project_manager_confirm(
            self.contract.pk, self.date.pk, 1
        )
        
        # Assert
        self.assertIsNone(result)
    
    def test_coordinator_confirm_creates_new_record_if_not_exists(self):
        """Test that coordinator confirmation creates new record."""
        # Arrange
        self.assertFalse(
            ReportConfirm.objects.filter(
                contractid=self.contract,
                dateid=self.date,
                type=5
            ).exists()
        )
        
        # Act
        result = ReportConfirmService.coordinator_confirm(
            self.contract.pk, self.date.pk, self.user.pk, 1, 5
        )
        
        # Assert
        self.assertTrue(
            ReportConfirm.objects.filter(
                contractid=self.contract,
                dateid=self.date,
                type=5,
                user_c=1
            ).exists()
        )


class WorkVolumeServiceTest(TestCase):
    """Test WorkVolumeService business logic."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date1 = ReportDate.objects.create(year='1403', month='01')
        self.date2 = ReportDate.objects.create(year='1403', month='02')
    
    @patch('projects.services.SetReportVisit')
    def test_get_or_create_work_volumes_creates_default_types(self, mock_visit):
        """Test that default work volume types are created."""
        # Act
        result = WorkVolumeService.get_or_create_work_volumes(
            self.user.pk, self.contract.pk, self.date1.pk, 7
        )
        
        # Assert
        self.assertEqual(result.count(), 6)  # 6 default work types
        work_types = list(result.values_list('work', flat=True))
        self.assertIn("خاکبرداری(متر مکعب)", work_types)
        self.assertIn("بتن ریزی(متر مکعب)", work_types)
    
    @patch('projects.services.SetReportVisit')
    def test_get_or_create_work_volumes_copies_from_previous_month(self, mock_visit):
        """Test that work volumes are copied from previous month."""
        # Arrange - Create work volumes for date1
        WorkVolume.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            work="Custom Work Type",
            planestimate=100,
            totalestimate=200,
            executedsofar=50
        )
        
        # Act - Get work volumes for date2 (should copy from date1)
        result = WorkVolumeService.get_or_create_work_volumes(
            self.user.pk, self.contract.pk, self.date2.pk, 7
        )
        
        # Assert
        copied_volume = result.filter(work="Custom Work Type").first()
        self.assertIsNotNone(copied_volume)
        self.assertEqual(copied_volume.planestimate, 100)
        self.assertEqual(copied_volume.totalestimate, 200)
        self.assertEqual(copied_volume.executedsofar, 50)


class MachineryServiceTest(TestCase):
    """Test MachineryService business logic."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date1 = ReportDate.objects.create(year='1403', month='01')
        self.date2 = ReportDate.objects.create(year='1403', month='02')
    
    @patch('projects.services.SetReportVisit')
    def test_get_or_create_machinery_creates_total_field(self, mock_visit):
        """Test that total field is automatically created and calculated."""
        # Arrange - Create machinery records
        Machinary.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            machine="تاور کرین",
            activeno=5,
            inactiveno=2
        )
        Machinary.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            machine="بولدوزر",
            activeno=3,
            inactiveno=1
        )
        
        # Act
        result = MachineryService.get_or_create_machinery(
            self.user.pk, self.contract.pk, self.date2.pk, 10
        )
        
        # Assert
        total = result.filter(machine="جمع کل").first()
        self.assertIsNotNone(total)
        self.assertEqual(total.priority, 1)
    
    @patch('projects.services.SetReportVisit')
    def test_get_or_create_machinery_calculates_totals_correctly(self, mock_visit):
        """Test that machinery totals are calculated correctly."""
        # Arrange
        Machinary.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            machine="تاور کرین",
            activeno=5,
            inactiveno=2
        )
        Machinary.objects.create(
            contractid=self.contract,
            dateid=self.date1,
            machine="بولدوزر",
            activeno=3,
            inactiveno=1
        )
        
        # Act
        MachineryService.get_or_create_machinery(
            self.user.pk, self.contract.pk, self.date1.pk, 10
        )
        
        # Assert
        total = Machinary.objects.get(
            contractid=self.contract,
            dateid=self.date1,
            machine="جمع کل"
        )
        self.assertEqual(total.activeno, 8)  # 5 + 3
        self.assertEqual(total.inactiveno, 3)  # 2 + 1


# Run tests with: python manage.py test projects.tests.test_services