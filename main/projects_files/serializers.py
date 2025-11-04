"""
Serializers for the projects_files application.
"""
from rest_framework import serializers

from projects_files.models import *


class HseReportDoxSerializers(serializers.ModelSerializer):
    """
    Serializer for the HseReportDox model.
    """
    year = serializers.ReadOnlyField()
    month = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField()
    
    class Meta:
        model = HseReportDox
        fields = ('hsereportdoxid', 'contractid', 'dateid', 'year', 'month', 'filename', 'description', 'file', 'active')


class ProjectDoxSerializers(serializers.ModelSerializer):
    """
    Serializer for the ProjectDox model.
    """
    filename = serializers.ReadOnlyField()
    
    class Meta:
        model = ProjectDox
        fields = ('projectdoxid', 'contractid', 'dateid', 'doctitle', 'dockind', 'docno', 'filename', 'file', 'active')


class ContractorDoxSerializers(serializers.ModelSerializer):
    """
    Serializer for the ContractorDox model.
    """
    contractshamsidate = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField()
    
    class Meta:
        model = ContractorDox
        fields = ('contractordoxid', 'contractid', 'contractdate', 'contractshamsidate',  
                  'contracttitle', 'contractor', 'contractno', 'riderno', 'file', 'filename')


class ProjectMonthlyDoxSerializers(serializers.ModelSerializer):
    """
    Serializer for the ProjectMonthlyDox model.
    """
    year = serializers.ReadOnlyField()
    month = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField()
    
    class Meta:
        model = ProjectMonthlyDox
        fields = ('projectmonthlydoxid', 'contractid', 'dateid', 'year', 'month', 'filename', 'description', 'file', 'active')


class ApprovedInvoiceDoxSerializers(serializers.ModelSerializer):
    """
    Serializer for the ApprovedInvoiceDox model.
    """
    invoiceshamsidate = serializers.ReadOnlyField()
    sendshamsidate = serializers.ReadOnlyField()
    confirmshamsidate = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField()

    class Meta:
        model = InvoiceDox
        fields = ('invoicedoxid', 'contractid', 'dateid', 'invoicekind', 'invoiceno', 'invoicedate', 
                  'senddate', 'confirmdate', 'invoiceshamsidate', 'sendshamsidate', 'confirmshamsidate',  
                  'sgp_r', 'sgp_fc', 'cgp_r', 'cgp_fc', 'description', 'file', 'filename', 'active')


class ReportDoxSerializers(serializers.ModelSerializer):
    """
    Serializer for the ReportDox model.
    """
    class Meta:
        model = ReportDox
        fields = '__all__'
        

class ReportVisitSerializers(serializers.ModelSerializer):
    """
    Serializer for the ReportVisit model.
    """
    class Meta:
        model = ReportVisit
        fields = '__all__'


class ZoneSerializers(serializers.ModelSerializer):
    """
    Serializer for the Zone model.
    """
    class Meta:
        model = Zone
        fields = ('zoneid', 'zone')


class ZoneImagesSerializers(serializers.ModelSerializer):
    """
    Serializer for the ZoneImages model.
    """
    contract = serializers.ReadOnlyField
    zone = serializers.ReadOnlyField
    imagename1 = serializers.ReadOnlyField
    imagename2 = serializers.ReadOnlyField
    imagename3 = serializers.ReadOnlyField
    
    class Meta:
        model = ZoneImage
        fields = ('zoneimageid', 'zoneid', 'dateid', 'contract', 'zone', 'ppp', 'app', 'img1', 'imagepath1', 
                  'description1', 'img2', 'imagepath2', 'description2', 'img3', 'imagepath3', 'description3')
       

class ProjectZoneImagesSerializers(serializers.Serializer):
    """
    Serializer for the ProjectZoneImages model.
    """
    contract = serializers.CharField()
    zone = serializers.CharField()
    ppp = serializers.CharField()
    app = serializers.CharField()
    img = serializers.CharField()
    description = serializers.CharField()

    
class ReportZoneImagesSerializers1(serializers.ModelSerializer):
    """
    Serializer for the ReportZoneImages model.
    """
    zone = serializers.ReadOnlyField
    explanation = serializers.ReadOnlyField

    class Meta:
        model = ZoneImage
        fields = ('zone', 'img1', 'img2', 'img3', 'explanation')
        
        
class ReportVisitSerializers(serializers.ModelSerializer):
    """
    Serializer for the ReportVisit model.
    """
    manager = serializers.ReadOnlyField
    class Meta:
        model = ReportVisit
        fields = ('manager', 'financialinfo', 'hse','progressstate', 'timeprogressstate', 'invoice', 
                  'financialinvoice', 'workvolume', 'pmsprogress', 'budget', 'machinary', 'personel', 
                  'problems', 'criticalactions', 'zoneimages', 'projectdox', 'durationdox', 'dashboard_r', 
                  'dashboard_fc', 'imagereport',)
     