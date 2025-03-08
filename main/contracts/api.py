from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view, action, permission_classes
# from django.db.models import Count
import pandas as pd
from django_pivot.pivot import pivot
import re

from contracts.models import *
from projects.models import ReportConfirm
from accounts.serializers import ProjectConfirmersSerializers
from .serializers import *


class ContractTypeAPI(viewsets.ModelViewSet):
    queryset = ContractType.objects.order_by('contracttypeid')

    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ContractTypeSerializer
  
  
class ContractAPI(viewsets.ModelViewSet):
    queryset = Contract.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = ContractSerializer


class ContractAPIEx(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    # READ ContractS
    def get(self, request, userid):
        try:
            all_contracts = UserRole.objects.filter(userid__exact=userid, 
                                                       projectid__exact=None)
            if(len(all_contracts) == 1):
                contracts = Contract.objects.all().order_by('-startdate')
                serializer = ContractSerializerEx(contracts, many=True)
            else:
                contracts = Contract.objects.filter(Contract_UserRole__userid__exact=userid).order_by(
                    '-startdate').distinct()
                serializer = ContractSerializerEx(contracts, many=True)
                
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ContractTypeAPI(viewsets.ModelViewSet):
    queryset = ContractType.objects.order_by('contracttypeid')

    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ContractTypeSerializer

class CountryAPI(viewsets.ModelViewSet):
    queryset = Country.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = CountrySerializer
    
class CurrencyAPI(viewsets.ModelViewSet):
    queryset = Currency.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = CurrencySerializer
    
class PersonelTypeAPI(viewsets.ModelViewSet):
    queryset = Personeltype.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = PersonelTypeSerializer


class PersonelAPI(viewsets.ModelViewSet):
    queryset = Personel.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = PersonelSerializer
    

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_ContractBaseInfo(request, contractId, dateId):
    try:
        contractBaseInfo = Contract.objects.get(pk=contractId)
        serializer = ContractBaseInfoSerializer(instance=contractBaseInfo, many=False)
                
        reportConfirmed = ReportConfirm.objects.filter(contractid__exact=contractId, dateid__exact=dateId, pm_c__gt=0)
        
        return Response({
            "status": "success", 
            "contractInfo": serializer.data,
            "projectManagerConfirmed": True if reportConfirmed is not None and len(reportConfirmed) > 0 else False
            }, 
            status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['Patch'])
@permission_classes([permissions.IsAuthenticated])
def put_startOperationDate(request, contractId, date):
    try:
        date_format = "%Y-%m-%d"
        startOperationDate = datetime.strptime(str(date), date_format)

        Contract.objects.filter(contractid__exact=contractId).update(startoperationdate=startOperationDate)
        return Response({"status": "success"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
      

@api_view(['Patch'])
@permission_classes([permissions.IsAuthenticated])
def put_notificationDate(request, contractId, date):
    try:
        date_format = "%Y-%m-%d"
        notificationDate = datetime.strptime(str(date), date_format)

        Contract.objects.filter(contractid__exact=contractId).update(notificationdate=notificationDate)
        return Response({"status": "success"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


@api_view(['Patch'])
@permission_classes([permissions.IsAuthenticated])
def put_planStartDate(request, contractId, date):
    try:
        date_format = "%Y-%m-%d"
        planStartDate = datetime.strptime(str(date), date_format)

        Contract.objects.filter(contractid__exact=contractId).update(planstartdate=planStartDate)
        return Response({"status": "success"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


@api_view(['Patch'])
@permission_classes([permissions.IsAuthenticated])
def put_finishDate(request, contractId, date):
    try:
        date_format = "%Y-%m-%d"
        finishDate = datetime.strptime(str(date), date_format)

        Contract.objects.filter(contractid__exact=contractId).update(finishdate=finishDate)
        return Response({"status": "success"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

      
class ContractInfo(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    
    @api_view(['Patch'])
    def put_ContractBaseInfo(request, id):
        try:
            contract = Contract.objects.get(pk=id)
            serializer = ContractBaseInfoSerializer(instance=contract, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = ContractBaseInfoSerializer(instance=contract, many=False)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# data=            serializer.is_valid()
    @api_view(['GET'])
    def get_ContractConsultant(request, id):
        try:
            contractConsultants = ContractConsultant.objects.filter(contractid__exact=id)
            serializer = ContractConsultantSerializer((contractConsultants if len(contractConsultants) > 0 else None) if contractConsultants is not None else None, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#    data= serializer.is_valid()
    @api_view(['GET'])
    def get_EpcCorporation(request, id):
        try:
            contractCorporations = EpcCorporation.objects.filter(contractid__exact=id).first()
            serializer = EpcCorporationSerializer(contractCorporations)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class ContractAddendumAPI(viewsets.ModelViewSet):
    queryset = Addendum.objects.all()
    
    serializer_class = ContractAddendumSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    
    @action(detail=True, methods=['get'])
    def contractAddendumList(self, request, *args, **kwargs):
        try:
            contractId = int(kwargs["contract_id"])
            
            contractAddendums = Addendum.objects.filter(contractid__exact=contractId)
            serializer = ContractAddendumSerializer(contractAddendums, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
