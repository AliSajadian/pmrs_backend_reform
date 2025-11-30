"""
Services for the projects_files application.
"""
from django.contrib.auth import get_user_model
from accounts.models import UserRole
from contracts.models import Contract
from projects.models import ReportDate
from projects_files.models import ReportVisit, ReportVisitdate


def set_report_visit(userId, contractId, dateId, reportId):
    """
    Set the report visit for the projects_files application.
    """
    try:       
        isManager = UserRole.objects.filter(userid__exact=userId, roleid__role__exact='Board').count()
        if isManager == 0:
            return False
        
        user = get_user_model().objects.get(pk=userId)
        
        date = ReportDate.objects.get(pk=dateId)

        if(contractId == -1):
            reportVisits = ReportVisit.objects.filter(userid__exact=userId, dateid__exact=dateId)
            reportVisits.update(imagereport=1)
            
            isAllProject = UserRole.objects.filter(userid__exact=userId, contractid__exact=None).count() > 0
            
            if isAllProject:
                contracts = Contract.objects.filter(iscompleted__exact=False).exclude(contractid__in=reportVisits)
                for contract in contracts:
                    ReportVisit.objects.create(contractid=contract, dateid=date, userid=user, imagereport=1)
            else:
                userContractRole = UserRole.objects.filter(userid__exact=userId)
                contracts = Contract.objects.filter(contractid__in=userContractRole).exclude(contractid__in=reportVisits)
                for contract in contracts:
                    ReportVisit.objects.create(contractid=contract, dateid=date, userid=user, imagereport=1)
        else: 
            # reportVisits = ReportVisit.objects.filter(userid__exact=userId, contractid__exact=contractId, dateid__exact=dateId)
            contracts = Contract.objects.filter(contractid__exact=contractId)
            if len(contracts) == 1:
                # if len(reportVisits) == 0:
                    if reportId == 1:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, financialinfo=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 2:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, hse=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 3:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, progressstate=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 4:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, timeprogressstate=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 5:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, invoice=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 6:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, financialinvoice=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 7:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, workvolume=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 8:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, pmsprogress=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 9:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, budget=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)

                    elif reportId == 10:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, machinary=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 11:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, personel=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 12:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, problems=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 13:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, criticalactions=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)

                    elif reportId == 14:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, zoneimages=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 15:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, projectdox=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 16:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, durationdox=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 17:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, dashboard_r=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)

                    elif reportId == 18:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, dashboard_fc=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
                    elif reportId == 19:
                        reportVisit, _ = ReportVisit.objects.update_or_create(userid=user, contractid=contracts[0], 
                                                    dateid=date, imagereport=1)

                        ReportVisitdate.objects.update_or_create(visitreportid=reportVisit, reportid=reportId)
        return True
    except Exception as e:
        return False
       
