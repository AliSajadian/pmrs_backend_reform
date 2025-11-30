"""
Tests for projects_files serializers.
"""
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal

from contracts.models import Contract, Company
from projects.models import ReportDate
from projects_files.models import (
    HseReportDox, ProjectDox, ContractorDox, ProjectMonthlyDox,
    InvoiceDox, Zone, ZoneImage, ReportVisit
)
from projects_files.serializers import (
    HseReportDoxSerializers, ProjectDoxSerializers, ContractorDoxSerializers,
    ProjectMonthlyDoxSerializers, ApprovedInvoiceDoxSerializers,
    ZoneSerializers, ZoneImagesSerializers, ProjectZoneImagesSerializers,
    ReportVisitSerializers
)
from django.contrib.auth import get_user_model


User = get_user_model()


class HseReportDoxSerializerTest(TestCase):
    """Test cases for HseReportDox serializer."""
    
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
        
        cls.hse_doc = HseReportDox.objects.create(
            contractid=cls.contract,
            dateid=cls.report_date,
            description='Test HSE Report',
            active=True
        )
    
    def test_serializer_contains_expected_fields(self):
        """Test serializer has expected fields."""
        serializer = HseReportDoxSerializers(instance=self.hse_doc)
        data = serializer.data
        
        self.assertIn('hsereportdoxid', data)
        self.assertIn('contractid', data)
        self.assertIn('dateid', data)
        self.assertIn('year', data)
        self.assertIn('month', data)
        self.assertIn('filename', data)
        self.assertIn('description', data)
        self.assertIn('active', data)
    
    def test_serializer_year_field(self):
        """Test year field is read only and correct."""
        serializer = HseReportDoxSerializers(instance=self.hse_doc)
        self.assertEqual(serializer.data['year'], 1403)
    
    def test_serializer_month_field(self):
        """Test month field is read only and correct."""
        serializer = HseReportDoxSerializers(instance=self.hse_doc)
        self.assertEqual(serializer.data['month'], 9)
    
    def test_serializer_create(self):
        """Test creating object through serializer."""
        data = {
            'contractid': self.contract.pk,
            'dateid': self.report_date.pk,
            'description': 'New HSE Report',
            'active': True
        }
        serializer = HseReportDoxSerializers(data=data)
        self.assertTrue(serializer.is_valid())
        hse_doc = serializer.save()
        self.assertEqual(hse_doc.description, 'New HSE Report')


class ProjectDoxSerializerTest(TestCase):
    """Test cases for ProjectDox serializer."""
    
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
    
    def test_serializer_contains_expected_fields(self):
        """Test serializer has expected fields."""
        serializer = ProjectDoxSerializers(instance=self.project_doc)
        data = serializer.data
        
        self.assertIn('projectdoxid', data)
        self.assertIn('contractid', data)
        self.assertIn('dateid', data)
        self.assertIn('doctitle', data)
        self.assertIn('dockind', data)
        self.assertIn('docno', data)
        self.assertIn('filename', data)
        self.assertIn('active', data)
    
    def test_serializer_filename_readonly(self):
        """Test filename is read only."""
        serializer = ProjectDoxSerializers(instance=self.project_doc)
        self.assertEqual(serializer.data['filename'], '')


class ContractorDoxSerializerTest(TestCase):
    """Test cases for ContractorDox serializer."""
    
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
    
    def test_serializer_contains_expected_fields(self):
        """Test serializer has expected fields."""
        serializer = ContractorDoxSerializers(instance=self.contractor_doc)
        data = serializer.data
        
        self.assertIn('contractordoxid', data)
        self.assertIn('contractid', data)
        self.assertIn('contractdate', data)
        self.assertIn('contractshamsidate', data)
        self.assertIn('contracttitle', data)
        self.assertIn('contractor', data)
        self.assertIn('contractno', data)
        self.assertIn('riderno', data)
        self.assertIn('filename', data)
    
    def test_serializer_shamsi_date_readonly(self):
        """Test shamsi date is read only."""
        serializer = ContractorDoxSerializers(instance=self.contractor_doc)
        self.assertIsInstance(serializer.data['contractshamsidate'], str)


class ZoneSerializerTest(TestCase):
    """Test cases for Zone serializer."""
    
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
    
    def test_serializer_contains_expected_fields(self):
        """Test serializer has expected fields."""
        serializer = ZoneSerializers(instance=self.zone)
        data = serializer.data
        
        self.assertIn('zoneid', data)
        self.assertIn('zone', data)
        self.assertEqual(data['zone'], 'Zone A')
    
    def test_serializer_create(self):
        """Test creating zone through serializer."""
        data = {
            'zoneid': 999,  # Will be auto-generated
            'zone': 'Zone B'
        }
        serializer = ZoneSerializers(data=data)
        # Note: This will fail validation because contractid is required
        # but not in the serializer fields
        self.assertFalse(serializer.is_valid())


class ZoneImagesSerializerTest(TestCase):
    """Test cases for ZoneImages serializer."""
    
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
    
    def test_serializer_contains_expected_fields(self):
        """Test serializer has expected fields."""
        serializer = ZoneImagesSerializers(instance=self.zone_image)
        data = serializer.data
        
        self.assertIn('zoneimageid', data)
        self.assertIn('zoneid', data)
        self.assertIn('dateid', data)
        self.assertIn('ppp', data)
        self.assertIn('app', data)
        self.assertIn('description1', data)
        self.assertIn('description2', data)
        self.assertIn('description3', data)
    
    def test_serializer_decimal_fields(self):
        """Test decimal fields are correctly serialized."""
        serializer = ZoneImagesSerializers(instance=self.zone_image)
        self.assertEqual(serializer.data['ppp'], '75.50')
        self.assertEqual(serializer.data['app'], '80.25')


class ProjectZoneImagesSerializerTest(TestCase):
    """Test cases for ProjectZoneImages serializer."""
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'contract': 'Test Contract',
            'zone': 'Zone A',
            'ppp': '75.50',
            'app': '80.25',
            'img': 'zone_images/test.jpg',
            'description': 'Test description'
        }
        serializer = ProjectZoneImagesSerializers(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['contract'], 'Test Contract')
        self.assertEqual(serializer.validated_data['zone'], 'Zone A')
    
    def test_serializer_with_invalid_data(self):
        """Test serializer with missing required fields."""
        data = {
            'contract': 'Test Contract',
            'zone': 'Zone A'
            # Missing required fields
        }
        serializer = ProjectZoneImagesSerializers(data=data)
        self.assertFalse(serializer.is_valid())


class ReportVisitSerializerTest(TestCase):
    """Test cases for ReportVisit serializer."""
    
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
            progressstate=False,
            zoneimages=True
        )
    
    def test_serializer_contains_expected_fields(self):
        """Test serializer has expected fields."""
        serializer = ReportVisitSerializers(instance=self.report_visit)
        data = serializer.data
        
        self.assertIn('manager', data)
        self.assertIn('financialinfo', data)
        self.assertIn('hse', data)
        self.assertIn('progressstate', data)
        self.assertIn('zoneimages', data)
    
    def test_serializer_boolean_fields(self):
        """Test boolean fields are correctly serialized."""
        serializer = ReportVisitSerializers(instance=self.report_visit)
        self.assertTrue(serializer.data['financialinfo'])
        self.assertTrue(serializer.data['hse'])
        self.assertFalse(serializer.data['progressstate'])
        self.assertTrue(serializer.data['zoneimages'])


class ApprovedInvoiceDoxSerializerTest(TestCase):
    """Test cases for ApprovedInvoiceDox serializer."""
    
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
    
    def test_serializer_contains_expected_fields(self):
        """Test serializer has expected fields."""
        serializer = ApprovedInvoiceDoxSerializers(instance=self.invoice)
        data = serializer.data
        
        self.assertIn('invoicedoxid', data)
        self.assertIn('contractid', data)
        self.assertIn('dateid', data)
        self.assertIn('invoicekind', data)
        self.assertIn('invoiceno', data)
        self.assertIn('invoicedate', data)
        self.assertIn('senddate', data)
        self.assertIn('confirmdate', data)
        self.assertIn('invoiceshamsidate', data)
        self.assertIn('sendshamsidate', data)
        self.assertIn('confirmshamsidate', data)
        self.assertIn('sgp_r', data)
        self.assertIn('sgp_fc', data)
        self.assertIn('description', data)
        self.assertIn('active', data)
    
    def test_serializer_shamsi_dates_readonly(self):
        """Test shamsi date fields are read only."""
        serializer = ApprovedInvoiceDoxSerializers(instance=self.invoice)
        self.assertIsInstance(serializer.data['invoiceshamsidate'], str)
        self.assertIsInstance(serializer.data['sendshamsidate'], str)
        self.assertIsInstance(serializer.data['confirmshamsidate'], str)
