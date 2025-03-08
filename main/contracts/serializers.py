from rest_framework import serializers

from accounts.models import *
from contracts.models import *


#=========== Contract Serializers ============
class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = '__all__'
        
class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'

class ContractSerializerEx(serializers.ModelSerializer):
    contracttype = serializers.ReadOnlyField() 
    currency = serializers.ReadOnlyField()
    
    class Meta:
        model = Contract
        fields = ['contractid', 'contracttypeid', 'contracttype', 'contract', 'currency']
        
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
        
class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class PersonelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personeltype
        fields = '__all__'

class PersonelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personel
        fields = '__all__'

class ContractBaseInfoSerializer(serializers.ModelSerializer):
    contractamount_r_ = serializers.ReadOnlyField()
    contractamount_fc_ = serializers.ReadOnlyField()
    extraWorkPrice_r = serializers.ReadOnlyField()
    extraWorkPrice_fc = serializers.ReadOnlyField()
    projectManager = serializers.ImageField
    projectManagerImage = serializers.ReadOnlyField()
    customer = serializers.ReadOnlyField()
    currency = serializers.ReadOnlyField()
    passedDuration = serializers.ReadOnlyField()
    addendumDuration =  serializers.ReadOnlyField()
    planStartShamsiDate = serializers.ReadOnlyField()
    finishShamsiDate = serializers.ReadOnlyField()
    approximateFinishShamsiDate = serializers.ReadOnlyField()
    
    class Meta:
        model = Contract
        fields = ('contractid', 'contract', 'contractamount_r', 'contractamount_r_', 'extraWorkPrice_r', 
                  'contractamount_fc', 'contractamount_fc_', 'extraWorkPrice_fc', 'projectmanagerid', 'projectManager', 
                  'projectManagerImage', 'customer', 'currency', 'startoperationdate', 'notificationdate', 'planstartdate', 
                  'finishdate', 'duration', 'passedDuration', 'addendumDuration', 'planStartShamsiDate', 'finishShamsiDate', 
                  'approximateFinishShamsiDate', 'location', 'longitude', 'latitude'
                 )

class ContractBaseInfoEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ('contractid', 'startoperationdate', 
                  'notificationdate', 'planstartdate', 'finishdate', 
                  'attachmentcontractprice1_r', 'attachmentcontractprice1_fc', 
                  'attachmentcontractprice2_r', 'attachmentcontractprice2_fc', 
                  'attachmentcontractprice3_r', 'attachmentcontractprice3_fc', 
                  'attachmentcontractprice4_r', 'attachmentcontractprice4_fc', 
                  'attachmentcontractprice5_r', 'attachmentcontractprice5_fc')

class ContractConsultantSerializer(serializers.ModelSerializer):
    consultant = serializers.ReadOnlyField()

    class Meta:
        model = ContractConsultant
        fields = ('consultantid', 'consultant')
        
class ContractAddendumSerializer(serializers.ModelSerializer):
    afteraddendumshamsidate = serializers.ReadOnlyField()
    
    class Meta:
        model = Addendum
        fields = ('addendumid', 'contractid', 'addendumamount_r', 'addendumamount_fc', 'afteraddendumdate', 'afteraddendumshamsidate')

                
# class EPCDictField(serializers.DictField):
#     def to_internal_value(self, data):
#         # Perform validation on the keys of the dictionary here
#         if set(data.keys()) != {"value", "label"}:
#             raise serializers.ValidationError("Invalid keys for dictionary.")
#         return super().to_internal_value(data)
    
#     def to_representation(self, value):
#         return super().to_representation(value)
        
# class ContractCorporationSerializer(serializers.ModelSerializer):
#     E = EPCDictField()
#     P = EPCDictField()
#     C = EPCDictField()

#     class Meta:
#         model = EpcCorporation
#         fields = ('E', 'P', 'C')

class ItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.FloatField()

class EpcCorporationSerializer(serializers.ModelSerializer):
    E = ItemSerializer(many=True, read_only=True)
    P = ItemSerializer(many=True, read_only=True)
    C = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = EpcCorporation
        fields = ('E', 'P', 'C')