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