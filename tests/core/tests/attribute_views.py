import django
from django.core.files.base import ContentFile
from django.test import TestCase
from django.test.client import MULTIPART_CONTENT, RequestFactory

from tastypie.exceptions import BadRequest

from .resources import NullableMediaBitResource
from core.models import Note, MediaBit

class FileUploadTestCase(TestCase):
    fixtures = ['note_testdata.json']
    urls = 'core.tests.field_urls'

    def setUp(self):
        super(FileUploadTestCase, self).setUp()
        
        self.note_1 = Note.objects.get(pk=1)
        
        self.mb_1 = self.note_1.media_bits.all()[0]

        if django.VERSION >= (1, 4):
            self.body_attr = "body"
        else:
            self.body_attr = "raw_post_data"

    def test_successful_upload_multipart(self):
        data = {
            'file': ContentFile('some fake data', name='foo.png'),
        }
        
        resource = NullableMediaBitResource()
        
        rf = RequestFactory()
        
        request = rf.put('/', rf._encode_data(data, MULTIPART_CONTENT), content_type=MULTIPART_CONTENT)
        
        resp = resource.dispatch_attribute(request, pk=self.mb_1.pk, attribute='image')
        
        self.assertEqual(resp.status_code, 200)

    def test_successful_upload_request_body(self):
        data = 'some fake data'
        
        resource = NullableMediaBitResource()
        
        rf = RequestFactory()
        
        request = rf.put('/', data, content_type='image/png')
        
        resp = resource.dispatch_attribute(request, pk=self.mb_1.pk, attribute='image')
        
        self.assertEqual(resp.status_code, 200)

    def test_404_upload_request_body_nonexistant_field(self):
        data = 'some fake data'
        
        resource = NullableMediaBitResource()
        
        rf = RequestFactory()
        
        request = rf.put('/', data, content_type='image/png')
        
        resp = resource.dispatch_attribute(request, pk=self.mb_1.pk, attribute='nonexistantfield')
        
        self.assertEqual(resp.status_code, 404)

    def test_400_upload_request_body_missing_file(self):
        data = {}
        
        resource = NullableMediaBitResource()
        
        rf = RequestFactory()
        
        request = rf.put('/', rf._encode_data(data, MULTIPART_CONTENT), content_type=MULTIPART_CONTENT)
        
        with self.assertRaises(BadRequest):
            resp = resource.dispatch_attribute(request, pk=self.mb_1.pk, attribute='image')

