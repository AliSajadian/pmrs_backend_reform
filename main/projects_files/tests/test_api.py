"""
Tests for projects_files API views.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock

from contracts.models import Contract, Company
from projects.models import ReportDate
from accounts.models import UserRole, Role
from projects_files.models import (
    HseReportDox, ProjectDox, ContractorDox, ProjectMonthlyDox,
    InvoiceDox, Zone, ZoneImage, ReportVisit
)


User = get_user_model()


class HseReportDoxAPITest(TestCase):
    """Test cases for HseReportDox API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )

        self.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=self.company,
            contractType=1
        )

        self.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )

        self.hse_doc = HseReportDox.objects.create(
            contractid=self.contract,
            dateid=self.report_date,
            description='Test HSE Report',
            active=True
        )

    def test_list_hse_documents(self):
        """Test listing HSE documents."""
        response = self.client.get('/api/hse-reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_hse_document(self):
        """Test creating HSE document."""
        data = {
            'contractid': self.contract.pk,
            'dateid': self.report_date.pk,
            'description': 'New HSE Report',
            'active': True
        }
        response = self.client.post('/api/hse-reports/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_access(self):
        """Test unauthorized access is denied."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/hse-reports/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProjectDoxAPITest(TestCase):
    """Test cases for ProjectDox API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )

        self.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=self.company,
            contractType=1
        )

        self.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )

        self.project_doc = ProjectDox.objects.create(
            contractid=self.contract,
            dateid=self.report_date,
            doctitle=1,
            dockind=1,
            docno=1,
            active=True
        )

    def test_list_project_documents(self):
        """Test listing project documents."""
        response = self.client.get('/api/project-docs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_project_document(self):
        """Test creating project document."""
        data = {
            'contractid': self.contract.pk,
            'dateid': self.report_date.pk,
            'doctitle': 2,
            'dockind': 1,
            'docno': 2,
            'active': True
        }
        response = self.client.post('/api/project-docs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_project_document(self):
        """Test retrieving a single project document."""
        response = self.client.get(f'/api/project-docs/{self.project_doc.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['doctitle'], 1)


class ZoneAPITest(TestCase):
    """Test cases for Zone API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )

        self.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=self.company,
            contractType=1
        )

        self.zone = Zone.objects.create(
            contractid=self.contract,
            zone='Zone A'
        )

    def test_list_zones(self):
        """Test listing zones."""
        response = self.client.get('/api/zones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_zone(self):
        """Test retrieving a single zone."""
        response = self.client.get(f'/api/zones/{self.zone.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['zone'], 'Zone A')


class ZoneImagesAPITest(TestCase):
    """Test cases for ZoneImages API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )

        self.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=self.company,
            contractType=1
        )

        self.zone = Zone.objects.create(
            contractid=self.contract,
            zone='Zone A'
        )

        self.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )

        self.zone_image = ZoneImage.objects.create(
            zoneid=self.zone,
            dateid=self.report_date,
            ppp=Decimal('75.50'),
            app=Decimal('80.25'),
            description1='Progress image 1'
        )

    @patch('projects_files.api.ZoneImageService.create_zone_image')
    def test_create_zone_image(self, mock_create):
        """Test creating zone image via API."""
        mock_create.return_value = self.zone_image

        data = {
            'contractid': self.contract.pk,
            'zone': 'Zone A',
            'dateid': self.report_date.pk,
            'ppp': '75.50',
            'app': '80.25',
            'description1': 'New progress image',
            'description2': '',
            'description3': ''
        }

        response = self.client.post('/api/zone-images/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    @patch('projects_files.api.ZoneImageService.update_zone_image')
    def test_update_zone_image(self, mock_update):
        """Test updating zone image via API."""
        mock_update.return_value = self.zone_image

        data = {
            'contractid': self.contract.pk,
            'zone': 'Zone A',
            'dateid': self.report_date.pk,
            'ppp': '80.00',
            'app': '85.00',
            'description1': 'Updated progress',
            'description2': '',
            'description3': ''
        }

        response = self.client.put(
            f'/api/zone-images/{self.zone_image.pk}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('projects_files.api.ZoneImageService.delete_zone_image')
    def test_delete_zone_image(self, mock_delete):
        """Test deleting zone image via API."""
        response = self.client.delete(f'/api/zone-images/{self.zone_image.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_delete.assert_called_once_with(self.zone_image.pk)


class GetContractZoneImagesAPITest(TestCase):
    """Test cases for getContractZoneImages API function."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )
        
        self.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=self.company,
            contractType=1
        )

        self.zone = Zone.objects.create(
            contractid=self.contract,
            zone='Zone A'
        )

        self.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )

        self.zone_image = ZoneImage.objects.create(
            zoneid=self.zone,
            dateid=self.report_date,
            ppp=Decimal('75.50'),
            app=Decimal('80.25')
        )

    @patch('projects_files.api.ZoneImageService.get_or_create_contract_zone_images')
    def test_get_contract_zone_images(self, mock_get_images):
        """Test getting contract zone images."""
        mock_get_images.return_value = ZoneImage.objects.filter(
            pk=self.zone_image.pk
        )
        
        data = {
            'userid': self.user.pk,
            'contractid': self.contract.pk,
            'dateid': self.report_date.pk,
            'reportid': 14
        }

        response = self.client.post(
            '/api/contract-zone-images/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        mock_get_images.assert_called_once_with(
            self.user.pk, self.contract.pk, self.report_date.pk, 14
        )


class ReportVisitAPITest(TestCase):
    """Test cases for ReportVisit API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.role = Role.objects.create(role='Board')

        self.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )

        self.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=self.company,
            contractType=1
        )

        self.user_role = UserRole.objects.create(
            userid=self.user,
            roleid=self.role,
            contractid=self.contract
        )

        self.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )

        self.report_visit = ReportVisit.objects.create(
            userid=self.user,
            contractid=self.contract,
            dateid=self.report_date,
            financialinfo=True
        )

    @patch('projects_files.api.ReportVisitService.get_contract_date_visits')
    def test_get_report_visits(self, mock_get_visits):
        """Test getting report visits."""
        mock_get_visits.return_value = ReportVisit.objects.filter(
            pk=self.report_visit.pk
        )

        response = self.client.get(
            f'/api/report-visits/{self.contract.pk}/{self.report_date.pk}/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    @patch('projects_files.api.ReportVisitService.create_report_visit')
    def test_create_report_visit(self, mock_create):
        """Test creating report visit."""
        mock_create.return_value = True

        data = {
            'contractid': self.contract.pk,
            'dateid': self.report_date.pk,
            'userid': self.user.pk,
            'reportid': 1
        }

        response = self.client.post(
            '/api/report-visits/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        mock_create.assert_called_once_with(
            self.contract.pk, self.report_date.pk, self.user.pk, 1
        )


class ContractorDoxAPITest(TestCase):
    """Test cases for ContractorDox API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )

        self.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=self.company,
            contractType=1
        )

        self.contractor_doc = ContractorDox.objects.create(
            contractid=self.contract,
            contractdate=timezone.now().date(),
            contracttitle='Contractor Agreement',
            contractor='XYZ Contractor',
            contractno='CONT-001',
            riderno=1
        )

    def test_list_contractor_documents(self):
        """Test listing contractor documents."""
        response = self.client.get('/api/contractor-docs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_contractor_document(self):
        """Test retrieving contractor document."""
        response = self.client.get(f'/api/contractor-docs/{self.contractor_doc.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contractor'], 'XYZ Contractor')


class ProjectMonthlyDoxAPITest(TestCase):
    """Test cases for ProjectMonthlyDox API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )

        self.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=self.company,
            contractType=1
        )

        self.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )

        self.monthly_doc = ProjectMonthlyDox.objects.create(
            contractid=self.contract,
            dateid=self.report_date,
            description='Monthly Report',
            active=True
        )

    def test_list_monthly_documents(self):
        """Test listing monthly documents."""
        response = self.client.get('/api/monthly-docs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_monthly_document(self):
        """Test creating monthly document."""
        data = {
            'contractid': self.contract.pk,
            'dateid': self.report_date.pk,
            'description': 'New Monthly Report',
            'active': True
        }
        response = self.client.post('/api/monthly-docs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ApprovedInvoiceDoxAPITest(TestCase):
    """Test cases for ApprovedInvoiceDox API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.company = Company.objects.create(
            company='Test Company',
            companyType=1
        )

        self.contract = Contract.objects.create(
            contract='Test Contract',
            number='CNT-001',
            companyid=self.company,
            contractType=1
        )

        self.report_date = ReportDate.objects.create(
            year=1403,
            month=9,
            date=timezone.now().date()
        )

        self.invoice = InvoiceDox.objects.create(
            contractid=self.contract,
            dateid=self.report_date,
            invoicekind=1,
            invoiceno=1001,
            invoicedate=timezone.now().date(),
            active=True
        )

    def test_list_invoice_documents(self):
        """Test listing invoice documents."""
        response = self.client.get('/api/invoices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_invoice_document(self):
        """Test retrieving invoice document."""
        response = self.client.get(f'/api/invoices/{self.invoice.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['invoiceno'], 1001)
