from django.core.urlresolvers import reverse
from django.test import TestCase

#from oscar.apps.dashboard.orders.tests import *
#from oscar.apps.dashboard.reports.tests import *
#from oscar.apps.dashboard.users.tests import *
#from oscar.apps.dashboard.promotions.tests import *
#from oscar.apps.dashboard.catalogue.tests import *

from django.contrib.flatpages.models import FlatPage

from oscar.test import ClientTestCase

from oscar.apps.dashboard.pages import views


class AnonymousUserTests(ClientTestCase):

    def test_login_form_is_displayed_for_anon_user(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertTrue('Username' in response.content)


class PagesViewTest(ClientTestCase):
    is_anonymous = False
    is_staff = True

    def test_dashboard_index_is_for_staff_only(self):
        response = self.client.get(reverse('dashboard:page-list'))
        self.assertTrue('Password' not in response.content)

    def test_dashboard_page_list(self):
        fp1 = FlatPage(title='title1', url='/url1/', content='some content')
        fp1.save()

        fp2 = FlatPage(title='title2', url='/url2/', content='other content')
        fp2.save()

        response = self.client.get(reverse('dashboard:page-list'))
        objects = response.context[-1]['object_list']

        self.assertTrue(fp1 in objects)
        self.assertTrue(fp2 in objects)

    def test_dashboard_create_pages(self):
        ## make sure no flatpages exist
        self.assertEquals(FlatPage.objects.count(), 0)

        ## check that no page is created for existing URL
        response = self.client.post('/dashboard/pages/', data={
                                        'title': 'test', 
                                        'url': '/dashboard/pages/',
                                    }, follow=True)
        self.assertEquals(FlatPage.objects.count(), 0)

        ## check creating a new page with custome URL
        response = self.client.post('/dashboard/pages/create/', data={
                                        'title': 'Test Page', 
                                        'url': '/test/page/', 
                                        'content': "<h1> Content </h1>"
                                    }, follow=True)

        self.assertEquals(FlatPage.objects.count(), 1)
        page = FlatPage.objects.all()[0]
        self.assertEquals(page.title, 'Test Page')
        self.assertEquals(page.url, '/test/page/')
        self.assertEquals(page.content, "<h1> Content </h1>")
        self.assertEquals(page.sites.count(), 1)

        ## check creating page with slugified URL 
        response = self.client.post('/dashboard/pages/create/', data={
                                        'title': 'New Page', 'content': ""
                                    }, follow=True)

        self.assertEquals(FlatPage.objects.count(), 2)
        page = FlatPage.objects.all()[0]
        self.assertEquals(page.title, 'New Page')
        self.assertEquals(page.url, '/new-page/')
        self.assertEquals(page.content, "")
        self.assertEquals(page.sites.count(), 1)

        ## check creating page with existing URL does not work
        response = self.client.post('/dashboard/pages/create/', data={
                                        'title': 'New Page', 'content': ""
                                    }, follow=True)

        self.assertEquals(FlatPage.objects.count(), 2)

    def test_dashboard_update_page_valid_url(self):
        fp1 = FlatPage(title='title1', url='/url1/', content='some content')
        fp1.save()
        fp2 = FlatPage(title='title2', url='/url2/', content='other content')
        fp2.save()

        ## check if overwriting all properties works 
        response = self.client.post('/dashboard/pages/update/1/', data={
                                        'title': 'Test Page', 
                                        'url': '/test/page/', 
                                        'content': "<h1> Content </h1>"
                                    }, follow=True)

        self.assertEquals(FlatPage.objects.count(), 2)
        
        page = FlatPage.objects.get(pk=1)
        self.assertEquals(page.title, 'Test Page')
        self.assertEquals(page.url, '/test/page/')
        self.assertEquals(page.content, "<h1> Content </h1>")
        self.assertEquals(page.sites.count(), 1)

    def test_dashboard_update_page_invalid_url(self):
        fp1 = FlatPage(title='title1', url='/url1/', content='some content')
        fp1.save()
        fp2 = FlatPage(title='title2', url='/url2/', content='other content')
        fp2.save()

        ## check changing to an invalid urls does not work
        response = self.client.post('/dashboard/pages/update/1/', data={
                                        'title': 'Test Page', 
                                        'url': '/url2/', 
                                        'content': "<h1> Content </h1>"
                                    }, follow=True)

        self.assertEquals(FlatPage.objects.count(), 2)
        
        page = FlatPage.objects.get(pk=1)
        self.assertEquals(page.title, 'title1')
        self.assertEquals(page.url, '/url1/')
        self.assertEquals(page.content, "some content")

    def test_dashboard_delete_pages(self):
        fp1 = FlatPage(title='title1', url='/url1/', content='some content')
        fp1.save()
        fp2 = FlatPage(title='title2', url='/url2/', content='other content')
        fp2.save()

        ## check if overwriting all properties works 
        response = self.client.post('/dashboard/pages/delete/1/', follow=True)

        self.assertEquals(FlatPage.objects.count(), 1)
        
        page = FlatPage.objects.get(pk=2)
        self.assertEquals(page.title, 'title2')
        self.assertEquals(page.url, '/url2/')
        self.assertEquals(page.content, "other content")

