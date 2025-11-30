"""
Tests for the contracts application serializers.
"""
from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta

from contracts.models import (
    ContractType, Contract, Country, Currency, 
    Personeltype, Personel, Addendum, ContractConsultant,
    EpcCorporation
)
from contracts.serializers import (
    ContractTypeSerializer, ContractSerializer, ContractSerializerEx,
    CountrySerializer, CurrencySerializer, PersonelTypeSerializer,
    PersonelSerializer, ContractBaseInfoSerializer, ContractConsultantSerializer,
    ContractAddendumSerializer, EpcCorporationSerializer, ItemSerializer
)


class ContractTypeSerializerTest(TestCase):
    """Test cases for ContractTypeSerializer."""

    def setUp(self):
        """Set up test data."""
        self.contract_type = ContractType.objects.create(
            contracttypeid=1,
            contracttype='EPC',
            description='Engineering, Procurement, and Construction'
        )
        self.serializer = ContractTypeSerializer(instance=self.contract_type)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        self.assertIn('contracttypeid', data)
        self.assertIn('contracttype', data)

    def test_serializer_data_matches_model(self):
        """Test serializer data matches model data."""
        data = self.serializer.data
        self.assertEqual(data['contracttype'], 'EPC')

    def test_deserialize_valid_data(self):
        """Test deserializing valid data."""
        data = {
            'contracttypeid': 2,
            'contracttype': 'BOT',
            'description': 'Build Operate Transfer'
        }
        serializer = ContractTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['contracttype'], 'BOT')


class ContractSerializerTest(TestCase):
    """Test cases for ContractSerializer."""

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
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type,
            currencyid=self.currency,
            contractamount_r=Decimal('1000000.00')
        )
        self.serializer = ContractSerializer(instance=self.contract)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        self.assertIn('contractid', data)
        self.assertIn('contract', data)
        self.assertIn('contractamount_r', data)

    def test_serializer_data_matches_model(self):
        """Test serializer data matches model data."""
        data = self.serializer.data
        self.assertEqual(data['contract'], 'Test Contract')

    def test_decimal_field_serialization(self):
        """Test decimal fields are serialized correctly."""
        data = self.serializer.data
        self.assertEqual(data['contractamount_r'], '1000000.00')


class ContractSerializerExTest(TestCase):
    """Test cases for ContractSerializerEx."""

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
        self.contract = Contract.objects.create(
            contractid=1,
            contract='Test Contract',
            contracttypeid=self.contract_type,
            currencyid=self.currency
        )
        self.serializer = ContractSerializerEx(instance=self.contract)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        expected_fields = ['contractid', 'contracttypeid', 'contracttype', 'contract', 'currency']
        for field in expected_fields:
            self.assertIn(field, data)

    def test_readonly_fields(self):
        """Test readonly fields are present."""
        data = self.serializer.data
        self.assertIn('contracttype', data)
        self.assertIn('currency', data)

    def test_only_specified_fields_included(self):
        """Test only the fields in Meta.fields are included."""
        data = self.serializer.data
        self.assertEqual(set(data.keys()), {'contractid', 'contracttypeid', 'contracttype', 'contract', 'currency'})


class CountrySerializerTest(TestCase):
    """Test cases for CountrySerializer."""

    def setUp(self):
        """Set up test data."""
        self.country = Country.objects.create(
            countryid=1,
            country='Iran',
            code='IR'
        )
        self.serializer = CountrySerializer(instance=self.country)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        self.assertIn('countryid', data)
        self.assertIn('country', data)
        self.assertIn('code', data)

    def test_serializer_data_matches_model(self):
        """Test serializer data matches model data."""
        data = self.serializer.data
        self.assertEqual(data['country'], 'Iran')
        self.assertEqual(data['code'], 'IR')


class CurrencySerializerTest(TestCase):
    """Test cases for CurrencySerializer."""

    def setUp(self):
        """Set up test data."""
        self.currency = Currency.objects.create(
            currencyid=1,
            currency='Rial',
            code='IRR'
        )
        self.serializer = CurrencySerializer(instance=self.currency)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        self.assertIn('currencyid', data)
        self.assertIn('currency', data)
        self.assertIn('code', data)

    def test_create_currency(self):
        """Test creating currency via serializer."""
        data = {
            'currencyid': 2,
            'currency': 'Dollar',
            'code': 'USD'
        }
        serializer = CurrencySerializer(data=data)
        self.assertTrue(serializer.is_valid())


class PersonelTypeSerializerTest(TestCase):
    """Test cases for PersonelTypeSerializer."""

    def setUp(self):
        """Set up test data."""
        self.personel_type = Personeltype.objects.create(
            personeltypeid=1,
            personeltype='Engineer'
        )
        self.serializer = PersonelTypeSerializer(instance=self.personel_type)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        self.assertIn('personeltypeid', data)
        self.assertIn('personeltype', data)


class PersonelSerializerTest(TestCase):
    """Test cases for PersonelSerializer."""

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
        self.serializer = PersonelSerializer(instance=self.personel)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        self.assertIn('personelid', data)
        self.assertIn('firstname', data)
        self.assertIn('lastname', data)

    def test_serializer_with_many(self):
        """Test serializer with multiple instances."""
        Personel.objects.create(
            personelid=2,
            firstname='Jane',
            lastname='Smith',
            personeltypeid=self.personel_type
        )
        personels = Personel.objects.all()
        serializer = PersonelSerializer(personels, many=True)
        self.assertEqual(len(serializer.data), 2)


class ContractBaseInfoSerializerTest(TestCase):
    """Test cases for ContractBaseInfoSerializer."""

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
        self.serializer = ContractBaseInfoSerializer(instance=self.contract)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        expected_fields = [
            'contractid', 'contract', 'contractamount_r',
            'projectmanagerid', 'duration', 'location'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_readonly_fields_present(self):
        """Test readonly fields are present in serialized data."""
        data = self.serializer.data
        readonly_fields = ['projectManager', 'customer', 'currency', 'passedDuration']
        for field in readonly_fields:
            self.assertIn(field, data)

    def test_computed_fields(self):
        """Test computed readonly fields."""
        data = self.serializer.data
        self.assertIn('contractamount_r_', data)
        self.assertIn('extraWorkPrice_r', data)

    def test_partial_update(self):
        """Test partial update with serializer."""
        update_data = {'location': 'New Location'}
        serializer = ContractBaseInfoSerializer(
            instance=self.contract,
            data=update_data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())


class ContractConsultantSerializerTest(TestCase):
    """Test cases for ContractConsultantSerializer."""

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
        self.serializer = ContractConsultantSerializer(instance=self.consultant)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        self.assertIn('consultantid', data)
        self.assertIn('consultant', data)

    def test_consultant_readonly_field(self):
        """Test consultant field is readonly."""
        data = self.serializer.data
        self.assertIn('consultant', data)
        self.assertEqual(data['consultant'], 'ABC Consulting')

    def test_multiple_consultants(self):
        """Test serializing multiple consultants."""
        ContractConsultant.objects.create(
            consultantid=2,
            contractid=self.contract,
            consultant='XYZ Consulting'
        )
        consultants = ContractConsultant.objects.filter(contractid=self.contract)
        serializer = ContractConsultantSerializer(consultants, many=True)
        self.assertEqual(len(serializer.data), 2)


class ContractAddendumSerializerTest(TestCase):
    """Test cases for ContractAddendumSerializer."""

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
            afteraddendumdate=date.today() + timedelta(days=30)
        )
        self.serializer = ContractAddendumSerializer(instance=self.addendum)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        expected_fields = [
            'addendumid', 'contractid', 'addendumamount_r',
            'addendumamount_fc', 'afteraddendumdate', 'afteraddendumshamsidate'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_readonly_fields(self):
        """Test readonly fields are present."""
        data = self.serializer.data
        self.assertIn('afteraddendumshamsidate', data)

    def test_decimal_fields(self):
        """Test decimal fields are properly serialized."""
        data = self.serializer.data
        self.assertEqual(data['addendumamount_r'], '100000.00')

    def test_create_addendum(self):
        """Test creating addendum via serializer."""
        data = {
            'addendumid': 2,
            'contractid': self.contract.contractid,
            'addendumamount_r': '50000.00',
            'addendumamount_fc': '500.00',
            'afteraddendumdate': (date.today() + timedelta(days=60)).isoformat()
        }
        serializer = ContractAddendumSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class ItemSerializerTest(TestCase):
    """Test cases for ItemSerializer."""

    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'name': 'Engineering',
            'value': 50000.0
        }
        serializer = ItemSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], 'Engineering')
        self.assertEqual(serializer.validated_data['value'], 50000.0)

    def test_serializer_with_invalid_data(self):
        """Test serializer with invalid data."""
        data = {
            'name': 'Engineering',
            'value': 'invalid'
        }
        serializer = ItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('value', serializer.errors)

    def test_missing_required_fields(self):
        """Test validation with missing fields."""
        data = {'name': 'Engineering'}
        serializer = ItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('value', serializer.errors)

    def test_serialize_item_list(self):
        """Test serializing list of items."""
        items = [
            {'name': 'Engineering', 'value': 50000.0},
            {'name': 'Procurement', 'value': 30000.0},
            {'name': 'Construction', 'value': 20000.0}
        ]
        serializer = ItemSerializer(data=items, many=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data), 3)


class EpcCorporationSerializerTest(TestCase):
    """Test cases for EpcCorporationSerializer."""

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
        self.serializer = EpcCorporationSerializer(instance=self.epc)

    def test_contains_expected_fields(self):
        """Test serializer contains expected fields."""
        data = self.serializer.data
        self.assertIn('E', data)
        self.assertIn('P', data)
        self.assertIn('C', data)

    def test_nested_item_serializer(self):
        """Test nested ItemSerializer fields."""
        data = self.serializer.data
        # These should be lists or None
        self.assertTrue(isinstance(data['E'], (list, type(None))))
        self.assertTrue(isinstance(data['P'], (list, type(None))))
        self.assertTrue(isinstance(data['C'], (list, type(None))))

    def test_readonly_nested_fields(self):
        """Test that E, P, C fields are readonly."""
        fields = self.serializer.fields
        self.assertTrue(fields['E'].read_only)
        self.assertTrue(fields['P'].read_only)
        self.assertTrue(fields['C'].read_only)

    def test_serializer_with_no_data(self):
        """Test serializer when EPC has no data."""
        data = self.serializer.data
        # Should have the three keys even if empty
        self.assertEqual(set(data.keys()), {'E', 'P', 'C'})


class SerializerIntegrationTest(TestCase):
    """Integration tests for multiple serializers working together."""

    def setUp(self):
        """Set up complex test data."""
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
            contract='Integration Test Contract',
            contracttypeid=self.contract_type,
            currencyid=self.currency,
            projectmanagerid=self.personel,
            contractamount_r=Decimal('1000000.00')
        )
        self.consultant = ContractConsultant.objects.create(
            consultantid=1,
            contractid=self.contract,
            consultant='Test Consulting'
        )
        self.addendum = Addendum.objects.create(
            addendumid=1,
            contractid=self.contract,
            addendumamount_r=Decimal('100000.00'),
            afteraddendumdate=date.today() + timedelta(days=30)
        )

    def test_serialize_contract_with_relations(self):
        """Test serializing contract with all related data."""
        contract_serializer = ContractBaseInfoSerializer(instance=self.contract)
        consultant_serializer = ContractConsultantSerializer(
            ContractConsultant.objects.filter(contractid=self.contract),
            many=True
        )
        addendum_serializer = ContractAddendumSerializer(
            Addendum.objects.filter(contractid=self.contract),
            many=True
        )
        
        contract_data = contract_serializer.data
        consultant_data = consultant_serializer.data
        addendum_data = addendum_serializer.data
        
        self.assertIsInstance(contract_data, dict)
        self.assertIsInstance(consultant_data, list)
        self.assertIsInstance(addendum_data, list)
        self.assertEqual(len(consultant_data), 1)
        self.assertEqual(len(addendum_data), 1)