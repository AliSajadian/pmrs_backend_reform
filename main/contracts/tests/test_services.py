"""
Tests for the contracts application services.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from decimal import Decimal
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock

from contracts.models import (
    ContractType, Contract, Country, Currency, 
    Personeltype, Personel, Addendum, ContractConsultant,
    EpcCorporation
)
from accounts.models import UserRole
from projects.models import ReportConfirm
from contracts.services import ContractService

User = get_user_model()


class ContractServiceReadContractTest(TestCase):
    """Test cases for ContractService.read_contract method."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.currency = Currency.objects.create(
            currencyid=1,
            currency='Rial'
        )
        self.contract1 = Contract.objects.create(
            contractid=1,
            contract='Contract 1',
            contracttypeid=self.contract_type,
            currencyid=self.currency,
            startdate=date.today()
        )
        self.contract2 = Contract.objects.create(
            contractid=2,
            contract='Contract 2',
            contracttypeid=self.contract_type,
            currencyid=self.currency,
            startdate=date.today() - timedelta(days=30)
        )
        self.service = ContractService()

    def test_read_contract_for_user_with_all_contracts(self):
        """Test reading contracts for user with access to all contracts."""
        UserRole.objects.create(
            userid=self.user,
            projectid=None
        )
        
        result = self.service.read_contract(self.user.id)
        
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result, list)

    def test_read_contract_for_user_with_specific_contracts(self):
        """Test reading contracts for user with specific contract access."""
        UserRole.objects.create(
            userid=self.user,
            projectid=1
        )
        UserRole.objects.create(
            userid=self.user,
            contractid=self.contract1
        )
        
        result = self.service.read_contract(self.user.id)
        
        self.assertIsInstance(result, list)

    def test_read_contract_returns_serialized_data(self):
        """Test that read_contract returns properly serialized data."""
        UserRole.objects.create(
            userid=self.user,
            projectid=None
        )
        
        result = self.service.read_contract(self.user.id)
        
        # Check that result contains expected fields
        if result:
            self.assertIn('contractid', result[0])
            self.assertIn('contract', result[0])

    def test_read_contract_ordered_by_startdate(self):
        """Test that contracts are ordered by startdate descending."""
        UserRole.objects.create(
            userid=self.user,
            projectid=None
        )
        
        result = self.service.read_contract(self.user.id)
        
        # First contract should be the most recent
        self.assertEqual(result[0]['contractid'], 1)

    def test_read_contract_no_user_roles(self):
        """Test reading contracts when user has no roles."""
        result = self.service.read_contract(self.user.id)
        
        # Should return empty list or contracts based on implementation
        self.assertIsInstance(result, list)


class ContractServiceReadContractBaseInfoTest(TestCase):
    """Test cases for ContractService.read_contract_base_info method."""

    def setUp(self):
        """Set up test data."""
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
            contractamount_r=Decimal('1000000.00'),
            duration=365
        )
        self.service = ContractService()

    def test_read_contract_base_info_success(self):
        """Test successfully reading contract base info."""
        data, confirmed = self.service.read_contract_base_info(
            contract_id=1,
            date_id=1
        )
        
        self.assertIsInstance(data, dict)
        self.assertIsInstance(confirmed, bool)
        self.assertIn('contractid', data)
        self.assertIn('contract', data)
        self.assertEqual(data['contract'], 'Test Contract')

    def test_read_contract_base_info_not_found(self):
        """Test reading contract base info for non-existent contract."""
        with self.assertRaises(NotFound) as context:
            self.service.read_contract_base_info(
                contract_id=999,
                date_id=1
            )
        
        self.assertIn('999', str(context.exception))

    def test_read_contract_base_info_with_confirmed_report(self):
        """Test reading contract base info with confirmed report."""
        ReportConfirm.objects.create(
            contractid=self.contract,
            dateid=1,
            pm_c=1
        )
        
        data, confirmed = self.service.read_contract_base_info(
            contract_id=1,
            date_id=1
        )
        
        self.assertTrue(confirmed)

    def test_read_contract_base_info_without_confirmed_report(self):
        """Test reading contract base info without confirmed report."""
        data, confirmed = self.service.read_contract_base_info(
            contract_id=1,
            date_id=1
        )
        
        self.assertFalse(confirmed)

    def test_read_contract_base_info_with_zero_pm_c(self):
        """Test reading contract base info with pm_c = 0."""
        ReportConfirm.objects.create(
            contractid=self.contract,
            dateid=1,
            pm_c=0
        )
        
        data, confirmed = self.service.read_contract_base_info(
            contract_id=1,
            date_id=1
        )
        
        self.assertFalse(confirmed)

    def test_read_contract_base_info_returns_all_fields(self):
        """Test that all expected fields are in returned data."""
        data, confirmed = self.service.read_contract_base_info(
            contract_id=1,
            date_id=1
        )
        
        expected_fields = ['contractid', 'contract', 'contractamount_r', 'duration']
        for field in expected_fields:
            self.assertIn(field, data)


class ContractServiceReadContractConsultantTest(TestCase):
    """Test cases for ContractService.read_contract_consultant method."""

    def setUp(self):
        """Set up test data."""
        contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Main Contract',
            contracttypeid=contract_type
        )
        self.consultant1 = ContractConsultant.objects.create(
            consultantid=1,
            contractid=self.contract,
            consultant='ABC Consulting'
        )
        self.consultant2 = ContractConsultant.objects.create(
            consultantid=2,
            contractid=self.contract,
            consultant='XYZ Consulting'
        )
        self.service = ContractService()

    def test_read_contract_consultant_success(self):
        """Test successfully reading contract consultants."""
        result = self.service.read_contract_consultant(contract_id=1)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn('consultantid', result[0])
        self.assertIn('consultant', result[0])

    def test_read_contract_consultant_no_consultants(self):
        """Test reading consultants for contract with no consultants."""
        contract2 = Contract.objects.create(
            contractid=2,
            contract='Contract Without Consultants',
            contracttypeid=ContractType.objects.first()
        )
        
        result = self.service.read_contract_consultant(contract_id=2)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_read_contract_consultant_data_structure(self):
        """Test the structure of returned consultant data."""
        result = self.service.read_contract_consultant(contract_id=1)
        
        for consultant in result:
            self.assertIn('consultantid', consultant)
            self.assertIn('consultant', consultant)

    def test_read_contract_consultant_correct_values(self):
        """Test that correct consultant values are returned."""
        result = self.service.read_contract_consultant(contract_id=1)
        
        consultant_names = [c['consultant'] for c in result]
        self.assertIn('ABC Consulting', consultant_names)
        self.assertIn('XYZ Consulting', consultant_names)


class ContractServiceReadContractAddendumsTest(TestCase):
    """Test cases for ContractService.read_contract_addendums method."""

    def setUp(self):
        """Set up test data."""
        contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Main Contract',
            contracttypeid=contract_type
        )
        self.addendum1 = Addendum.objects.create(
            addendumid=1,
            contractid=self.contract,
            addendumamount_r=Decimal('100000.00'),
            afteraddendumdate=date.today() + timedelta(days=30)
        )
        self.addendum2 = Addendum.objects.create(
            addendumid=2,
            contractid=self.contract,
            addendumamount_r=Decimal('50000.00'),
            afteraddendumdate=date.today() + timedelta(days=60)
        )
        self.service = ContractService()

    def test_read_contract_addendums_success(self):
        """Test successfully reading contract addendums."""
        result = self.service.read_contract_addendums(contract_id=1)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn('addendumid', result[0])
        self.assertIn('addendumamount_r', result[0])

    def test_read_contract_addendums_no_addendums(self):
        """Test reading addendums for contract with no addendums."""
        contract2 = Contract.objects.create(
            contractid=2,
            contract='Contract Without Addendums',
            contracttypeid=ContractType.objects.first()
        )
        
        result = self.service.read_contract_addendums(contract_id=2)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_read_contract_addendums_data_structure(self):
        """Test the structure of returned addendum data."""
        result = self.service.read_contract_addendums(contract_id=1)
        
        for addendum in result:
            self.assertIn('addendumid', addendum)
            self.assertIn('addendumamount_r', addendum)
            self.assertIn('afteraddendumdate', addendum)


class ContractServiceReadEpcCorporationTest(TestCase):
    """Test cases for ContractService.read_epc_corporation method."""

    def setUp(self):
        """Set up test data."""
        contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Main Contract',
            contracttypeid=contract_type
        )
        self.epc = EpcCorporation.objects.create(
            epccorporationid=1,
            contractid=self.contract
        )
        self.service = ContractService()

    def test_read_epc_corporation_success(self):
        """Test successfully reading EPC corporation."""
        result = self.service.read_epc_corporation(contract_id=1)
        
        self.assertIsInstance(result, dict)
        self.assertIn('E', result)
        self.assertIn('P', result)
        self.assertIn('C', result)

    def test_read_epc_corporation_not_found(self):
        """Test reading EPC corporation for contract without one."""
        contract2 = Contract.objects.create(
            contractid=2,
            contract='Contract Without EPC',
            contracttypeid=ContractType.objects.first()
        )
        
        result = self.service.read_epc_corporation(contract_id=2)
        
        self.assertIsNone(result)

    def test_read_epc_corporation_structure(self):
        """Test the structure of returned EPC data."""
        result = self.service.read_epc_corporation(contract_id=1)
        
        self.assertEqual(set(result.keys()), {'E', 'P', 'C'})

    @patch('contracts.services.logger')
    def test_read_epc_corporation_logs_warning(self, mock_logger):
        """Test that warning is logged when EPC not found."""
        contract2 = Contract.objects.create(
            contractid=2,
            contract='Contract Without EPC',
            contracttypeid=ContractType.objects.first()
        )
        
        result = self.service.read_epc_corporation(contract_id=2)
        
        mock_logger.warning.assert_called_once()
        self.assertIsNone(result)


class ContractServiceUpdateContractBaseInfoTest(TestCase):
    """Test cases for ContractService.update_contract_base_info method."""

    def setUp(self):
        """Set up test data."""
        contract_type = ContractType.objects.create(
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
            contracttypeid=contract_type,
            currencyid=self.currency,
            contractamount_r=Decimal('1000000.00')
        )
        self.service = ContractService()

    def test_update_contract_base_info_success(self):
        """Test successfully updating contract base info."""
        update_data = {
            'location': 'Updated Location',
            'latitude': '35.6892',
            'longitude': '51.3890'
        }
        
        result = self.service.update_contract_base_info(
            contract_id=1,
            data=update_data
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('contractid', result)

    def test_update_contract_base_info_not_found(self):
        """Test updating contract base info for non-existent contract."""
        update_data = {'location': 'New Location'}
        
        with self.assertRaises(NotFound):
            self.service.update_contract_base_info(
                contract_id=999,
                data=update_data
            )

    def test_update_contract_base_info_partial_update(self):
        """Test partial update of contract base info."""
        update_data = {'location': 'New Location'}
        
        result = self.service.update_contract_base_info(
            contract_id=1,
            data=update_data
        )
        
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.location, 'New Location')

    def test_update_contract_base_info_returns_fresh_data(self):
        """Test that method returns fresh serialized data."""
        update_data = {'location': 'Fresh Location'}
        
        result = self.service.update_contract_base_info(
            contract_id=1,
            data=update_data
        )
        
        self.assertEqual(result['location'], 'Fresh Location')

    def test_update_contract_base_info_multiple_fields(self):
        """Test updating multiple fields at once."""
        update_data = {
            'location': 'Multi Update Location',
            'latitude': '35.6892',
            'longitude': '51.3890'
        }
        
        result = self.service.update_contract_base_info(
            contract_id=1,
            data=update_data
        )
        
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.location, 'Multi Update Location')


class ContractServiceUpdateDatesTest(TestCase):
    """Test cases for date update methods in ContractService."""

    def setUp(self):
        """Set up test data."""
        contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=contract_type
        )
        self.service = ContractService()

    def test_update_start_operation_date(self):
        """Test updating start operation date."""
        new_date = '2024-01-15'
        
        self.service.update_start_operation_date(
            contract_id=1,
            date=new_date
        )
        
        self.contract.refresh_from_db()
        self.assertEqual(
            self.contract.startoperationdate.strftime('%Y-%m-%d'),
            new_date
        )

    def test_update_notification_date(self):
        """Test updating notification date."""
        new_date = '2024-01-20'
        
        self.service.update_notification_date(
            contract_id=1,
            date=new_date
        )
        
        self.contract.refresh_from_db()
        self.assertEqual(
            self.contract.notificationdate.strftime('%Y-%m-%d'),
            new_date
        )

    def test_update_plan_start_date(self):
        """Test updating plan start date."""
        new_date = '2024-02-01'
        
        self.service.update_plan_start_date(
            contract_id=1,
            date=new_date
        )
        
        self.contract.refresh_from_db()
        self.assertEqual(
            self.contract.planstartdate.strftime('%Y-%m-%d'),
            new_date
        )

    def test_update_finish_date(self):
        """Test updating finish date."""
        new_date = '2024-12-31'
        
        self.service.update_finish_date(
            contract_id=1,
            date=new_date
        )
        
        self.contract.refresh_from_db()
        self.assertEqual(
            self.contract.finishdate.strftime('%Y-%m-%d'),
            new_date
        )

    def test_update_date_with_different_format(self):
        """Test updating date with valid date string."""
        new_date = '2024-06-15'
        
        self.service.update_start_operation_date(
            contract_id=1,
            date=new_date
        )
        
        self.contract.refresh_from_db()
        self.assertIsNotNone(self.contract.startoperationdate)

    def test_update_multiple_dates(self):
        """Test updating multiple dates sequentially."""
        self.service.update_start_operation_date(1, '2024-01-01')
        self.service.update_notification_date(1, '2024-01-15')
        self.service.update_plan_start_date(1, '2024-02-01')
        self.service.update_finish_date(1, '2024-12-31')
        
        self.contract.refresh_from_db()
        self.assertIsNotNone(self.contract.startoperationdate)
        self.assertIsNotNone(self.contract.notificationdate)
        self.assertIsNotNone(self.contract.planstartdate)
        self.assertIsNotNone(self.contract.finishdate)


class ContractServiceErrorHandlingTest(TestCase):
    """Test error handling in ContractService."""

    def setUp(self):
        """Set up test data."""
        self.service = ContractService()

    def test_read_contract_base_info_handles_does_not_exist(self):
        """Test that NotFound is raised for non-existent contract."""
        with self.assertRaises(NotFound):
            self.service.read_contract_base_info(999, 1)

    def test_update_contract_base_info_handles_does_not_exist(self):
        """Test that NotFound is raised when updating non-existent contract."""
        with self.assertRaises(NotFound):
            self.service.update_contract_base_info(999, {'location': 'Test'})

    @patch('contracts.services.logger')
    def test_logging_on_contract_not_found(self, mock_logger):
        """Test that errors are logged when contract not found."""
        with self.assertRaises(NotFound):
            self.service.read_contract_base_info(999, 1)
        
        mock_logger.error.assert_called_once()


class ContractServiceIntegrationTest(TestCase):
    """Integration tests for ContractService methods."""

    def setUp(self):
        """Set up complex test scenario."""
        self.user = User.objects.create_user(
            username='integrationuser',
            password='testpass123'
        )
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
            firstname='Integration',
            lastname='Manager'
        )
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Integration Contract',
            contracttypeid=self.contract_type,
            currencyid=self.currency,
            projectmanagerid=self.personel,
            contractamount_r=Decimal('5000000.00')
        )
        self.consultant = ContractConsultant.objects.create(
            consultantid=1,
            contractid=self.contract,
            consultant='Integration Consulting'
        )
        self.addendum = Addendum.objects.create(
            addendumid=1,
            contractid=self.contract,
            addendumamount_r=Decimal('500000.00'),
            afteraddendumdate=date.today() + timedelta(days=90)
        )
        self.epc = EpcCorporation.objects.create(
            epccorporationid=1,
            contractid=self.contract
        )
        UserRole.objects.create(
            userid=self.user,
            projectid=None
        )
        self.service = ContractService()

    def test_full_contract_data_retrieval(self):
        """Test retrieving all contract related data."""
        # Get base info
        base_info, confirmed = self.service.read_contract_base_info(1, 1)
        
        # Get consultants
        consultants = self.service.read_contract_consultant(1)
        
        # Get addendums
        addendums = self.service.read_contract_addendums(1)
        
        # Get EPC
        epc = self.service.read_epc_corporation(1)
        
        # Verify all data is retrieved
        self.assertIsInstance(base_info, dict)
        self.assertEqual(len(consultants), 1)
        self.assertEqual(len(addendums), 1)
        self.assertIsNotNone(epc)

    def test_update_and_retrieve_workflow(self):
        """Test updating contract and retrieving updated data."""
        # Update contract
        update_data = {'location': 'Updated Integration Location'}
        updated = self.service.update_contract_base_info(1, update_data)
        
        # Retrieve updated data
        base_info, _ = self.service.read_contract_base_info(1, 1)
        
        # Verify update
        self.assertEqual(base_info['location'], 'Updated Integration Location')