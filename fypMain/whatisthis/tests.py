from django.test import TestCase
from .models import *
from .views import *

# Create your tests here.

#test the object models.User [from django.contrib.auth.models]
class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
    #test for login with correct credentials    
    def test_user_login_success(self):
        login = self.client.login(username='testuser', password='12345!a')
        self.assertTrue(login)
        print('Login Success Test OK')
    #test for login with incorrect credentials
    def test_user_login_fail(self):
        login = self.client.login(username='testuser', password='wrongPass2')
        self.assertFalse(login)
        print('Login Fail Test OK')
#testing views and associated URL pairings
class DisplayViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
    #test home view   
    def test_call_view_load_home(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200) #HTTP OK
        self.assertTemplateUsed(response, 'home.html')
    #test login view   
    def test_call_view_load_login(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    #test signup view   
    def test_call_view_load_login(self):
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')
    #test menu view
    def test_call_view_load_menu(self):
        response = self.client.get('/menu', follow=True)
        self.assertRedirects(response, '/login/?next=/menu')
        self.client.login(username='testuser', password='12345!a')
        response = self.client.get('/menu')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu.html')
    #test upload_image view
    def test_call_view_load_uploadImage(self):
        response = self.client.get('/upload_image', follow=True)
        self.assertRedirects(response, '/login/?next=/upload_image')
        self.client.login(username='testuser', password='12345!a')
        response = self.client.get('/upload_image')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload_image.html')
    #test user view
    def test_call_view_load_user(self):
        response = self.client.get('/user', follow=True)
        self.assertRedirects(response, '/login/?next=/user')
        self.client.login(username='testuser', password='12345!a')
        response = self.client.get('/user')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
    #test gallery view
    def test_call_view_load_gallery(self):
        response = self.client.get('/history', follow=True)
        self.assertRedirects(response, '/login/?next=/history')
        self.client.login(username='testuser', password='12345!a')
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history.html')
    #test logout view
    def test_call_view_load_logout(self):
        self.client.login(username='testuser', password='12345!a')
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)#HTTP FOUND (Redirect)
    #test change-password view
    def test_call_view_change_password(self):
        self.client.login(username='testuser', password='12345!a')
        response = self.client.get('/password-change/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')
    #test reset-password view
    def test_call_view_password_reset(self):
        self.client.login(username='testuser', password='12345!a')
        response = self.client.get('/password-reset/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset.html')

#test the object models.Image
class ImageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage1.jpg')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage2.jpg', caption = 'unitTestCaption2', keywords = 'unitTestCaption2')
        

    def test_image_data(self):
        imageTest_image_1 = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        print('Test case: ' + str(imageTest_image_1.upload_Image))
        #check type = Image object
        self.assertIsInstance(imageTest_image_1, Image)
        #check associated user correct?
        self.assertEqual(str(imageTest_image_1.created_by), 'testuser')
        #check imageURL exists
        self.assertIsNotNone(imageTest_image_1.upload_Image)
        #check caption does not exist
        self.assertIsNone(imageTest_image_1.caption)
        #check keyword does not exists
        self.assertIsNone(imageTest_image_1.keywords)
        
        imageTest_image_2 = Image.objects.get(upload_Image = 'images/unitTestImage2.jpg')
        print('Test case: ' + str(imageTest_image_2.upload_Image))
        self.assertEqual(str(imageTest_image_2.created_by), 'testuser')
        self.assertIsNotNone(imageTest_image_2.upload_Image)
        self.assertIsNotNone(imageTest_image_2.caption)
        print('Test caption: ' + str(imageTest_image_2.caption))
        self.assertIsNotNone(imageTest_image_2.keywords)
        print('Test keywords: ' + str(imageTest_image_2.keywords))

#test the function views.blur_check(file) expect return str
class BlurTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage1.jpg')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage2.jpg')      
       
    def test_image_blur(self):
        imageTest_image_1 = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        blur_value1 = blur_check(imageTest_image_1.upload_Image.url)
        print('Not Blur 1: ' + blur_value1)
        #check if exists
        self.assertIsNotNone(blur_value1)
        #check type = str
        self.assertIsInstance(blur_value1, str)
        
        imageTest_image_2 = Image.objects.get(upload_Image = 'images/unitTestImage2.jpg')
        blur_value2 = blur_check(imageTest_image_2.upload_Image.url)
        print('Is Blur 2: ' + blur_value2)
        #check if exists
        self.assertIsNotNone(blur_value2)
        #check type = str
        self.assertIsInstance(blur_value2, str)
        
#test the function views.generate_keywords(file) expect return str
class KeywordGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage1.jpg') 
        
    def test_image_keywording(self):
        imageTest_image_1 = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        keywords = generate_keywords(imageTest_image_1.upload_Image.url)
        print('Keywords: ' + keywords)
        #check if exists
        self.assertIsNotNone(keywords)
        #check type = str
        self.assertIsInstance(keywords, str)
        
#test the function views.generate_audio(text, file) expect return str
class AudioGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage2.jpg', caption = 'unitTestCaption2', keywords = 'unitTestCaption2')
        
    def test_audio_generation(self):
        imageTest_image_2 = Image.objects.get(upload_Image = 'images/unitTestImage2.jpg')
        image_path = imageTest_image_2.upload_Image.url
        caption = imageTest_image_2.caption
        audio_path = generate_audio(caption, image_path)
        print('Audio Path: ' + audio_path)
        #check if exists
        self.assertIsNotNone(audio_path)
        #check type = str
        self.assertIsInstance(audio_path, str)

#test the function views.generate_caption(file) expect return str        
class CaptionGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage1.jpg')
        
    def test_image_captioning(self):
        imageTest_image_1 = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        file = imageTest_image_1.upload_Image.url
        caption = generate_caption(file)
        print('Generated Caption: '+ caption)
        #check if exists
        self.assertIsNotNone(caption)
        #check type = str
        self.assertIsInstance(caption, str)
