"""
Tests for projects_files services.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from unittest.mock import Mock, patch

from contracts.models import Contract, Company
from projects.models import ReportDate
from accounts.models import UserRole, Role
from projects_files.models import (
    HseReportDox, ProjectDox, ContractorDox, ProjectMonthlyDox,
    InvoiceDox, Zone, ZoneImage, ReportVisit
)
from projects_files.services import (
    FileDownloadService, HseReportDoxService, ProjectDoxService,
    ContractorDoxService, ProjectMonthlyDoxService, ApprovedInvoiceDoxService,
    ZoneService, ZoneImageService, ReportVisitService
)


User = get_user_model()


class FileDownloadServiceTest(TestCase):
    """Test cases for FileDownloadService."""
    
    def test_create_file_response_with_no_file(self):
        """Test creating file response when file doesn't exist."""
        response = FileDownloadService.create_file_response(None, 'test.pdf')
        self.assertIsNone(response)
    
    @patch('projects_files.services.FileResponse')
    def test_create_file_response_with_file(self, mock_file_response):
        """Test creating file response with valid file."""
        # Create a mock file object
        mock_file = Mock()
        mock_file.storage = Mock()
        mock_file.path = 'path/to/file.pdf'
        mock_file.size = 1024
        mock_file.storage.open.return_value = Mock()
        
        response = FileDownloadService.create_file_response(mock_file, 'test.pdf')
        
        # Verify FileResponse was called
        mock_file_response.assert_called_once()


class HseReportDoxServiceTest(TestCase):
    """Test cases for HseReportDoxService."""
    
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
        
        cls.hse_doc1 = HseReportDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date,
            description='HSE Report 1',
            active=True
        )
        
        cls.hse_doc2 = HseReportDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date,
            description='HSE Report 2',
            active=True
        )
    
    def test_get_contract_documents(self):
        """Test getting all HSE documents for a contract."""
        documents = HseReportDoxService.get_contract_documents(self.contract.pk)
        self.assertEqual(documents.count(), 2)
        self.assertIn(self.hse_doc1, documents)
        self.assertIn(self.hse_doc2, documents)
    
    def test_get_document_for_download(self):
        """Test getting specific document for download."""
        document = HseReportDoxService.get_document_for_download(self.hse_doc1.pk)
        self.assertEqual(document, self.hse_doc1)
        self.assertEqual(document.description, 'HSE Report 1')


class ProjectDoxServiceTest(TestCase):
    """Test cases for ProjectDoxService."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
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
        
        cls.report_date1 = ReportDate.objects.create(
            year=1403,
            month=8,
            date=timezone.now().date()
        )
        
        cls.report_date2 = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )
        
        cls.project_doc1 = ProjectDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date1,
            doctitle=1,
            active=True
        )
        
        cls.project_doc2 = ProjectDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date2,
            doctitle=2,
            active=True
        )
    
    @patch('projects_files.services.ReportVisitService.set_report_visit')
    def test_get_contract_documents(self, mock_set_visit):
        """Test getting project documents up to a specific date."""
        documents = ProjectDoxService.get_contract_documents(
            self.user.pk, self.contract.pk, self.report_date2.pk, 15
        )
        
        # Should include both documents (dateid <= report_date2)
        self.assertEqual(documents.count(), 2)
        
        # Verify report visit was set
        mock_set_visit.assert_called_once_with(
            self.user.pk, self.contract.pk, self.report_date2.pk, 15
        )


class ZoneServiceTest(TestCase):
    """Test cases for ZoneService."""
    
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
    
    def test_get_contract_zones(self):
        """Test getting all zones for a contract."""
        zones = ZoneService.get_contract_zones(self.contract.pk)
        self.assertEqual(zones.count(), 1)
        self.assertEqual(zones.first().zone, 'Zone A')
    
    def test_get_or_create_zone_existing(self):
        """Test getting existing zone."""
        zone = ZoneService.get_or_create_zone(self.contract.pk, 'Zone A')
        self.assertEqual(zone, self.zone)
        # Should not create a new zone
        self.assertEqual(Zone.objects.count(), 1)
    
    def test_get_or_create_zone_new(self):
        """Test creating new zone."""
        zone = ZoneService.get_or_create_zone(self.contract.pk, 'Zone B')
        self.assertIsNotNone(zone)
        self.assertEqual(zone.zone, 'Zone B')
        # Should now have 2 zones
        self.assertEqual(Zone.objects.count(), 2)


class ZoneImageServiceTest(TestCase):
    """Test cases for ZoneImageService."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
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
        
        cls.zone = Zone.objects.create(
            contractid=cls.contract,
            zone='Zone A'
        )
        
        cls.report_date1 = ReportDate.objects.create(
            dateid=1,
            year=1403,
            month=8,
            date=timezone.now().date()
        )
        
        cls.report_date2 = ReportDate.objects.create(
            dateid=2,
            year=1403,
            month=9,
            date=timezone.now().date()
        )
        
        cls.zone_image = ZoneImage.objects.create(
            zoneid=cls.zone,
            dateid=cls.report_date1,
            ppp=Decimal('75.50'),
            app=Decimal('80.25'),
            description1='Test'
        )
    
    def test_create_zone_image(self):
        """Test creating a new zone image."""
        zone_image = ZoneImageService.create_zone_image(
            self.contract.pk,
            'Zone A',
            self.report_date2.pk,
            Decimal('85.00'),
            Decimal('90.00'),
            None, 'New desc 1',
            None, 'New desc 2',
            None, 'New desc 3'
        )
        
        self.assertIsNotNone(zone_image)
        self.assertEqual(zone_image.ppp, Decimal('85.00'))
        self.assertEqual(zone_image.app, Decimal('90.00'))
        self.assertEqual(zone_image.description1, 'New desc 1')
    
    def test_update_zone_image(self):
        """Test updating an existing zone image."""
        updated_image = ZoneImageService.update_zone_image(
            self.zone_image.pk,
            self.contract.pk,
            'Zone A',
            self.report_date1.pk,
            Decimal('80.00'),
            Decimal('85.00'),
            None, 'Updated desc 1',
            None, 'Updated desc 2',
            None, 'Updated desc 3'
        )
        
        self.assertEqual(updated_image.ppp, Decimal('80.00'))
        self.assertEqual(updated_image.app, Decimal('85.00'))
        self.assertEqual(updated_image.description1, 'Updated desc 1')
    
    def test_delete_zone_image(self):
        """Test deleting a zone image."""
        image_id = self.zone_image.pk
        zone_id = self.zone_image.zoneid.pk
        
        ZoneImageService.delete_zone_image(image_id)
        
        # Image should be deleted
        self.assertFalse(ZoneImage.objects.filter(pk=image_id).exists())
        
        # Zone should also be deleted since it has no more images
        self.assertFalse(Zone.objects.filter(pk=zone_id).exists())
    
    def test_delete_zone_image_keeps_zone_with_other_images(self):
        """Test deleting image doesn't delete zone if other images exist."""
        # Create another image for the same zone
        zone_image2 = ZoneImage.objects.create(
            zoneid=self.zone,
            dateid=self.report_date2,
            ppp=Decimal('70.00'),
            app=Decimal('75.00')
        )
        
        zone_id = self.zone.pk
        
        # Delete first image
        ZoneImageService.delete_zone_image(self.zone_image.pk)
        
        # Zone should still exist
        self.assertTrue(Zone.objects.filter(pk=zone_id).exists())
        # Second image should still exist
        self.assertTrue(ZoneImage.objects.filter(pk=zone_image2.pk).exists())


class ReportVisitServiceTest(TestCase):
    """Test cases for ReportVisitService."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        cls.role = Role.objects.create(
            role='Board'
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
        
        cls.user_role = UserRole.objects.create(
            userid=cls.user,
            roleid=cls.role,
            contractid=cls.contract
        )
        
        cls.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )
    
    def test_get_contract_date_visits(self):
        """Test getting report visits for a contract and date."""
        # Create a report visit
        ReportVisit.objects.create(
            userid=self.user,
            contractid=self.contract,
            dateid=self.report_date,
            financialinfo=True
        )
        
        visits = ReportVisitService.get_contract_date_visits(
            self.contract.pk, self.report_date.pk
        )
        
        self.assertEqual(visits.count(), 1)
        self.assertTrue(visits.first().financialinfo)
    
    def test_set_report_visit_single_contract(self):
        """Test setting report visit for a single contract."""
        result = ReportVisitService.set_report_visit(
            self.user.pk, self.contract.pk, self.report_date.pk, 1
        )
        
        self.assertTrue(result)
        
        # Verify report visit was created
        visits = ReportVisit.objects.filter(
            userid=self.user,
            contractid=self.contract,
            dateid=self.report_date
        )
        self.assertEqual(visits.count(), 1)
        self.assertTrue(visits.first().financialinfo)
    
    def test_set_report_visit_non_manager(self):
        """Test setting report visit for non-manager returns False."""
        # Create user without Board role
        regular_user = User.objects.create_user(
            username='regularuser',
            password='testpass123'
        )
        
        result = ReportVisitService.set_report_visit(
            regular_user.pk, self.contract.pk, self.report_date.pk, 1
        )
        
        self.assertFalse(result)
    
    def test_create_report_visit(self):
        """Test create report visit entry point."""
        result = ReportVisitService.create_report_visit(
            self.contract.pk, self.report_date.pk, self.user.pk, 2
        )
        
        self.assertTrue(result)
        
        # Verify HSE report visit was created
        visit = ReportVisit.objects.get(
            userid=self.user,
            contractid=self.contract,
            dateid=self.report_date
        )
        self.assertTrue(visit.hse)


class ContractorDoxServiceTest(TestCase):
    """Test cases for ContractorDoxService."""
    
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
    
    def test_get_contract_documents(self):
        """Test getting contractor documents for a contract."""
        documents = ContractorDoxService.get_contract_documents(self.contract.pk)
        self.assertEqual(documents.count(), 1)
        self.assertEqual(documents.first().contractor, 'XYZ Contractor')
    
    def test_get_document_for_download(self):
        """Test getting specific contractor document."""
        document = ContractorDoxService.get_document_for_download(
            self.contractor_doc.pk
        )
        self.assertEqual(document, self.contractor_doc)


class ApprovedInvoiceDoxServiceTest(TestCase):
    """Test cases for ApprovedInvoiceDoxService."""
    
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
        
        cls.report_date1 = ReportDate.objects.create(
            year=1403,
            month=8,
            date=timezone.now().date()
        )
        
        cls.report_date2 = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )
        
        cls.invoice1 = InvoiceDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date1,
            invoicekind=1,
            invoiceno=1001,
            invoicedate=timezone.now().date(),
            active=True
        )
        
        cls.invoice2 = InvoiceDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date2,
            invoicekind=1,
            invoiceno=1002,
            invoicedate=timezone.now().date(),
            active=True
        )

    def test_get_contract_month_documents(self):
        """Test getting invoice documents up to a specific date."""
        documents = ApprovedInvoiceDoxService.get_contract_month_documents(
            self.contract.pk, self.report_date2.pk
        )
        
        # Should include both invoices
        self.assertEqual(documents.count(), 2)

    def test_get_document_for_download(self):
        """Test getting specific invoice document."""
        document = ApprovedInvoiceDoxService.get_document_for_download(
            self.invoice1.pk
        )
        self.assertEqual(document, self.invoice1)
        self.assertEqual(document.invoiceno, 1001)
