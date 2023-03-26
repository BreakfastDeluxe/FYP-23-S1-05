from django.test import TestCase
from .models import *
from .views import *

# Create your tests here.

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        
    def test_user_login_success(self):
        login = self.client.login(username='testuser', password='12345!a')
        self.assertTrue(login)
        print('Login Success Test OK')
    
    def test_user_login_fail(self):
        login = self.client.login(username='testuser', password='wrongPass2')
        self.assertFalse(login)
        print('Login Fail Test OK')

class ImageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage1.jpg')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage2.jpg', caption = 'unitTestCaption2', keywords = 'unitTestCaption2')
        

    def test_image_data(self):
        imageTest_image_1 = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        print('Test case: ' + str(imageTest_image_1.upload_Image))
        self.assertEqual(str(imageTest_image_1.created_by), 'testuser')
        self.assertIsNotNone(imageTest_image_1.upload_Image)
        self.assertIsNone(imageTest_image_1.caption)
        self.assertIsNone(imageTest_image_1.keywords)
        
        imageTest_image_2 = Image.objects.get(upload_Image = 'images/unitTestImage2.jpg')
        print('Test case: ' + str(imageTest_image_2.upload_Image))
        self.assertEqual(str(imageTest_image_2.created_by), 'testuser')
        self.assertIsNotNone(imageTest_image_2.upload_Image)
        self.assertIsNotNone(imageTest_image_2.caption)
        print('Test caption: ' + str(imageTest_image_2.caption))
        self.assertIsNotNone(imageTest_image_2.keywords)
        print('Test keywords: ' + str(imageTest_image_2.keywords))

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
        self.assertIsNotNone(blur_value1)
        
        imageTest_image_2 = Image.objects.get(upload_Image = 'images/unitTestImage2.jpg')
        blur_value2 = blur_check(imageTest_image_2.upload_Image.url)
        print('Is Blur 2: ' + blur_value2)
        self.assertIsNotNone(blur_value2)
        
class KeywordGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage1.jpg')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage2.jpg')  
        
    def test_image_keywording(self):
        imageTest_image_1 = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        keywords = generate_keywords(imageTest_image_1.upload_Image.url)
        print('Keywords: ' + keywords)
        self.assertIsNotNone(keywords)
        
class PredictTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage1.jpg')
        
    def testPrediction(self):
        imageTest_image_1 = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        file = imageTest_image_1.upload_Image.url
        print("predict unit testing start")
        model_load = joblib.load('/Users/brandontan/Desktop/FYP/num2/FYP-23-S1-05/fypMain/whatisthis/MLmodel/cnn_model.joblib')
        print("Load model test:")
        self.assertIsNotNone(model_load)
        print("predict_image method test:")
        label = predict_image(file)
        print(label)
        self.assertIsNotNone(label)
        print('predict unit test end')