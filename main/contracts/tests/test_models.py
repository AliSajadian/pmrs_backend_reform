"""
Tests for the contracts application models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta

from contracts.models import (
    ContractType, Contract, Country, Currency, 
    Personeltype, Personel, Addendum, ContractConsultant, 
    EpcCorporation
)

User = get_user_model()


class ContractTypeModelTest(TestCase):
    """Test cases for ContractType model."""

    def setUp(self):
        """Set up test data."""
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC',
            description='Engineering, Procurement, and Construction'
        )

    def test_contract_type_creation(self):
        """Test contract type is created correctly."""
        self.assertEqual(self.contract_type.contracttype, 'EPC')
        self.assertIsInstance(self.contract_type, ContractType)

    def test_contract_type_str(self):
        """Test string representation of contract type."""
        self.assertEqual(str(self.contract_type), 'EPC')


class CountryModelTest(TestCase):
    """Test cases for Country model."""

    def setUp(self):
        """Set up test data."""
        self.country = Country.objects.create(
            countryid=1,
            country='Iran',
            code='IR'
        )

    def test_country_creation(self):
        """Test country is created correctly."""
        self.assertEqual(self.country.country, 'Iran')
        self.assertEqual(self.country.code, 'IR')

    def test_country_str(self):
        """Test string representation of country."""
        self.assertEqual(str(self.country), 'Iran')


class CurrencyModelTest(TestCase):
    """Test cases for Currency model."""

    def setUp(self):
        """Set up test data."""
        self.currency = Currency.objects.create(
            currencyid=1,
            currency='Rial',
            code='IRR',
            symbol='﷼'
        )

    def test_currency_creation(self):
        """Test currency is created correctly."""
        self.assertEqual(self.currency.currency, 'Rial')
        self.assertEqual(self.currency.code, 'IRR')

    def test_currency_str(self):
        """Test string representation of currency."""
        self.assertEqual(str(self.currency), 'Rial')


class PersoneltypeModelTest(TestCase):
    """Test cases for Personeltype model."""

    def setUp(self):
        """Set up test data."""
        self.personel_type = Personeltype.objects.create(
            personeltypeid=1,
            personeltype='Project Manager'
        )

    def test_personel_type_creation(self):
        """Test personel type is created correctly."""
        self.assertEqual(self.personel_type.personeltype, 'Project Manager')


class PersonelModelTest(TestCase):
    """Test cases for Personel model."""

    def setUp(self):
        """Set up test data."""
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

    def test_personel_creation(self):
        """Test personel is created correctly."""
        self.assertEqual(self.personel.firstname, 'John')
        self.assertEqual(self.personel.lastname, 'Doe')

    def test_personel_full_name(self):
        """Test personel full name property."""
        expected_name = 'John Doe'
        self.assertEqual(self.personel.full_name, expected_name)


class ContractModelTest(TestCase):
    """Test cases for Contract model."""

    def setUp(self):
        """Set up test data."""
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC'
        )
        self.currency = Currency.objects.create(
            currencyid=1,
            currency='Rial',
            code='IRR'
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
            contractamount_r=Decimal('1000000.00'),
            contractamount_fc=Decimal('10000.00'),
            startdate=date.today(),
            duration=365,
            projectmanagerid=self.personel
        )

    def test_contract_creation(self):
        """Test contract is created correctly."""
        self.assertEqual(self.contract.contract, 'Test Contract')
        self.assertEqual(self.contract.contractamount_r, Decimal('1000000.00'))
        self.assertIsInstance(self.contract.startdate, date)

    def test_contract_str(self):
        """Test string representation of contract."""
        self.assertEqual(str(self.contract), 'Test Contract')

    def test_contract_relationships(self):
        """Test contract foreign key relationships."""
        self.assertEqual(self.contract.contracttypeid, self.contract_type)
        self.assertEqual(self.contract.currencyid, self.currency)
        self.assertEqual(self.contract.projectmanagerid, self.personel)


class AddendumModelTest(TestCase):
    """Test cases for Addendum model."""

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
        self.addendum = Addendum.objects.create(
            addendumid=1,
            contractid=self.contract,
            addendumamount_r=Decimal('100000.00'),
            addendumamount_fc=Decimal('1000.00'),
            afteraddendumdate=date.today() + timedelta(days=30)
        )

    def test_addendum_creation(self):
        """Test addendum is created correctly."""
        self.assertEqual(self.addendum.addendumamount_r, Decimal('100000.00'))
        self.assertEqual(self.addendum.contractid, self.contract)

    def test_addendum_relationship_to_contract(self):
        """Test addendum foreign key to contract."""
        self.assertEqual(self.addendum.contractid.contract, 'Main Contract')


class ContractConsultantModelTest(TestCase):
    """Test cases for ContractConsultant model."""

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
        self.consultant = ContractConsultant.objects.create(
            consultantid=1,
            contractid=self.contract,
            consultant='ABC Consulting'
        )

    def test_consultant_creation(self):
        """Test consultant is created correctly."""
        self.assertEqual(self.consultant.consultant, 'ABC Consulting')
        self.assertEqual(self.consultant.contractid, self.contract)


class EpcCorporationModelTest(TestCase):
    """Test cases for EpcCorporation model."""

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

    def test_epc_corporation_creation(self):
        """Test EPC corporation is created correctly."""
        self.assertEqual(self.epc.contractid, self.contract)
        self.assertIsInstance(self.epc, EpcCorporation)