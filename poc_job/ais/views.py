from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ais.forms import AisForm, AisSettingForm
from ais.models import Ais, AisSettings, GdrSubmissionControl, GdrValidationLog, UddAIDimension
from django.db.models import Sum
from django.db import connection
import math
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.core.serializers import serialize
import json
import datetime
import dateutil.relativedelta
from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from managements.models import AdminUsers, LastPasswords
from django.utils.timezone import now
from django.conf import settings
import hashlib

@login_required
def create(request):
    aisserror=''
    if request.method == "POST":
        aiss = Ais()
        reExist=Ais.objects.using('grd_db').filter(ai_code=request.POST['ai_code']).count()
        if reExist  :
            aisserror="AI already exist."
            dimension=UddAIDimension.objects.using('grd_db').filter(end_month='9999-12-01').all()
            form = AisForm()
            return render(request,'create.html',{'aisserror':aisserror,'form':form,'dimension':dimension})
        aiss.ai_code=request.POST['ai_code']
        aiss.ai_id=request.POST['ai_id']
        aiss.ai_no=request.POST['ai_no']
        aiss.email=request.POST['email_address']
        aiss.status=request.POST['status']
        aiss.save(using='grd_db')
        return redirect("/show")
    else:
        dimension=UddAIDimension.objects.using('grd_db').filter(end_month='9999-12-01').all()
        form = AisForm()
    return render(request,'create.html',{'form':form,'dimension':dimension})

@login_required
def show(request):
    ais = Ais.objects.using('grd_db').all()
    AAIS=[]
    for ai in ais:
        try:
            ai.create_dtm=UddAIDimension.objects.using('grd_db').filter(ai_code=ai.ai_code).all()[:1].get()
        except UddAIDimension.DoesNotExist:
            ai.create_dtm =''

        AAIS.append(ai)
    return render(request,"show.html",{'ais':AAIS})

@login_required
def edit(request, id):
    aiss = Ais.objects.using('grd_db').get(id=id)
    dimension=UddAIDimension.objects.using('grd_db').filter(end_month='9999-12-01').all()
    return render(request,'edit.html', {'aiss':aiss,'dimension':dimension})

@login_required
def update(request, id):
    reExist=Ais.objects.using('grd_db').filter(ai_code=request.POST['ai_code']).exclude(id=id).count()
    if reExist  :
        dimension=UddAIDimension.objects.using('grd_db').filter(end_month='9999-12-01').all()
        aiss = Ais.objects.using('grd_db').get(id=id)
        aisserror="AI  already exist."
        return render(request,'edit.html',{'aisserror':aisserror,'aiss':aiss,'dimension':dimension})
    aiss = Ais.objects.using('grd_db').get(id=id)
    aiss.ai_code=request.POST['ai_code']
    aiss.ai_id=request.POST['ai_id']
    aiss.ai_no=request.POST.get('ai_no', False)
    aiss.email=request.POST['email_address']
    aiss.status=request.POST['status']
    aiss.save(using='grd_db')
    return redirect("/show")
    return render(request, 'edit.html', {'aiss': aiss})


@login_required
def aissettings(request):
    ais=AisSettings.objects.using('grd_db').all()
    return render(request,"aisettings.html",{'ais':ais})


@login_required
def savecuttof(request):
    if request.method == "POST":
        reDt=request.POST['deadline_return'].split('-')
        return_type=request.POST['return_type']
        reExist=AisSettings.objects.using('grd_db').filter(deadline__year=reDt[0]).filter(deadline__month=reDt[1]).filter(return_type=return_type).count()

        if reExist  :
            aisserror="Return Deadlines already exist."
            return render(request,'create_cutoff.html',{'aisserror':aisserror})
        aiss = AisSettings()
        aiss.deadline=request.POST['deadline_return']
        aiss.return_type=request.POST['return_type']
        aiss.save(using='grd_db')
        return redirect("/aissettings")
    else:
        aiss = AisSettings()
        return render(request,'create_cutoff.html',{'aiss':aiss})


@login_required
def updatecutoff(request,id):
    aiss = AisSettings.objects.using('grd_db').get(id=id)
    if request.method == "POST":
        return_type=request.POST['return_type']
        reDt=request.POST['deadline_return'].split('-')
        reExist=AisSettings.objects.using('grd_db').exclude(id=id).filter(deadline__year=reDt[0]).filter(deadline__month=reDt[1]).filter(return_type=return_type).count()
        if reExist :
            aisserror="Return Deadlines already exist."
            return render(request,'create_cutoff.html',{'aisserror':aisserror,'aiss':aiss})
        aiss = AisSettings.objects.using('grd_db').get(id=id)
        aiss.deadline=request.POST['deadline_return']
        aiss.return_type=request.POST['return_type']
        aiss.save(using='grd_db')
        return redirect("/aissettings")
    else:
     return render(request,'update_cutoff.html',{'aiss':aiss})

@login_required
def getsummary(request):
    colun=request.GET.get('sort')
    ord=request.GET.get('order')
    search=request.GET.get('search')
    page=request.GET.get('page')
    start_date=request.GET.get('start_date')
    end_date=request.GET.get('end_date')
    rml=request.GET.get('rml')
    cl=request.GET.get('cl')

    if not start_date:
        start_date = str(datetime.date.today())

    if not end_date:
        end_date = str(datetime.date.today())
    coluno=""
    if colun:
        coluno=colun
    rec=20
    if page:
        page=int(page)
        nextpg=int(page)+1
        prevpg=int(page)-1
    else:
        page=1
        nextpg=page+1
        prevpg=page-1
    endp=page*rec
    startp=endp-rec

    where=""
    ordby=""
    limit="LIMIT "+str(rec)+" OFFSET "+str(startp)
    if search:
        where=" where  (gdr_submission_control.ai_code='"+search+"'  or gdr_submission_control.ai_no='"+search+"'  or return_name='"+search+"'  or udd_ai_dimensions.ai_name='"+search+"'  or  submission_type='"+search+"'  or  block_code='"+search+"' or  zip_file_name LIKE '%%"+search+"%%' or job_uuid='"+search+"' or csv_file_name LIKE '"+search+"')"
        if start_date and end_date and rml=='1' and cl=='1':
            where=where+" and (gdr_submission_control.download_timestamp::date>='"+start_date+"' and gdr_submission_control.download_timestamp::date<='"+end_date+"') and (return_name='CL' or return_name='RML')"
        else:
            if start_date:
                where=where+" and gdr_submission_control.download_timestamp::date>='"+start_date+"'"
            if  end_date:
                where=where+" and gdr_submission_control.download_timestamp::date<='"+end_date+"'"
            if rml=='1' and cl=='1':
                where=where+" and (return_name='CL' or return_name='RML')"
            elif rml=='1':
                where=where+" and return_name='RML'"
            elif cl=='1':
                where=where+" and return_name='CL'"

    else:
        search='';
        where=""
        if start_date and end_date and rml=='1' and cl=='1':
            where=where+" where  (gdr_submission_control.download_timestamp::date>='"+start_date+"' and gdr_submission_control.download_timestamp::date<='"+end_date+"') and (return_name='CL' or return_name='RML') "
        else:
            if start_date:
                where=where+" where gdr_submission_control.download_timestamp::date>='"+start_date+"'"

            if  end_date:
                if where=="":
                    where=where+" where gdr_submission_control.download_timestamp::date<='"+end_date+"'"
                else:
                    where=where+" and gdr_submission_control.download_timestamp::date<='"+end_date+"'"

            if rml=='1' and cl=='1':
                if where=="":
                    where=where+" where (return_name='CL' or return_name='RML')"
            elif rml=='1':
                if where=="":
                    where=where+" where return_name='RML'"
                else:
                    where=where+" and return_name='RML'"

            elif cl=='1':
                if where=="":
                    where=where+" where return_name='CL'"
                else:
                    where=where+" and return_name='CL'"


    if colun:
        if colun=='ai_name':
            colun='nm'
        else:
            colun='gdr_submission_control.'+colun
        ordby=" order by "+ colun+" "+ord
    else:
        colun=''
        ord=''



    qry="SELECT max(udd_ai_dimensions.ai_name) as nm, gdr_submission_control.ai_code, position_date, return_name,submission_type,zip_file_name,max(csv_file_name) as csv_file_name ,max(block_code) as block_code ,job_uuid,max(zip_file_timestamp) as zip_file_timestamp ,sum(tot_csv_rows) as tot_csv_rows ,sum(staging_failed) as staging_failed ,sum(staging_rows) as staging_rows ,sum(staging_good) as staging_good ,sum(staging_warn) as staging_warn ,sum(staging_error) as staging_error ,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn,count(*) as total, count(*) as details  FROM gdr_submission_control INNER JOIN     udd_ai_dimensions on udd_ai_dimensions.ai_code=gdr_submission_control.ai_code "+ where +"  group by gdr_submission_control.ai_code,position_date,return_name, submission_type, zip_file_timestamp, zip_file_name, job_uuid" +ordby+" "+limit
    submission=GdrSubmissionControl.objects.using('grd_db').raw(qry)
    return render(request,"summary.html",{'submission':submission,'colun':coluno,'ord':ord,'search':search,'start_date':start_date,'end_date':end_date,'rml':rml,'cl':cl})



@login_required
def loadmore(request):
    colun=request.GET.get('sort')
    ord=request.GET.get('order')
    search=request.GET.get('search')
    page=request.GET.get('page')
    end_date=request.GET.get('end_date')
    rml=request.GET.get('rml')
    start_date=request.GET.get('start_date')
    cl=request.GET.get('cl')
    rec=10
    if page:
        page=int(page)
        nextpg=int(page)+1
        prevpg=int(page)-1
    else:
        page=1
        nextpg=page+1
        prevpg=page-1
    endp=page*rec
    startp=endp-rec

    where=""
    ordby=""
    limit="LIMIT "+str(rec)+" OFFSET "+str(startp)
    if search:
        where=" where  (gdr_submission_control.ai_code LIKE '%%"+search+"%%'  or gdr_submission_control.ai_no LIKE '%%"+search+"%%'  or return_name='"+search+"'  or udd_ai_dimensions.ai_name='"+search+"'  or  submission_type='"+search+"'  or  block_code='"+search+"' or  zip_file_name LIKE '%%"+search+"%%' or job_uuid='"+search+"' or csv_file_name LIKE '"+search+"')"
        if start_date and end_date and rml=='1' and cl=='1':
            where=where+" and (gdr_submission_control.download_timestamp::date>='"+start_date+"' and gdr_submission_control.download_timestamp::date<='"+end_date+"') and (return_name='CL' or return_name='RML')"
        else:
            if start_date:
                where=where+" and gdr_submission_control.download_timestamp::date>='"+start_date+"'"
            if  end_date:
                where=where+" and gdr_submission_control.download_timestamp::date<='"+end_date+"'"
            if rml=='1' and cl=='1':
                where=where+" and (return_name='CL' or return_name='RML')"
            elif rml=='1':
                where=where+" and return_name='RML'"
            elif cl=='1':
                where=where+" and return_name='CL'"

    else:
        search='';
        where=""
        if start_date and end_date and rml=='1' and cl=='1':
            where=where+" where  (gdr_submission_control.download_timestamp::date>='"+start_date+"' and gdr_submission_control.download_timestamp::date<='"+end_date+"') and (return_name='CL' or return_name='RML') "
        else:
            if start_date:
                where=where+" where gdr_submission_control.download_timestamp::date>='"+start_date+"'"

            if  end_date:
                if where=="":
                    where=where+" where gdr_submission_control.download_timestamp::date<='"+end_date+"'"
                else:
                    where=where+" and gdr_submission_control.download_timestamp::date<='"+end_date+"'"
            if rml=='1' and cl=='1':
                if where=="":
                    where=where+" where (return_name='CL' or return_name='RML')"
                else:
                    where=where+" and (return_name='CL' or return_name='RML')"
            elif rml=='1':
                if where=="":
                    where=where+" where return_name='RML'"
                else:
                    where=where+" and return_name='RML'"

            elif cl=='1':
                if where=="":
                    where=where+" where return_name='CL'"
                else:
                    where=where+" and return_name='CL'"


    if colun:
        if colun=='ai_name':
            colun='nm'
        else:
            colun='gdr_submission_control.'+colun
        ordby=" order by "+ colun+" "+ord


    submission=GdrSubmissionControl.objects.using('grd_db').raw("SELECT max(udd_ai_dimensions.ai_name) as nm, gdr_submission_control.ai_code, position_date, return_name,submission_type,zip_file_name,max(csv_file_name) as csv_file_name ,max(block_code) as block_code ,job_uuid,max(zip_file_timestamp) as zip_file_timestamp ,sum(tot_csv_rows) as tot_csv_rows ,sum(staging_failed) as staging_failed ,sum(staging_rows) as staging_rows ,sum(staging_good) as staging_good ,sum(staging_warn) as staging_warn ,sum(staging_error) as staging_error ,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn,count(*) as total, count(*) as details  FROM gdr_submission_control INNER JOIN     udd_ai_dimensions on udd_ai_dimensions.ai_code=gdr_submission_control.ai_code "+ where +"  group by gdr_submission_control.ai_code,position_date,return_name, submission_type, zip_file_timestamp, zip_file_name, job_uuid" +ordby+" "+limit)
    allsubs=[]
    for sub in submission:
        subx={}
        subx['nm']=sub.nm
        subx['ai_code']=sub.ai_code
        subx['position_date']=sub.position_date
        subx['return_name']=sub.return_name
        subx['zip_file_name']=sub.zip_file_name
        subx['csv_file_name']=sub.csv_file_name
        subx['submission_type']=sub.submission_type
        subx['block_code']=sub.block_code
        subx['job_uuid']=sub.job_uuid
        subx['zip_file_timestamp']=sub.zip_file_timestamp
        subx['tot_csv_rows']=sub.tot_csv_rows
        subx['staging_failed']=sub.staging_failed
        subx['staging_rows']=sub.staging_rows
        subx['staging_good']=sub.staging_good
        subx['staging_warn']=sub.staging_warn
        subx['staging_error']=sub.staging_error
        subx['gdr_good']=sub.gdr_good
        subx['gdr_warn']=sub.gdr_warn
        allsubs.append(subx)
    return HttpResponse(json.dumps(allsubs, default=str))



@login_required
def innerdetails(request):
    ai_code=request.GET.get('ai_code')
    return_name=request.GET.get('return_name')
    position_date=request.GET.get('position_date')
    submission_type=request.GET.get('submission_type')
    zip_file_name=request.GET.get('zip_file_name')
    job_uuid=request.GET.get('job_uuid')
    page=request.GET.get('page')
    rec=10
    if not page:
        page=1
    else:
        page=int(page)


    endp=page*rec
    startp=endp-rec


    qry="SELECT ai_code, position_date, return_name,submission_type,zip_file_name,max(csv_file_name) as csv_file_name ,max(block_code) as block_code ,job_uuid,max(zip_file_timestamp) as zip_file_timestamp ,sum(tot_csv_rows) as tot_csv_rows ,sum(staging_failed) as staging_failed ,sum(staging_rows) as staging_rows ,sum(staging_good) as staging_good ,sum(staging_warn) as staging_warn ,sum(staging_error) as staging_error ,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn FROM gdr_submission_control where ai_code='"+ai_code+"' and position_date='"+position_date+"' and return_name='"+return_name+"' and submission_type='"+submission_type+"' and zip_file_name='"+zip_file_name+"' and job_uuid='"+job_uuid+"'  group by ai_code,position_date,return_name, submission_type, zip_file_name, job_uuid, block_code"

    detailsub=GdrSubmissionControl.objects.using('grd_db').raw(qry)
    dtsub=[]
    for dtl in detailsub:
        inerdt={}
        try:
            eror=GdrValidationLog.objects.using('grd_db').filter(ai_code=dtl.ai_code,job_uuid=dtl.job_uuid,position_date=dtl.position_date,return_name=dtl.return_name,submission_type=dtl.submission_type,zip_file_name=dtl.zip_file_name,block_code=dtl.block_code,zip_file_timestamp=dtl.zip_file_timestamp).values()[startp:endp]
            erors=[]
            for er in list(eror):
                ers={}
                ers['event_id']=er['event_id']
                ers['row_key']=er['row_key']
                ers['field_label']=er['field_label']
                ers['validation_rule']=er['validation_rule']
                ers['remark']=er['remark']
                ers['result']=er['result']

                erors.append(ers)
        except GdrValidationLog.DoesNotExist:
            erors = []
        inerdt['erors']=erors
        inerdt['tot_csv_rows']=dtl.tot_csv_rows
        inerdt['staging_failed']=dtl.staging_failed
        inerdt['staging_rows']=dtl.staging_rows
        inerdt['staging_good']=dtl.staging_good
        inerdt['staging_warn']=dtl.staging_warn
        inerdt['staging_error']=dtl.staging_error
        inerdt['gdr_good']=dtl.gdr_good
        inerdt['gdr_warn']=dtl.gdr_warn
        inerdt['block_code']=dtl.block_code
        inerdt['ai_code']=dtl.ai_code
        inerdt['job_uuid']=dtl.job_uuid
        inerdt['position_date']=dtl.position_date
        inerdt['return_name']=dtl.return_name
        inerdt['submission_type']=dtl.submission_type
        inerdt['zip_file_name']=dtl.zip_file_name
        inerdt['zip_file_timestamp']=dtl.zip_file_timestamp
        dtsub.append(inerdt)
    return HttpResponse(json.dumps(dtsub, default=str))


@login_required
def geterrors(request):
    submission=GdrSubmissionControl.objects.using('grd_db').all()
    nsubmission=[]
    for sub in submission:
        sub.ai_code=Ais.objects.get(ai_code=sub.ai_code)
        nsubmission.append(sub)
    return render(request,"summary.html",{'submission':submission})


@login_required
def updatesettings(request):
    aiss = AisSettings.objects.using('grd_db').get(id=1)
    aiss.deadline_return=request.POST['deadline_return']
    aiss.deadline_amendment=request.POST['deadline_amendment']
    aiss.deadline_delete=request.POST['deadline_delete']
    aiss.save(using='grd_db')
    return redirect("/aissettings")

@login_required
def destroy(request, id):
    aiss = Ais.objects.using('grd_db').get(id=id)
    aiss.status=False
    aiss.save(using='grd_db')
    return redirect("/show")

@login_required
def activate(request, id):
    aiss = Ais.objects.using('grd_db').get(id=id)
    aiss.status=True
    aiss.save(using='grd_db')
    return redirect("/show")

@login_required
def deletecutoff(request, id):
    aiss = AisSettings.objects.using('grd_db').get(id=id)
    aiss.delete(using='grd_db')
    return redirect("/aissettings")


@login_required
def deadlinesubs(request):
    search=request.GET.get('search')
    page=request.GET.get('page')
    start_date=request.GET.get('start_date')
    end_date=request.GET.get('end_date')

    rec=20
    if page:
        page=int(page)
        nextpg=int(page)+1
        prevpg=int(page)-1
    else:
        page=1
        nextpg=page+1
        prevpg=page-1
    endp=page*rec
    startp=endp-rec

    where=""
    ordby=""
    where2=""
    today = datetime.date.today()
    limit="LIMIT "+str(rec)+" OFFSET "+str(startp)
    if search:
        where=" where  (udd_ai_dimensions.ai_name LIKE '%%"+search+"%%' or udd_ai_dimensions.ai_no LIKE '%%"+search+"%%' or ai_code LIKE '%%"+search+"%%')"
    else:
        search=""

    if start_date:
        where2=where2+" where  deadline>='"+start_date+"'"
    else:
        start_date=str(today)
        where2=where2+" where  deadline>='"+str(today)+"'"

    if  end_date:
        where2=where2+" and  deadline<='"+end_date+"'"
    else:
        end_date=str(today)
        where2=where2+" and  deadline<='"+str(today)+"'"

    ais=Ais.objects.using('grd_db').raw("select ai_participating.*,udd_ai_dimensions.ai_name FROM ai_participating INNER JOIN udd_ai_dimensions on udd_ai_dimensions.ai_code=ai_participating.ai_code "+where+" "+limit)
    lent=str(len(list(ais)))
    alais=[]
    for ai in ais:
        qr="select * from return_deadline "+where2+" order by deadline desc "
        aiss=AisSettings.objects.using('grd_db').raw(qr)
        alldts=[]
        for aid  in aiss:
            d = datetime.datetime.strptime(str(aid.deadline), "%Y-%m-%d")
            d2 = d - dateutil.relativedelta.relativedelta(months=1)
            position_date=str(d2).split('-')
            position_date=str(position_date[0])+'-'+str(position_date[1])
            qr="SELECT max(udd_ai_dimensions.ai_name) as nm, gdr_submission_control.ai_code, position_date, return_name,max(submission_type) as submission_type ,max(zip_file_name) as zip_file_name,max(csv_file_name) as csv_file_name ,max(block_code) as block_code ,max(job_uuid) as job_uuid , max(zip_file_timestamp) as zip_file_timestamp ,sum(tot_csv_rows) as tot_csv_rows ,sum(staging_failed) as staging_failed ,sum(staging_rows) as staging_rows ,sum(staging_good) as staging_good ,sum(staging_warn) as staging_warn ,sum(staging_error) as staging_error ,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn,count(*) as total, count(*) as details  FROM gdr_submission_control INNER JOIN     udd_ai_dimensions on udd_ai_dimensions.ai_code=gdr_submission_control.ai_code where  gdr_submission_control.ai_code='"+ai.ai_code+"' and to_char(position_date, 'YYYY-MM')  ='"+position_date+"'   and  gdr_submission_control.return_name='"+str(aid.return_type)+"'  group by gdr_submission_control.ai_code,position_date,return_name"
            submission=GdrSubmissionControl.objects.using('grd_db').raw(qr)
            aid.created_by=submission
            alldts.append(aid)
        ai.email=alldts
        alais.append(ai)
    return render(request,"deadline.html",{'ais':alais,'lent':lent,'page':page,'search':search,'start_date':start_date,'end_date':end_date});


@login_required
def dashboard(request):
    date=request.GET.get('date')
    if date:
        date = date
    else:
        date = datetime.date.today()
    date=str(date)
    rtype=request.GET.get('rtype')
    if rtype:
        rtypeq="and  gdr_submission_control.return_name='"+str(rtype)+"'"
        aisd=AisSettings.objects.using('grd_db').filter(return_type=rtype).all().order_by('deadline')
    else:
        rtype=''
        aisd=''
        rtypeq=''

    d = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    d2 = d - dateutil.relativedelta.relativedelta(months=1)
    position_date=str(d2).split('-')
    month=position_date[1]
    year=position_date[0]
    position_date=str(position_date[0])+'-'+str(position_date[1])
    return_name=rtype
    qry="SELECT max(id) as id, SUM(CASE WHEN status = True THEN 1 ELSE 0 END) AS active, SUM(CASE WHEN status = False THEN 1 ELSE 0 END) AS inactive, COUNT(*) AS total FROM ai_participating "
    ais=Ais.objects.using('grd_db').raw(qry)


    ids = GdrSubmissionControl.objects.using('grd_db').filter(position_date__year=year).filter(position_date__month=month)
    if return_name:
        ids.filter(return_name=return_name)

    ids=ids.values_list('ai_code', flat=True)
    d=Ais.objects.using('grd_db').exclude(ai_code__in=ids).distinct('ai_code').count()

    qryE="SELECT count(ai_participating.id) as e, ai_participating.id FROM ai_participating INNER JOIN gdr_submission_control on ai_participating.ai_code=gdr_submission_control.ai_code where  to_char(gdr_submission_control.position_date, 'YYYY-MM')='"+position_date+"'  "+rtypeq+" and download_timestamp::date<='"+str(date)+"' group by ai_participating.ai_code"
    e=Ais.objects.using('grd_db').raw(qryE)
    e=len(list(e))

    qryF="SELECT count(ai_participating.ai_code) as f,ai_participating.id FROM ai_participating INNER JOIN gdr_submission_control on ai_participating.ai_code=gdr_submission_control.ai_code where  to_char(gdr_submission_control.position_date, 'YYYY-MM')='"+position_date+"'  "+rtypeq+"  and download_timestamp::date>'"+str(date)+"' group by ai_participating.ai_code"
    f=Ais.objects.using('grd_db').raw(qryF)
    f=len(list(f))

    qrygh="SELECT max(ai_code)  as ai_code, max(position_date) as position_date, max(return_name) as return_name,max(submission_type) as submission_type,max(zip_file_name) as zip_file_name,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn  FROM gdr_submission_control where to_char(position_date, 'YYYY-MM') ='"+position_date+"'  "+rtypeq

    gh=GdrSubmissionControl.objects.using('grd_db').raw(qrygh)


    qryIJ="SELECT max(ai_code)  as ai_code, max(position_date) as position_date, max(return_name) as return_name,max(submission_type) as submission_type,max(zip_file_name) as zip_file_name,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn FROM gdr_submission_control where to_char(position_date, 'YYYY-MM') ='"+position_date+"'  "+rtypeq+"  and submission_type='R'"
    ij=GdrSubmissionControl.objects.using('grd_db').raw(qryIJ)

    qrykl="SELECT max(ai_code)  as ai_code, max(position_date) as position_date, max(return_name) as return_name,max(submission_type) as submission_type,max(zip_file_name) as zip_file_name,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn FROM gdr_submission_control where to_char(position_date, 'YYYY-MM') ='"+position_date+"'  "+rtypeq+"  and submission_type='F'"
    kl=GdrSubmissionControl.objects.using('grd_db').raw(qrykl)

    qrymn="SELECT max(ai_code)  as ai_code, max(position_date) as position_date, max(return_name) as return_name,max(submission_type) as submission_type,max(zip_file_name) as zip_file_name,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn  FROM gdr_submission_control where to_char(position_date, 'YYYY-MM')  ='"+position_date+"'  "+rtypeq+"  and submission_type='D'"
    mn=GdrSubmissionControl.objects.using('grd_db').raw(qrymn)



    return render(request,"dashboard.html",{'aisd':aisd,'ais':ais[0],'d':d,'e':e,'f':f,'gh':gh,'ij':ij,'kl':kl,'mn':mn,'date':date,'rtype':rtype})

@login_required
def deadlinemore(request):
    date=request.GET.get('date')
    ai_code=request.GET.get('ai_code')
    return_type=request.GET.get('return_type')
    d = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    d2 = d - dateutil.relativedelta.relativedelta(months=1)
    position_date=str(d2).split('-')
    position_date=str(position_date[0])+'-'+str(position_date[1])
    qr="SELECT max(udd_ai_dimensions.ai_name) as nm, gdr_submission_control.ai_code, position_date, return_name,submission_type,zip_file_name,max(csv_file_name) as csv_file_name ,max(block_code) as block_code ,job_uuid,max(zip_file_timestamp) as zip_file_timestamp ,sum(tot_csv_rows) as tot_csv_rows ,sum(staging_failed) as staging_failed ,sum(staging_rows) as staging_rows ,sum(staging_good) as staging_good ,sum(staging_warn) as staging_warn ,sum(staging_error) as staging_error ,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn,count(*) as total, count(*) as details  FROM gdr_submission_control INNER JOIN     udd_ai_dimensions on udd_ai_dimensions.ai_code=gdr_submission_control.ai_code where  gdr_submission_control.ai_code='"+ai_code+"' and to_char(position_date, 'YYYY-MM')  ='"+position_date+"'   and  gdr_submission_control.return_name='"+return_type+"'  group by gdr_submission_control.ai_code,position_date,return_name, submission_type, zip_file_timestamp, zip_file_name, job_uuid"
    submission=GdrSubmissionControl.objects.using('grd_db').raw(qr)
    allsubs=[]
    for sub in submission:
        subx={}
        subx['nm']=sub.nm
        subx['ai_code']=sub.ai_code
        subx['position_date']=sub.position_date
        subx['return_name']=sub.return_name
        subx['zip_file_name']=sub.zip_file_name
        subx['csv_file_name']=sub.csv_file_name
        subx['submission_type']=sub.submission_type
        subx['block_code']=sub.block_code
        subx['job_uuid']=sub.job_uuid
        subx['zip_file_timestamp']=sub.zip_file_timestamp
        subx['tot_csv_rows']=sub.tot_csv_rows
        subx['staging_failed']=sub.staging_failed
        subx['staging_rows']=sub.staging_rows
        subx['staging_good']=sub.staging_good
        subx['staging_warn']=sub.staging_warn
        subx['staging_error']=sub.staging_error
        subx['gdr_good']=sub.gdr_good
        subx['gdr_warn']=sub.gdr_warn
        allsubs.append(subx)
    return HttpResponse(json.dumps(allsubs, default=str))

@login_required
def subdashboard(request):
    sdf=request.GET.get('sdf')
    page=request.GET.get('page')
    sdt=request.GET.get('sdt')
    pdt=request.GET.get('pdt')
    allsubsdt=request.GET.get('allsubsdt')



    ai_code=request.GET.get('ai')
    return_type=request.GET.get('return_type')
    search=request.GET.get('search')
    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
    start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

    if search:
        search=search
        where=" where  (udd_ai_dimensions.ai_name LIKE '%%"+search+"%%' or udd_ai_dimensions.ai_no LIKE '%%"+search+"%%')"
    else:
        search=''
        where=""

    if ai_code:
        ai_code=ai_code
        ai=ai_code.split("--")[0]
        if where=="":
            where="where udd_ai_dimensions.ai_code LIKE '%%"+ai+"%%'"
        else:
            where=where+" and  udd_ai_dimensions.ai_code LIKE '%%"+ai+"%%'"
    else:
        ai_code=''

    if sdf:
        sdf=sdf
    else:
        sdf=str(datetime.date.today())

    if sdt:
        sdt=sdt
    else:
        sdt=str(datetime.date.today())

    if pdt:
        pdt=pdt
        d = datetime.datetime.strptime(str(pdt), "%Y-%m-%d")
        d2 = d - dateutil.relativedelta.relativedelta(months=1)
        position_date=str(d2).split('-')
        position_date=str(position_date[0])+'-'+str(position_date[1])
        pq="and to_char(gdr_submission_control.position_date, 'YYYY-MM')='"+position_date+"'"
    else:
        pdt=''
        pq=''
        position_date=''


    total=0
    errr=0
    warn=0
    togdr=0
    good=0

    rec=20
    if page:
        page=int(page)
        nextpg=int(page)+1
        prevpg=int(page)-1
    else:
        page=1
        nextpg=page+1
        prevpg=page-1

    endp=page*rec
    startp=endp-rec
    limit="LIMIT "+str(rec)+" OFFSET "+str(startp)

    if allsubsdt=='1':
        subdt=""
    else:
        subdt="and (download_timestamp::date >='"+sdf+"' and download_timestamp::date <='"+sdt+"')"
        allsubsdt=0

    if return_type:
        rtype="and  gdr_submission_control.return_name='"+str(return_type)+"'"
        aisd=AisSettings.objects.using('grd_db').filter(return_type=return_type).all().order_by('deadline')
    else:
        rtype=""
        aisd=''

    ais = Ais.objects.using('grd_db').all().order_by('ai_code')
    qry="SELECT max(id) as id, SUM(CASE WHEN status = True THEN 1 ELSE 0 END) AS active, SUM(CASE WHEN status = False THEN 1 ELSE 0 END) AS inactive, COUNT(*) AS total FROM ai_participating "
    aisx=Ais.objects.using('grd_db').raw(qry)
    AAIS=[]
    for ai in ais:
        try:
            ai.create_dtm=UddAIDimension.objects.using('grd_db').filter(ai_code=ai.ai_code).all()[:1].get()
        except UddAIDimension.DoesNotExist:
            ai.create_dtm =''

        AAIS.append(ai)
    aisxn=ais = Ais.objects.using('grd_db').all().order_by('ai_no')
    AAISN=[]
    for ai in aisxn:
        try:
            ai.create_dtm=UddAIDimension.objects.using('grd_db').filter(ai_code=ai.ai_code).all()[:1].get()
        except UddAIDimension.DoesNotExist:
            ai.create_dtm =''

        AAISN.append(ai)

    ais=Ais.objects.using('grd_db').raw("select ai_participating.ai_no, ai_participating.id ,max(ai_participating.ai_code) as ai_code, max(udd_ai_dimensions.ai_name) as ai_name FROM ai_participating INNER JOIN udd_ai_dimensions on udd_ai_dimensions.ai_code=ai_participating.ai_code "+where+" group by ai_participating.ai_code "+limit)
    alais=[]
    for ai in ais:
        qr="SELECT (sum(staging_error)+sum(staging_failed)) as tot_error, gdr_submission_control.ai_code as innr, gdr_submission_control.ai_code, max(position_date) as position_date, return_name,max(submission_type) as submission_type ,max(zip_file_name) as zip_file_name,max(csv_file_name) as csv_file_name ,max(block_code) as block_code ,max(job_uuid) as job_uuid , max(zip_file_timestamp) as zip_file_timestamp ,sum(tot_csv_rows) as tot_csv_rows ,sum(staging_failed) as staging_failed ,sum(staging_rows) as staging_rows ,sum(staging_good) as staging_good ,sum(staging_warn) as staging_warn ,sum(staging_error) as staging_error ,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn,count(*) as total, count(*) as details  FROM gdr_submission_control   where  gdr_submission_control.ai_code='"+ai.ai_code+"'  "+pq+" "+subdt+"   "+rtype+"  group by gdr_submission_control.ai_code,return_name"
        #print(qr)
        submissions=[]
        submission=GdrSubmissionControl.objects.using('grd_db').raw(qr)
        for sub in submission:
            total=total+int(sub.tot_csv_rows)
            errr=errr+(int(sub.staging_failed)+int(sub.staging_error))
            warn=warn+int(sub.gdr_warn)
            good=good+int(sub.gdr_good)
            qr2="SELECT  (sum(staging_error)+sum(staging_failed)) as tot_error, ai_code, position_date,  max(block_code) as block_code,  return_name,submission_type,zip_file_name,max(csv_file_name) as csv_file_name  ,job_uuid,max(zip_file_timestamp) as zip_file_timestamp ,sum(tot_csv_rows) as tot_csv_rows ,sum(staging_failed) as staging_failed ,sum(staging_rows) as staging_rows ,sum(staging_good) as staging_good ,sum(staging_warn) as staging_warn ,sum(staging_error) as staging_error ,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn,count(*) as total, max(process_timestamp) as process_timestamp  FROM gdr_submission_control  where   ai_code='"+ai.ai_code+"' "+pq+"   "+subdt+"  and return_name ='"+sub.return_name+"'   group by ai_code,position_date,return_name, submission_type, zip_file_timestamp, zip_file_name, job_uuid"
            asubmission=GdrSubmissionControl.objects.using('grd_db').raw(qr2)
            al=len(list(asubmission))
            if al:
                sub.details=asubmission
            else:
                sub.details=''
            submissions.append(sub)
        ai.email=submissions
        alais.append(ai)
        #total=warn+errr+good
        togdr=warn+good
    lent=str(len(alais))
    if pdt:
        pd=position_date.split('-')
        year=pd[0]
        month=pd[1]
        ids = GdrSubmissionControl.objects.using('grd_db').filter(position_date__year=year).filter(position_date__month=month)
        if subdt:
            ids.filter(download_timestamp__range=(sdf,sdt))
        if return_type:
            ids.filter(return_name=return_type).values_list('ai_code', flat=True)
        ids=ids.values_list('ai_code', flat=True)
        d=Ais.objects.using('grd_db').exclude(ai_code__in=ids).distinct('ai_code').count()

        qryE="SELECT count(ai_participating.id) as e, ai_participating.id FROM ai_participating INNER JOIN gdr_submission_control on ai_participating.ai_code=gdr_submission_control.ai_code where  to_char(gdr_submission_control.position_date, 'YYYY-MM')='"+position_date+"' "+subdt+"  "+rtype+" and  download_timestamp::date<='"+str(pdt)+"'  group by ai_participating.ai_code"
        e=Ais.objects.using('grd_db').raw(qryE)
        e=len(list(e))

        qryF="SELECT count(ai_participating.ai_code) as f,ai_participating.id FROM ai_participating INNER JOIN gdr_submission_control on ai_participating.ai_code=gdr_submission_control.ai_code where  to_char(gdr_submission_control.position_date, 'YYYY-MM')='"+position_date+"'  "+subdt+"  "+rtype+" and  download_timestamp::date>'"+str(pdt)+"' group by ai_participating.ai_code"
        f=Ais.objects.using('grd_db').raw(qryF)
        f=len(list(f))
    else:
        f=0
        d=0
        e=0





    return render(request,"subdashboard.html",{'allsubsdt':allsubsdt,'aisd':aisd,'ais':aisx[0],'AAISN':AAISN,'AAIS':AAIS,'lent':lent,'page':page,'pdt':pdt,'sdf':sdf,'sdt':sdt,'search':search,'ai_code':ai_code,'return_type':return_type,'alais':alais,'togdr':togdr,'good':good,'warn':warn,'errr':errr,'total':total,'d':d,'e':e,'f':f});


@login_required
def subdashprevnext(request):
    ai_code=request.GET.get('ai_code')
    job_uuid=request.GET.get('job_uuid')
    position_date=request.GET.get('position_date')
    return_name=request.GET.get('return_name')
    submission_type=request.GET.get('submission_type')
    zip_file_name=request.GET.get('zip_file_name')
    block_code=request.GET.get('block_code')
    zip_file_timestamp=request.GET.get('zip_file_timestamp')
    page=request.GET.get('page')
    herror=request.GET.get('herror')
    hwarning=request.GET.get('hwarning')
    if not page:
        page=1
    else:
        page=int(page)
    rec=20
    endp=page*rec
    startp=endp-rec
    try:
        eror=GdrValidationLog.objects.using('grd_db').filter(ai_code=ai_code,job_uuid=job_uuid,position_date=position_date,return_name=return_name,submission_type=submission_type,zip_file_name=zip_file_name,block_code=block_code,zip_file_timestamp=zip_file_timestamp)
        if herror=='1':
            eror=eror.exclude(result='E')
        if hwarning=='1':
            eror=eror.exclude(result='W')

        eror=eror.values()[startp:endp]
        erors=[]
        for er in list(eror):
            ers={}
            ers['event_id']=er['event_id']
            ers['row_key']=er['row_key']
            ers['field_label']=er['field_label']
            ers['validation_rule']=er['validation_rule']
            ers['remark']=er['remark']
            ers['result']=er['result']

            erors.append(ers)
    except GdrValidationLog.DoesNotExist:
        erors = []
    return HttpResponse(json.dumps(erors, default=str))


@login_required
def innersubdashboard(request):
    ai_code=request.GET.get('ai_code')
    job_uuid=request.GET.get('job_uuid')
    return_name=request.GET.get('return_name')
    submission_type=request.GET.get('submission_type')
    zip_file_name=request.GET.get('zip_file_name')
    block_code=request.GET.get('block_code')
    zip_file_timestamp=request.GET.get('zip_file_timestamp')
    sdf=request.GET.get('sdf')
    sdt=request.GET.get('sdt')
    page=request.GET.get('page')
    allsubsdt=request.GET.get('allsubsdt')
    herror=request.GET.get('herror')
    hwarning=request.GET.get('hwarning')
    if allsubsdt=='1':
        subdt=""
    else:
        subdt="and (download_timestamp::date >='"+sdf+"' and download_timestamp::date <='"+sdt+"')"

    if not page:
        page=1
    else:
        page=int(page)
    rec=20
    endp=page*rec
    startp=endp-rec
    qr2="SELECT  (sum(staging_error)+sum(staging_failed)) as tot_error, ai_code, position_date, block_code,  return_name,submission_type,zip_file_name,max(csv_file_name) as csv_file_name  ,job_uuid,max(zip_file_timestamp) as zip_file_timestamp ,sum(tot_csv_rows) as tot_csv_rows ,sum(staging_failed) as staging_failed ,sum(staging_rows) as staging_rows ,sum(staging_good) as staging_good ,sum(staging_warn) as staging_warn ,sum(staging_error) as staging_error ,sum(gdr_good) as gdr_good ,sum(gdr_warn) as gdr_warn,count(*) as total, max(process_timestamp) as process_timestamp  FROM gdr_submission_control  where   ai_code='"+ai_code+"'  "+subdt+"  and return_name ='"+return_name+"'  and submission_type='"+submission_type+"' and zip_file_name='"+zip_file_name+"' and job_uuid='"+job_uuid+"' group by ai_code,position_date,return_name, submission_type, zip_file_timestamp, zip_file_name, job_uuid,block_code"
    detailsub=GdrSubmissionControl.objects.using('grd_db').raw(qr2)
    dtsub=[]
    for dtl in detailsub:
        inerdt={}
        try:
            eror=GdrValidationLog.objects.using('grd_db').filter(ai_code=dtl.ai_code,job_uuid=dtl.job_uuid,return_name=dtl.return_name,position_date=dtl.position_date, submission_type=dtl.submission_type,zip_file_name=dtl.zip_file_name,block_code=dtl.block_code,zip_file_timestamp=dtl.zip_file_timestamp)
            if herror=='1':
                eror=eror.exclude(result='E')
            if hwarning=='1':
                eror=eror.exclude(result='W')
            eror=eror.values()[startp:endp]
            erors=[]
            for er in list(eror):
                ers={}
                ers['event_id']=er['event_id']
                ers['row_key']=er['row_key']
                ers['field_label']=er['field_label']
                ers['validation_rule']=er['validation_rule']
                ers['remark']=er['remark']
                ers['result']=er['result']

                erors.append(ers)
        except GdrValidationLog.DoesNotExist:
            erors = []
        inerdt['erors']=erors
        inerdt['tot_csv_rows']=dtl.tot_csv_rows
        inerdt['staging_failed']=dtl.staging_failed
        inerdt['staging_rows']=dtl.staging_rows
        inerdt['tot_error']=dtl.tot_error
        inerdt['staging_good']=dtl.staging_good
        inerdt['staging_warn']=dtl.staging_warn
        inerdt['staging_error']=dtl.staging_error
        inerdt['gdr_good']=dtl.gdr_good
        inerdt['gdr_warn']=dtl.gdr_warn
        inerdt['block_code']=dtl.block_code
        inerdt['ai_code']=dtl.ai_code
        inerdt['job_uuid']=dtl.job_uuid
        inerdt['position_date']=dtl.position_date
        inerdt['return_name']=dtl.return_name
        inerdt['submission_type']=dtl.submission_type
        inerdt['zip_file_name']=dtl.zip_file_name
        inerdt['zip_file_timestamp']=dtl.zip_file_timestamp
        dtsub.append(inerdt)

    return HttpResponse(json.dumps(dtsub, default=str))

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            users=AdminUsers.objects.get(pk=request.user.pk)
            users.is_login=1
            users.last_password_change=now()
            users.save()

            lp=LastPasswords()
            lp.user_id=request.user.pk
            result = hashlib.md5(request.POST['new_password2'].encode())
            lp.last_passwords=result.hexdigest()
            lp.save()

            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form,
        'PREVOIUS_PASSWORDS':settings.PREVOIUS_PASSWORDS,
        'PASSWORD_CHNGED_WITHIN_DAYS':settings.PASSWORD_CHNGED_WITHIN_DAYS,
        'LOGIN_ATTEMPET':settings.LOGIN_ATTEMPET,
        'LOGIN_ATTEMPET_LOCK':settings.LOGIN_ATTEMPET_LOCK,
        'PASSWORD_EXPIRY_DURATION':settings.PASSWORD_EXPIRY_DURATION

    })
