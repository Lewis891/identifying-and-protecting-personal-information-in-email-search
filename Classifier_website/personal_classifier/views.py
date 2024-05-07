from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.views import generic
from .tables import DataTable
from .filters import EmailFilter
from .models import RunClassifierData, EmailDataTable, FeatureData, TopicData
import pandas as pd
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from django.core.paginator import Paginator, EmptyPage
from personal_classifier.python_files import enron_classifier

# Create your views here.

def index(request):
    context = {}
    return render(request, 'personal_classifier/index.html', context)

def upload_collection(request):
    submitbutton= request.POST.get('submit')
    uploadbutton = request.POST.get('Update database')
    if submitbutton:
        number_of_docs,test_accuracy,features,topics,topic_names = enron_classifier.main()
        data_instance = RunClassifierData.objects.create(no_of_personal_emails=number_of_docs,accuracy_percentage=test_accuracy)
        for i in range(0,len(features)-1):
            obj = FeatureData.objects.create(
                feature_name = features[i][0],
                coefficient = features[i][1],
            )
            obj.save()
        for i in range(0,len(topics)):
            for j in range(0,len(topics[i])):
                obj = TopicData.objects.create(
                    topic_name = topic_names[i],
                    word = topics[i][j][0],
                    importance = topics[i][j][1],
                )

    elif uploadbutton:
        dbframe = pd.read_excel('classifier_data.xlsx')
        for dbframe in dbframe.itertuples():
            File_list = (dbframe.File).split('\\')[-2:]
            if dbframe.preds_rf == 1:
                obj = EmailDataTable.objects.create(
                    File = File_list[0] + "-" + File_list[1],
                    To = dbframe.To,
                    From = dbframe.From,
                    Body = dbframe.body,
                    message = dbframe.message,
                    count = dbframe.count,
                    IsPersonal = dbframe.IsPersonal,
                    category = dbframe.category,
                    lemma = dbframe.lemma,
                    preds_rf = "Personal",
                    topic = dbframe.Topic,
                    percentage = dbframe.Percentage,
                )
            else:
                obj = EmailDataTable.objects.create(
                    File = File_list[0] + "-" + File_list[1],
                    To = dbframe.To,
                    From = dbframe.From,
                    Body = dbframe.body,
                    message = dbframe.message,
                    count = dbframe.count,
                    IsPersonal = dbframe.IsPersonal,
                    category = dbframe.category,
                    lemma = dbframe.lemma,
                    preds_rf = "Non-personal",
                    topic = dbframe.Topic,
                    percentage = dbframe.Percentage,
                )
            obj.save()
    context = {
        'submitbutton':submitbutton,
        'uploadbutton':uploadbutton,
    }
    return render(request, 'personal_classifier/upload.html', context)

class search_collection(SingleTableMixin, FilterView):
    model = EmailDataTable
    table_class = DataTable
    template_name='personal_classifier/search.html'

    filterset_class = EmailFilter

def detail(request, email_id):
    IsPersonal = request.POST.get("IsPersonal")
    Reason = request.POST.get("reason")
    email = get_object_or_404(EmailDataTable, pk=email_id)
    body = email.Body
    feature_list = FeatureData.objects.values_list('feature_name', flat=True)
    topic_list = TopicData.objects.values_list('word', flat=True)
    features = []
    topic_words = []
    for f in feature_list:
        features.append(f)
    for t in topic_list:
        topic_words.append(t)
    if IsPersonal:
        EmailDataTable.objects.filter(pk=email_id).update(ManualClassify=IsPersonal)
    if Reason:
        EmailDataTable.objects.filter(pk=email_id).update(ManualReason=Reason)
    context = {
        'email_body' : body,
        'email' : email,
        'features_list' : features,
        'topic_list' : topic_words
    }
    return render(request, 'personal_classifier/detail.html', context)

def user_email(request, user_id):
    user = user_id
    emails_sent = EmailDataTable.objects.filter(From=user)
    emails_recieved = EmailDataTable.objects.filter(To__contains=user).values()
    no_sent = 0
    no_recieved = 0
    personal_sent = 0
    personal_recieved = 0
    sent_addresses = []
    no_sent_to = []
    from_addresses = []
    no_from = []
    for email in emails_sent:
        no_sent += 1
        if email.preds_rf == "Personal" or email.ManualClassify == "Personal" :
            personal_sent += 1
            sent_to_list = email.To.split(",")
            for person in sent_to_list:
                if person not in sent_addresses:
                    sent_addresses.append(person)
                    no_sent_to.append(1)
                else:
                    no_sent_to[(sent_addresses.index(person))] += 1

    for email in emails_recieved:
        no_recieved +=1
        if email['preds_rf'] == "Personal" or email['ManualClassify'] == "Personal" :
            personal_recieved += 1
            if email['From'] not in from_addresses:
                from_addresses.append(email['From'])
                no_from.append(1)
            else:
                no_from[(from_addresses.index(email['From']))] += 1

    non_personal_sent = no_sent - personal_sent
    non_personal_recieved = no_recieved - personal_recieved
    sent = [personal_sent,non_personal_sent]
    recieved = [personal_recieved, non_personal_recieved]
    context = {
        'user' : user,
        'no_sent' : no_sent,
        'no_recieved' : no_recieved,
        'personal_sent' : personal_sent,
        'personal_recieved' : personal_recieved,
        'emails_sent' : emails_sent,
        'emails_recieved' : emails_recieved,
        'sent' : sent,
        'recieved' : recieved,
        'sent_addresses' : sent_addresses,
        'no_sent_to' : no_sent_to,
        'from_addresses' : from_addresses,
        'no_from' : no_from,
    }
    return render(request, 'personal_classifier/user_email.html', context)

def graph_collection(request):
    topic_1 = request.POST.get("topic_1")
    no_of_personal_labels = ["Personal", "Non-personal"]
    no_of_personal = [0,0]
    From_addresses = []
    no_of_emails_from = []
    query = EmailDataTable.objects.order_by('preds_rf')
    feature_query = FeatureData.objects.all().order_by('-coefficient')
    topic_query = TopicData.objects.all().order_by('-importance')
    feature_names = []
    feature_coefs = []
    topic_0_names = []
    topic_o_imp = []
    for email in query:
        if email.preds_rf == "Personal" or email.ManualClassify == "Personal":
            no_of_personal[0] += 1
            if email.From not in From_addresses:
                From_addresses.append(email.From)
                no_of_emails_from.append(1)
            else:
                no_of_emails_from[(From_addresses.index(email.From))] += 1
        else :
            no_of_personal[1] += 1
    for feature in feature_query:
        feature_names.append(feature.feature_name)
        feature_coefs.append(feature.coefficient)
    if topic_1:
        for topic in topic_query:
            if topic.topic_name == topic_1:
                topic_0_names.append(topic.word)
                topic_o_imp.append(topic.importance)
    else:
        topic_1 = 'customers'
        for topic in topic_query:
            if topic.topic_name == 'customers':
                topic_0_names.append(topic.word)
                topic_o_imp.append(topic.importance)

    context = {
        'no_of_personal_labels': no_of_personal_labels,
        'no_of_personal': no_of_personal,
        'From_addresses': From_addresses,
        'no_of_emails_from': no_of_emails_from,
        'feature_names' : feature_names[:20],
        'coefficients' : feature_coefs[:20],
        'topic_0_words' : topic_0_names,
        'topic_0_imps' : topic_o_imp,
        'topic_1': topic_1,
    }
    return render(request, 'personal_classifier/graphs.html', context)