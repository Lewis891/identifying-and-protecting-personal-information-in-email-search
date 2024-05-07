import django_tables2 as tables
from .models import EmailDataTable

class DataTable(tables.Table):
    File = tables.Column(attrs={
        'td' : {
            "onClick": lambda record: "document.location.href='{0}';".format(record.File)
        }
    })
    To = tables.TemplateColumn('<data-toggle="tooltip" title="{{record.To}}">{{record.To|truncatewords:3}}')
    From = tables.Column(attrs={
        'td' : {
            "onClick": lambda record: "document.location.href='user/{0}';".format(record.From)
        }
    })
    Body = tables.TemplateColumn('<data-toggle="tooltip" title="{{record.Body}}">{{record.Body|truncatewords:10}}')
    preds_rf = tables.Column(verbose_name="Prediction")
    topic = tables.Column()
    class Meta:
        attrs = {"class": "table email_table"}
        model =EmailDataTable
        template_name = "django_tables2/bootstrap.html"
        exclude = ("message", "count", "lemma", "ManualClassify", "ManualReason","IsPersonal","percentage","category")
