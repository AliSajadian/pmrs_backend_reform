"""
Services for the contracts application.
"""
import datetime
import math
import jdatetime
import logging
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from contracts.models import Contract, ContractConsultant, EpcCorporation, Addendum
from accounts.models import UserRole
from projects.models import ReportConfirm
from .serializers import ContractSerializerEx, ContractBaseInfoSerializer, ContractConsultantSerializer, \
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


def gregorian_to_shamsi(date):
    """
    Convert Gregorian date to Shamsi date.
    """
    # gregorian_date = jdatetime.date(1400,5,24).togregorian()
    try:
        j_date = jdatetime.date.fromgregorian(day=date.day,month=date.month,year=date.year)
        return  f"{str(j_date.year)}, {str(j_date.month)}, {str(j_date.day)}"
    except (ValueError, AttributeError, TypeError) as e:
        return str(e)


def gregorian_to_shamsi_show(date):
    """
    Convert Gregorian date to Shamsi date for display.
    """
    # gregorian_date = jdatetime.date(1400,5,24).togregorian()
    try:
        j_date = jdatetime.date.fromgregorian(day=date.day,month=date.month,year=date.year)
        return  f"{str(j_date.day)}, {str(j_date.month)}, {str(j_date.year)}"
    except (ValueError, AttributeError, TypeError) as e:
        return str(e)

        
def gregorian_to_shamsi1(date):
    """
    Convert Gregorian date to Shamsi date.
    """
    y = (math.trunc(date.timestamp()) + 467066.53004084 - 0.641087919916919581508) / 365.24219878
    y1 = y - math.trunc(datetime.datetime.fromtimestamp(y))

    m = 1 + math.trunc(datetime.datetime.fromtimestamp(y1 / 0.084875187)) \
         if (y1 <= 0.084875187 * 6) else \
           (7 + math.trunc(datetime.datetime.fromtimestamp((y1 - 0.084875187 * 6) / 0.082137278)) \
           if y1 <= (0.084875187 * 6 + 0.082137278 * 5) else 12)

    mm = '0' + str(math.trunc(datetime.datetime.fromtimestamp(m))) if m < 10 else \
        str(math.trunc(datetime.datetime.fromtimestamp(m)))

    d = math.trunc(datetime.datetime.fromtimestamp(y1 * 365.24219878 - (m - 1) * 31)) + 1 \
        if (m <= 6) else \
          math.trunc(datetime.datetime.fromtimestamp(y1 * 365.24219878 - (m - 1) * 30 - 6)) + 1 \
          if (m < 12) else \
            math.trunc(datetime.datetime.fromtimestamp(y1 * 365.24219878 - 336)) + 1

    dd = '0' + str(math.trunc(datetime.datetime.fromtimestamp(d))) if d < 10 else \
        str(math.trunc(datetime.datetime.fromtimestamp(d)))

    result = str(math.trunc(datetime.datetime.fromtimestamp(y))) + '/' + mm + '/' + dd

    return result

