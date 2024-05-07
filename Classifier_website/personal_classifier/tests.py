from django.test import TestCase
from django.urls import reverse
import unittest


from .models import EmailDataTable
from personal_classifier.python_files import enron_classifier


# Create your tests here.
class YourTestClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        EmailDataTable.objects.create(
            File='test1.txt', To = 'To-test1',
            From='From-test1', Body='Test Test Test',
            message='Test-Test-Test', count=5,
            IsPersonal=1, category='Personal',
            lemma='test test test', preds_rf='Personal',
            topic='test', percentage=0.76,
            ManualClassify = 'Personal', ManualReason='Test'
        )

    def test_file_label(self):
        email = EmailDataTable.objects.get(File='test1.txt')
        field_label = email._meta.get_field('File').verbose_name
        self.assertEqual(field_label, 'File')

    def test_object_name_is_file_name(self):
        email = EmailDataTable.objects.get(File='test1.txt')
        expected_name = 'test1.txt'
        self.assertEqual(str(email), expected_name)

    def test_views_use_correct_templates(self):
        upload = self.client.get(reverse('upload_collection'))
        index = self.client.get(reverse('index'))
        search = self.client.get(reverse('search_collection'))
        detail = self.client.get('search/test/')
        graph = self.client.get(reverse('graph_collection'))
        user = self.client.get('search/user/test/')

        self.assertTemplateUsed(index, 'personal_classifier/index.html')
        self.assertEqual(index.status_code, 200)
        self.assertTemplateUsed(upload, 'personal_classifier/upload.html')
        self.assertEqual(upload.status_code, 200)
        self.assertTemplateUsed(search, 'personal_classifier/search.html')
        self.assertEqual(search.status_code, 200)
        self.assertTemplateUsed(graph, 'personal_classifier/graphs.html')
        self.assertEqual(graph.status_code, 200)


class Testing(unittest.TestCase):
    
    def test_preprocess(self):
        email = 'C:/Users/Lewis/University/identifying-and-protecting-personal-information-in-email-search/Classifier_website/personal_classifier/test emails/176675.txt'
        preprocess = enron_classifier.preprocess(email)
        self.assertEqual({
            'File': 'C:/Users/Lewis/University/identifying-and-protecting-personal-information-in-email-search/Classifier_website/personal_classifier/test emails/176675.txt',
            'From': 'steven.kean@enron.com',
            'IsPersonal': 1,
            'To': 'john.lavorato@enron.com',
            'body': 'Please call me.',
            'count': 2,
            'message': ['please', 'call', 'me', '.']
        },preprocess)

    def test_lemmatize(self):
        message  = ['please', 'call', 'me', '.']
        lemmatize = enron_classifier.lemmatize(message)
        self.assertEqual('please call me .',lemmatize)
        
    def test_main(self):
        try:
            test1, test2, test3, test4, test5 = enron_classifier.main()
        except Exception:
            self.fail("main failed")