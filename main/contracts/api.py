"""
API for the contracts application.

This module contains the API for the contracts application.
"""
from datetime import datetime
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action, permission_classes

from contracts.models import ContractType, Contract, UserRole, Country, Currency, Personeltype, \
    Personel, Addendum, EpcCorporation, ContractConsultant
from projects.models import ReportConfirm
from .serializers import ContractTypeSerializer, ContractSerializer, ContractSerializerEx, \
    CountrySerializer, CurrencySerializer, PersonelTypeSerializer, PersonelSerializer, \
    ContractBaseInfoSerializer, ContractConsultantSerializer, EpcCorporationSerializer, \
    ContractAddendumSerializer

# pylint: disable=too-many-ancestors
class ContractTypeAPI(viewsets.ModelViewSet):
    """
    API for the ContractType model.
    """
    queryset = ContractType.objects.order_by('contracttypeid')

    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ContractTypeSerializer


class ContractAPI(viewsets.ModelViewSet):
    """
    API for the Contract model.
    """
    queryset = Contract.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = ContractSerializer


class ContractAPIEx(APIView):
    """
    API for the Contract model.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    # READ ContractS
    def get(self, request, userid):
        """
        Get the contracts for a user.
        """
        all_contracts = UserRole.objects.filter(
            userid__exact=userid,
            projectid__exact=None
        )
        if len(all_contracts) == 1:
            contracts = Contract.objects.all().order_by('-startdate')
            serializer = ContractSerializerEx(contracts, many=True)
        else:
            contracts = Contract.objects.filter(Contract_UserRole__userid__exact=userid).order_by(
                '-startdate').distinct()
            serializer = ContractSerializerEx(contracts, many=True)

        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


class CountryAPI(viewsets.ModelViewSet):
    """
    API for the Country model.
    """
    queryset = Country.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = CountrySerializer


class CurrencyAPI(viewsets.ModelViewSet):
    """
    API for the Currency model.
    """
    queryset = Currency.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = CurrencySerializer


class PersonelTypeAPI(viewsets.ModelViewSet):
    """
    API for the PersonelType model.
    """
    queryset = Personeltype.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = PersonelTypeSerializer


class PersonelAPI(viewsets.ModelViewSet):
    """
    API for the Personel model.
    """
    queryset = Personel.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = PersonelSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_contract_base_info(request, contract_id, date_id):
    """
    Get the contract base info for a contract.
    """
    contract_base_info = Contract.objects.get(pk=contract_id)
    serializer = ContractBaseInfoSerializer(instance=contract_base_info, many=False)

    report_confirmed = ReportConfirm.objects.filter(
        contractid__exact=contract_id,
        dateid__exact=date_id,
        pm_c__gt=0
    )

    return Response(
        {
            "status": "success", 
            "contractInfo": serializer.data,
            "projectManagerConfirmed": True if \
                report_confirmed is not None and len(report_confirmed) > 0 \
                else False
        },
        status=status.HTTP_200_OK
    )


@api_view(['Patch'])
@permission_classes([permissions.IsAuthenticated])
def put_start_operation_date(request, contract_id, date):
    """
    Update the start operation date for a contract.
    """
    date_format = "%Y-%m-%d"
    start_operation_date = datetime.strptime(str(date), date_format)

    Contract.objects.filter(
        contractid__exact=contract_id).update(startoperationdate=start_operation_date)
    return Response({"status": "success"}, status=status.HTTP_200_OK)


@api_view(['Patch'])
@permission_classes([permissions.IsAuthenticated])
def put_notification_date(request, contract_id, date):
    """
    Update the notification date for a contract.
    """
    date_format = "%Y-%m-%d"
    notification_date = datetime.strptime(str(date), date_format)

    Contract.objects.filter(
        contractid__exact=contract_id).update(notificationdate=notification_date)
    return Response({"status": "success"}, status=status.HTTP_200_OK)


@api_view(['Patch'])
@permission_classes([permissions.IsAuthenticated])
def put_plan_start_date(request, contract_id, date):
    """
    Update the plan start date for a contract.
    """
    date_format = "%Y-%m-%d"
    plan_start_date = datetime.strptime(str(date), date_format)

    Contract.objects.filter(contractid__exact=contract_id).update(planstartdate=plan_start_date)
    return Response({"status": "success"}, status=status.HTTP_200_OK)


@api_view(['Patch'])
@permission_classes([permissions.IsAuthenticated])
def put_finish_date(request, contract_id, date):
    """
    Update the finish date for a contract.
    """
    date_format = "%Y-%m-%d"
    finish_date = datetime.strptime(str(date), date_format)

    Contract.objects.filter(contractid__exact=contract_id).update(finishdate=finish_date)
    return Response({"status": "success"}, status=status.HTTP_200_OK)


class ContractInfo(APIView):
    """
    API for the ContractInfo model.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @api_view(['Patch'])
    def put_contract_base_info(self, request, *args, **kwargs):
        """
        Update the contract base info for a contract.
        """
        pk = kwargs["id"]
        contract = Contract.objects.get(pk=pk)
        serializer = ContractBaseInfoSerializer(instance=contract, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = ContractBaseInfoSerializer(instance=contract, many=False)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @api_view(['GET'])
    def get_contract_consultant(self, request, *args, **kwargs):
        """
        Get the contract consultant for a contract.
        """
        pk = kwargs["id"]
        contract_onsultants = ContractConsultant.objects.filter(contractid__exact=pk)
        serializer = ContractConsultantSerializer((contract_onsultants \
            if len(contract_onsultants) > 0 else None) \
                if contract_onsultants is not None else None, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @api_view(['GET'])
    def get_epc_corporation(self, request, *args, **kwargs):
        """
        Get the epc corporation for a contract.
        """
        pk = kwargs["id"]
        contract_corporations = EpcCorporation.objects.filter(contractid__exact=pk).first()
        serializer = EpcCorporationSerializer(contract_corporations)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

# pylint: disable=too-many-ancestors
class ContractAddendumAPI(viewsets.ModelViewSet):
    """
    API for the ContractAddendum model.
    """
    queryset = Addendum.objects.all()

    serializer_class = ContractAddendumSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['get'])
    def contract_addendum_list(self, request, *args, **kwargs):
        """
        Get the contract addendum list for a contract.
        """
        contract_id = int(kwargs["contract_id"])

        contract_addendums = Addendum.objects.filter(contractid__exact=contract_id)
        serializer = ContractAddendumSerializer(contract_addendums, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
