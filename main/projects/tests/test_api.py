"""
Integration tests for projects API views.
Tests HTTP request/response flow, authentication, and serialization.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from projects.models import (
    ReportDate, ReportConfirm, FinancialInfo, Hse, ProgressState,
    TimeprogressState, Invoice, FinancialInvoice, WorkVolume,
    PmsProgress, Budgetcost, Machinary, ProjectPersonnel,
    Problem, CriticalAction
)
from contracts.models import Contract


class ReportDateAPITest(APITestCase):
    """Test ReportDate API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        ReportDate.objects.create(year='1403', month='01')
        ReportDate.objects.create(year='1403', month='02')
    
    @patch('projects.services.ReportDateService.get_and_create_report_dates')
    def test_get_report_dates_returns_200(self, mock_service):
        """Test that GET endpoint returns 200 with data."""
        mock_service.return_value = ReportDate.objects.all()
        
        url = '/api/report-dates/'  # Adjust to your actual URL
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
    
    def test_get_report_dates_requires_authentication(self):
        """Test that endpoint requires authentication."""
        self.client.force_authenticate(user=None)
        
        url = '/api/report-dates/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReportConfirmAPITest(APITestCase):
    """Test ReportConfirm API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.ReportConfirmService.get_confirmed_reports')
    def test_get_confirmed_reports_returns_200(self, mock_service):
        """Test getting confirmed reports."""
        mock_service.return_value = ReportConfirm.objects.none()
        
        url = f'/api/report-confirm/getConfirmedReports/{self.contract.pk}/{self.date.pk}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
    
    @patch('projects.services.ReportConfirmService.project_manager_confirm')
    def test_project_manager_confirm_success(self, mock_service):
        """Test project manager confirmation."""
        # Create 15 report confirm records
        for i in range(1, 16):
            ReportConfirm.objects.create(
                contractid=self.contract,
                dateid=self.date,
                userid=self.user,
                type=i
            )
        
        mock_service.return_value = ReportConfirm.objects.filter(
            contractid=self.contract,
            dateid=self.date
        )
        
        url = '/api/report-confirm/projectManagerReportConfirm/'
        data = {
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'confirmed': 1
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
    
    @patch('projects.services.ReportConfirmService.coordinator_confirm')
    def test_coordinator_confirm_success(self, mock_service):
        """Test coordinator confirmation."""
        mock_service.return_value = ReportConfirm.objects.filter(
            contractid=self.contract,
            dateid=self.date
        )
        
        url = '/api/report-confirm/coordinatorReportConfirm/'
        data = {
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'userid': self.user.pk,
            'confirmed': 1,
            'type': 1
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class FinancialInfoAPITest(APITestCase):
    """Test FinancialInfo API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.FinancialInfoService.get_or_create_financial_info')
    def test_contract_month_list_returns_200(self, mock_service):
        """Test getting financial info for contract month."""
        financial_info = FinancialInfo.objects.create(
            contractid=self.contract,
            dateid=self.date
        )
        mock_service.return_value = financial_info
        
        url = '/api/financial-info/contractMonthList/'
        data = {
            'userid': self.user.pk,
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'reportid': 1
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
    
    @patch('projects.services.FinancialInfoService.update_financial_info')
    def test_update_financial_info_success(self, mock_service):
        """Test updating financial info."""
        financial_info = FinancialInfo.objects.create(
            contractid=self.contract,
            dateid=self.date
        )
        mock_service.return_value = financial_info
        
        url = f'/api/financial-info/updateFinancialInfo/{financial_info.pk}/'
        data = {
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'lastclaimedinvoice_r': 5000,
            'lastclaimedinvoice_fc': 100,
            'lci_no': 5
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class HseAPITest(APITestCase):
    """Test HSE API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.HseService.get_or_create_hse')
    def test_contract_month_list_returns_200(self, mock_service):
        """Test getting HSE for contract month."""
        hse = Hse.objects.create(
            contractid=self.contract,
            dateid=self.date,
            totaloperationdays=30
        )
        mock_service.return_value = hse
        
        url = '/api/hse/contractMonthList/'
        data = {
            'userid': self.user.pk,
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'reportid': 2
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class ProgressStateAPITest(APITestCase):
    """Test ProgressState API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.ProgressStateService.get_or_create_progress_state')
    def test_contract_month_list_returns_200(self, mock_service):
        """Test getting progress state for contract month."""
        progress_state = ProgressState.objects.create(
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
        mock_service.return_value = ProgressState.objects.filter(pk=progress_state.pk)
        
        url = f'/api/progress-state/{self.contract.pk}/contractMonthList/'
        data = {
            'userid': self.user.pk,
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'reportid': 3
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class WorkVolumeAPITest(APITestCase):
    """Test WorkVolume API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.WorkVolumeService.get_or_create_work_volumes')
    def test_contract_month_list_creates_default_volumes(self, mock_service):
        """Test that default work volumes are created."""
        work_volumes = [
            WorkVolume(
                contractid=self.contract,
                dateid=self.date,
                work="خاکبرداری(متر مکعب)"
            )
        ]
        mock_service.return_value = work_volumes
        
        url = f'/api/work-volume/{self.contract.pk}/contractMonthList/'
        data = {
            'userid': self.user.pk,
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'reportid': 7
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class MachineryAPITest(APITestCase):
    """Test Machinery API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.MachineryService.get_or_create_machinery')
    def test_contract_month_list_returns_machinery(self, mock_service):
        """Test getting machinery for contract month."""
        machinery = Machinary.objects.create(
            contractid=self.contract,
            dateid=self.date,
            machine="تاور کرین",
            activeno=5,
            inactiveno=2
        )
        mock_service.return_value = Machinary.objects.filter(pk=machinery.pk)
        
        url = f'/api/machinery/{self.contract.pk}/contractMonthList/'
        data = {
            'userid': self.user.pk,
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'reportid': 10
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class BudgetCostAPITest(APITestCase):
    """Test BudgetCost API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.BudgetCostService.set_admin_description')
    def test_set_admin_description_success(self, mock_service):
        """Test setting admin description."""
        budget = Budgetcost.objects.create(
            contractid=self.contract,
            dateid=self.date,
            bac_r=1000000
        )
        
        url = '/api/budget-cost/setAdminDescription/'
        data = {
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'description': 'Test description'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        mock_service.assert_called_once()


class ProjectPersonnelAPITest(APITestCase):
    """Test ProjectPersonnel API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.ProjectPersonnelService.get_or_create_project_personnel')
    def test_contract_month_list_returns_personnel(self, mock_service):
        """Test getting project personnel for contract month."""
        personnel = ProjectPersonnel.objects.create(
            contractid=self.contract,
            dateid=self.date,
            dpno=10,
            dcpno=5,
            mepno=8
        )
        mock_service.return_value = ProjectPersonnel.objects.filter(pk=personnel.pk)
        
        url = f'/api/project-personnel/{self.contract.pk}/contractMonthList/'
        data = {
            'userid': self.user.pk,
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'reportid': 11
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class ProblemAPITest(APITestCase):
    """Test Problem API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.ProblemService.get_problems')
    def test_contract_month_list_returns_problems(self, mock_service):
        """Test getting problems for contract month."""
        problem = Problem.objects.create(
            contractid=self.contract,
            dateid=self.date,
            problem="Test problem description"
        )
        mock_service.return_value = Problem.objects.filter(pk=problem.pk)
        
        url = f'/api/problem/{self.contract.pk}/contractMonthList/'
        data = {
            'userid': self.user.pk,
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'reportid': 12
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class CriticalActionAPITest(APITestCase):
    """Test CriticalAction API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract = Contract.objects.create(
            contract='TEST001',
            contracttitle='Test Contract'
        )
        self.date = ReportDate.objects.create(year='1403', month='01')
    
    @patch('projects.services.CriticalActionService.get_critical_actions')
    def test_contract_month_list_returns_actions(self, mock_service):
        """Test getting critical actions for contract month."""
        action = CriticalAction.objects.create(
            contractid=self.contract,
            dateid=self.date,
            criticalaction="Test critical action"
        )
        mock_service.return_value = CriticalAction.objects.filter(pk=action.pk)
        
        url = f'/api/critical-action/{self.contract.pk}/contractMonthList/'
        data = {
            'userid': self.user.pk,
            'contractid': self.contract.pk,
            'dateid': self.date.pk,
            'reportid': 13
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


# Run tests with: python manage.py test projects.tests.test_api