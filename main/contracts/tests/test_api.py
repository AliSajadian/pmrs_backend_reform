"""
Tests for the contracts application API views.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from contracts.models import (
    ContractType, Contract, Country, Currency, 
    Personeltype, Personel, Addendum, ContractConsultant,
    EpcCorporation
)
from accounts.models import UserRole

User = get_user_model()


class ContractTypeAPITest(TestCase):
    """Test cases for ContractTypeAPI."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC',
            description='Engineering, Procurement, and Construction'
        )

    def test_list_contract_types(self):
        """Test listing contract types."""
        url = reverse('contracttype-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_contract_type(self):
        """Test retrieving a single contract type."""
        url = reverse('contracttype-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contracttype'], 'EPC')

    def test_create_contract_type(self):
        """Test creating a new contract type."""
        url = reverse('contracttype-list')
        data = {
            'contracttypeid': 2,
            'contracttype': 'BOT',
            'description': 'Build Operate Transfer'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContractType.objects.count(), 2)

    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access the API."""
        self.client.force_authenticate(user=None)
        url = reverse('contracttype-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ContractAPITest(TestCase):
    """Test cases for ContractAPI."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.currency = Currency.objects.create(
            currencyid=1,
            currency='Rial'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type,
            currencyid=self.currency,
            contractamount_r=Decimal('1000000.00')
        )

    def test_list_contracts(self):
        """Test listing contracts."""
        url = reverse('contract-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_contract(self):
        """Test retrieving a single contract."""
        url = reverse('contract-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contract'], 'Test Contract')


class ContractAPIExTest(TestCase):
    """Test cases for ContractAPIEx."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.currency = Currency.objects.create(
            currencyid=1,
            currency='Rial'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type,
            currencyid=self.currency
        )
        
        UserRole.objects.create(
            userid=self.user,
            projectid=None
        )

    def test_get_user_contracts(self):
        """Test getting contracts for a user."""
        url = f'/api/contracts/user/{self.user.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)


class GetContractBaseInfoTest(TestCase):
    """Test cases for get_contract_base_info view."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.currency = Currency.objects.create(
            currencyid=1,
            currency='Rial'
        )
        self.personel = Personel.objects.create(
            personelid=1,
            firstname='Jane',
            lastname='Smith'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type,
            currencyid=self.currency,
            projectmanagerid=self.personel,
            contractamount_r=Decimal('1000000.00')
        )

    def test_get_contract_base_info_success(self):
        """Test successfully getting contract base info."""
        url = f'/api/contracts/{self.contract.contractid}/base-info/{1}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('contractInfo', response.data)
        self.assertIn('projectManagerConfirmed', response.data)

    def test_get_contract_base_info_not_found(self):
        """Test getting contract base info for non-existent contract."""
        url = f'/api/contracts/999/base-info/1/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateDateViewsTest(TestCase):
    """Test cases for date update views."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type
        )

    def test_put_start_operation_date(self):
        """Test updating start operation date."""
        url = f'/api/contracts/{self.contract.contractid}/start-operation-date/2024-01-15/'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        self.contract.refresh_from_db()
        self.assertEqual(
            self.contract.startoperationdate.strftime('%Y-%m-%d'),
            '2024-01-15'
        )

    def test_put_notification_date(self):
        """Test updating notification date."""
        url = f'/api/contracts/{self.contract.contractid}/notification-date/2024-01-20/'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_put_plan_start_date(self):
        """Test updating plan start date."""
        url = f'/api/contracts/{self.contract.contractid}/plan-start-date/2024-02-01/'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_put_finish_date(self):
        """Test updating finish date."""
        url = f'/api/contracts/{self.contract.contractid}/finish-date/2024-12-31/'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class ContractInfoAPITest(TestCase):
    """Test cases for ContractInfoAPI."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type
        )
        self.consultant = ContractConsultant.objects.create(
            consultantid=1,
            contractid=self.contract,
            consultant='ABC Consulting'
        )
        self.epc = EpcCorporation.objects.create(
            epccorporationid=1,
            contractid=self.contract
        )

    def test_get_consultant_info(self):
        """Test getting consultant info."""
        url = f'/api/contracts/{self.contract.contractid}/info/?type=consultant'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)

    def test_get_epc_info(self):
        """Test getting EPC corporation info."""
        url = f'/api/contracts/{self.contract.contractid}/info/?type=epc'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)

    def test_patch_contract_info(self):
        """Test updating contract info."""
        url = f'/api/contracts/{self.contract.contractid}/info/'
        data = {
            'location': 'Updated Location',
            'latitude': '35.6892',
            'longitude': '51.3890'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class GetContractConsultantTest(TestCase):
    """Test cases for get_contract_consultant view."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type
        )
        self.consultant = ContractConsultant.objects.create(
            consultantid=1,
            contractid=self.contract,
            consultant='ABC Consulting'
        )

    def test_get_contract_consultant_success(self):
        """Test getting contract consultant."""
        url = f'/api/contracts/{self.contract.contractid}/consultant/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIsInstance(response.data['data'], list)


class GetEpcCorporationTest(TestCase):
    """Test cases for get_epc_corporation view."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type
        )
        self.epc = EpcCorporation.objects.create(
            epccorporationid=1,
            contractid=self.contract
        )

    def test_get_epc_corporation_success(self):
        """Test getting EPC corporation."""
        url = f'/api/contracts/{self.contract.contractid}/epc/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIsInstance(response.data['data'], dict)


class ContractAddendumAPITest(TestCase):
    """Test cases for ContractAddendumAPI."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type
        )
        self.addendum = Addendum.objects.create(
            addendumid=1,
            contractid=self.contract,
            addendumamount_r=Decimal('100000.00'),
            afteraddendumdate=date.today() + timedelta(days=30)
        )

    def test_list_addendums(self):
        """Test listing addendums."""
        url = reverse('addendum-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_addendum(self):
        """Test retrieving a single addendum."""
        url = reverse('addendum-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['addendumamount_r'], '100000.00')

    def test_create_addendum(self):
        """Test creating a new addendum."""
        url = reverse('addendum-list')
        data = {
            'addendumid': 2,
            'contractid': self.contract.contractid,
            'addendumamount_r': '50000.00',
            'addendumamount_fc': '500.00',
            'afteraddendumdate': (date.today() + timedelta(days=60)).isoformat()
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Addendum.objects.count(), 2)


class CountryAPITest(TestCase):
    """Test cases for CountryAPI."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.country = Country.objects.create(
            countryid=1,
            country='Iran',
            code='IR'
        )

    def test_list_countries(self):
        """Test listing countries."""
        url = reverse('country-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CurrencyAPITest(TestCase):
    """Test cases for CurrencyAPI."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.currency = Currency.objects.create(
            currencyid=1,
            currency='Rial'
        )

    def test_list_currencies(self):
        """Test listing currencies."""
        url = reverse('currency-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class PersonelAPITest(TestCase):
    """Test cases for PersonelAPI."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.personel_type = Personeltype.objects.create(
            personeltypeid=1,
            personeltype='Engineer'
        )
        self.personel = Personel.objects.create(
            personelid=1,
            firstname='John',
            lastname='Doe',
            personeltypeid=self.personel_type
        )

    def test_list_personel(self):
        """Test listing personel."""
        url = reverse('personel-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)