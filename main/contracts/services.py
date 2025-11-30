"""
Services for the contracts application.
"""
import datetime
import logging
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from contracts.models import Contract, ContractConsultant, EpcCorporation, Addendum
from accounts.models import UserRole
from projects.models import ReportConfirm
from contracts.serializers import ContractSerializerEx, ContractBaseInfoSerializer, ContractConsultantSerializer, \
    EpcCorporationSerializer, ContractAddendumSerializer


logger = logging.getLogger(__name__)


class ContractService:
    """
    Service for the contracts application.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def read_contract(userid):
        all_contracts = UserRole.objects.filter(
            userid__exact=userid,
            projectid__exact=None
        )

        if len(all_contracts) == 1:
            contracts = Contract.objects.all().order_by('-startdate')
        else:
            contracts = Contract.objects.filter(
                Contract_UserRole__userid__exact=userid
                ).order_by('-startdate').distinct()

        serializer = ContractSerializerEx(contracts, many=True)
        return serializer.data

    @staticmethod
    def read_contract_base_info(contract_id, date_id):
        """
        Get the contract base info for a contract.
        Returns dict with contractInfo and projectManagerConfirmed.
        """
        try:
            contract = Contract.objects.get(pk=contract_id)
        except Contract.DoesNotExist:
            logger.error("Contract not found: %s", contract_id)
            raise NotFound(f"Contract with id {contract_id} not found")

        serializer = ContractBaseInfoSerializer(instance=contract, many=False)

        report_confirmed = ReportConfirm.objects.filter(
            contractid__exact=contract_id,
            dateid__exact=date_id,
            pm_c__gt=0
        )

        return serializer.data, True if report_confirmed is not None and len(report_confirmed) > 0 else False

    @staticmethod
    def read_contract_consultant(contract_id):
        """
        Get the contract consultant for a contract.
        Returns serialized data (list of dicts).
        """
        consultants = ContractConsultant.objects.filter(contractid=contract_id)
        serializer = ContractConsultantSerializer(consultants, many=True)
        return serializer.data

    @staticmethod
    def read_contract_addendums(contract_id):
        """
        Get the contract addendum list for a contract.
        Returns serialized data (list of dicts).
        """
        addendums = Addendum.objects.filter(contractid=contract_id)
        serializer = ContractAddendumSerializer(addendums, many=True)
        return serializer.data

    @staticmethod
    def read_epc_corporation(contract_id):
        """
        Get the EPC corporation for a contract.
        Returns serialized data (dict or None).
        """
        try:
            corporation = EpcCorporation.objects.filter(contractid=contract_id).first()
            if not corporation:
                return None
            serializer = EpcCorporationSerializer(corporation)
            return serializer.data
        except ObjectDoesNotExist:
            logger.warning("EPC Corporation not found for contract: %s", contract_id)
            return None

    @staticmethod
    def update_contract_base_info(contract_id, data):
        """
        Update the contract base info for a contract.
        Returns updated serialized data (dict).
        """
        try:
            contract = Contract.objects.get(pk=contract_id)
        except Contract.DoesNotExist:
            logger.error("Contract not found: %s", contract_id)
            raise NotFound(f"Contract with id {contract_id} not found")

        serializer = ContractBaseInfoSerializer(
            instance=contract,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return fresh serialized data
        return ContractBaseInfoSerializer(contract).data

    @staticmethod
    def update_start_operation_date(contract_id, date):
        """
        Update the start operation date for a contract.
        """
        date_format = "%Y-%m-%d"
        start_operation_date = datetime.strptime(str(date), date_format)

        Contract.objects.filter(
            contractid__exact=contract_id).update(startoperationdate=start_operation_date)

    @staticmethod
    def update_notification_date(contract_id, date):
        """
        Update the notification date for a contract.
        """
        date_format = "%Y-%m-%d"
        notification_date = datetime.strptime(str(date), date_format)

        Contract.objects.filter(
            contractid__exact=contract_id).update(notificationdate=notification_date)

    @staticmethod
    def update_plan_start_date(contract_id, date):
        """
        Update the plan start date for a contract.
        """
        date_format = "%Y-%m-%d"
        plan_start_date = datetime.strptime(str(date), date_format)

        Contract.objects.filter(contractid__exact=contract_id).update(planstartdate=plan_start_date)

    @staticmethod
    def update_finish_date(contract_id, date):
        """
        Update the finish date for a contract.
        """
        date_format = "%Y-%m-%d"
        finish_date = datetime.strptime(str(date), date_format)

        Contract.objects.filter(contractid__exact=contract_id).update(finishdate=finish_date)

