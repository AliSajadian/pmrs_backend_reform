"""
Tests for projects_files models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from decimal import Decimal

from contracts.models import Contract, Company
from projects.models import ReportDate
from projects_files.models import (
    HseReportDox, ProjectDox, ContractorDox, ProjectMonthlyDox,
    InvoiceDox, ApprovedInvoiceDox, Zone, ZoneImage, ReportVisit,
    ReportVisitdate, ReportDox
)


User = get_user_model()


class HseReportDoxModelTest(TestCase):
    """Test cases for HseReportDox model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        # Create company
        cls.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )
        
        # Create contract
        cls.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=cls.company,
            contractType=1
        )
        
        # Create report date
        cls.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )
        
        # Create HSE report document
        cls.hse_doc = HseReportDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date,
            description='Test HSE Report',
            active=True
        )
    
    def test_hse_report_dox_creation(self):
        """Test HSE report document creation."""
        self.assertEqual(self.hse_doc.description, 'Test HSE Report')
        self.assertEqual(self.hse_doc.contractid, self.contract)
        self.assertTrue(self.hse_doc.active)
    
    def test_year_method(self):
        """Test year method returns correct year."""
        self.assertEqual(self.hse_doc.year(), 1403)
    
    def test_month_method(self):
        """Test month method returns correct month."""
        self.assertEqual(self.hse_doc.month(), 9)
    
    def test_filename_method_no_file(self):
        """Test filename method when no file exists."""
        self.assertEqual(self.hse_doc.filename(), '')
    
    def test_filename_method_with_file(self):
        """Test filename method with file."""
        # Create a simple uploaded file
        test_file = SimpleUploadedFile(
            "test_hse.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        self.hse_doc.file = test_file
        self.hse_doc.save()
        
        filename = self.hse_doc.filename()
        self.assertIn('test_hse', filename)


class ProjectDoxModelTest(TestCase):
    """Test cases for ProjectDox model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )
        
        cls.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=cls.company,
            contractType=1
        )
        
        cls.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )
        
        cls.project_doc = ProjectDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date,
            doctitle=1,
            dockind=1,
            docno=1,
            active=True
        )
    
    def test_project_dox_creation(self):
        """Test project document creation."""
        self.assertEqual(self.project_doc.contractid, self.contract)
        self.assertEqual(self.project_doc.doctitle, 1)
        self.assertTrue(self.project_doc.active)
    
    def test_filename_method(self):
        """Test filename method."""
        self.assertEqual(self.project_doc.filename(), '')


class ContractorDoxModelTest(TestCase):
    """Test cases for ContractorDox model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )
        
        cls.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=cls.company,
            contractType=1
        )
        
        cls.contractor_doc = ContractorDox.objects.create(
            contractid=cls.contract,
            contractdate=timezone.now().date(),
            contracttitle='Contractor Agreement',
            contractor='XYZ Contractor',
            contractno='CONT-001',
            riderno=1
        )
    
    def test_contractor_dox_creation(self):
        """Test contractor document creation."""
        self.assertEqual(self.contractor_doc.contracttitle, 'Contractor Agreement')
        self.assertEqual(self.contractor_doc.contractor, 'XYZ Contractor')
        self.assertEqual(self.contractor_doc.riderno, 1)
    
    def test_contractshamsidate_method(self):
        """Test contract shamsi date method."""
        shamsi_date = self.contractor_doc.contractshamsidate()
        self.assertIsInstance(shamsi_date, str)


class ZoneModelTest(TestCase):
    """Test cases for Zone model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )
        
        cls.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=cls.company,
            contractType=1
        )
        
        cls.zone = Zone.objects.create(
            contractid=cls.contract,
            zone='Zone A'
        )
    
    def test_zone_creation(self):
        """Test zone creation."""
        self.assertEqual(self.zone.zone, 'Zone A')
        self.assertEqual(self.zone.contractid, self.contract)


class ZoneImageModelTest(TestCase):
    """Test cases for ZoneImage model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )
        
        cls.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=cls.company,
            contractType=1
        )
        
        cls.zone = Zone.objects.create(
            contractid=cls.contract,
            zone='Zone A'
        )
        
        cls.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )
        
        cls.zone_image = ZoneImage.objects.create(
            zoneid=cls.zone,
            dateid=cls.report_date,
            ppp=Decimal('75.50'),
            app=Decimal('80.25'),
            description1='Progress image 1',
            description2='Progress image 2',
            description3='Progress image 3'
        )
    
    def test_zone_image_creation(self):
        """Test zone image creation."""
        self.assertEqual(self.zone_image.zoneid, self.zone)
        self.assertEqual(self.zone_image.ppp, Decimal('75.50'))
        self.assertEqual(self.zone_image.app, Decimal('80.25'))
    
    def test_zone_method(self):
        """Test zone method."""
        self.assertEqual(self.zone_image.zone(), 'Zone A')
    
    def test_contract_method(self):
        """Test contract method."""
        self.assertEqual(self.zone_image.contract(), 'Test Contract')
    
    def test_imagepath_methods(self):
        """Test image path methods."""
        self.assertEqual(self.zone_image.imagepath1(), '')
        self.assertEqual(self.zone_image.imagepath2(), '')
        self.assertEqual(self.zone_image.imagepath3(), '')
    
    def test_explanation_property(self):
        """Test explanation property."""
        explanation = self.zone_image.explanation
        self.assertIn('Test Contract', explanation)
        self.assertIn('Zone A', explanation)


class ReportVisitModelTest(TestCase):
    """Test cases for ReportVisit model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        cls.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )
        
        cls.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=cls.company,
            contractType=1
        )
        
        cls.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )
        
        cls.report_visit = ReportVisit.objects.create(
            userid=cls.user,
            contractid=cls.contract,
            dateid=cls.report_date,
            financialinfo=True,
            hse=True,
            progressstate=False
        )
    
    def test_report_visit_creation(self):
        """Test report visit creation."""
        self.assertEqual(self.report_visit.userid, self.user)
        self.assertTrue(self.report_visit.financialinfo)
        self.assertTrue(self.report_visit.hse)
        self.assertFalse(self.report_visit.progressstate)
    
    def test_manager_method(self):
        """Test manager method."""
        manager_name = self.report_visit.manager()
        self.assertEqual(manager_name, 'John Doe')
    
    def test_unique_together_constraint(self):
        """Test unique_together constraint."""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            ReportVisit.objects.create(
                userid=self.user,
                contractid=self.contract,
                dateid=self.report_date,
                financialinfo=False
            )


class InvoiceDoxModelTest(TestCase):
    """Test cases for InvoiceDox model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )
        
        cls.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=cls.company,
            contractType=1
        )
        
        cls.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )
        
        cls.invoice = InvoiceDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date,
            invoicekind=1,
            invoiceno=1001,
            invoicedate=timezone.now().date(),
            senddate=timezone.now().date(),
            confirmdate=timezone.now().date(),
            sgp_r=1000,
            sgp_fc=50000000,
            cgp_r=900,
            cgp_fc=45000000,
            description='Test Invoice',
            active=True
        )
    
    def test_invoice_dox_creation(self):
        """Test invoice document creation."""
        self.assertEqual(self.invoice.invoiceno, 1001)
        self.assertEqual(self.invoice.sgp_r, 1000)
        self.assertTrue(self.invoice.active)
    
    def test_shamsi_date_methods(self):
        """Test shamsi date conversion methods."""
        invoice_shamsi = self.invoice.invoiceshamsidate()
        send_shamsi = self.invoice.sendshamsidate()
        confirm_shamsi = self.invoice.confirmshamsidate()
        
        self.assertIsInstance(invoice_shamsi, str)
        self.assertIsInstance(send_shamsi, str)
        self.assertIsInstance(confirm_shamsi, str)