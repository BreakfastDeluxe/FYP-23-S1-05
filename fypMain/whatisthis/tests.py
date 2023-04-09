from django.test import TestCase
from django.core.files import File
from .models import *
from .views import *
from .validators import *
from django.test.client import RequestFactory

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
    #test if customUser is auto created along with user, default values init correctly
    def test_customUser(self):
        testUser = User.objects.get(username='testuser')
        #check default score
        self.assertEquals(testUser.customuser.score, 0)
        #check default pin
        self.assertEquals(testUser.customuser.pin, '000000')
#testing views and associated URL pairings
class DisplayViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        self.task = Task.objects.create(task_complete = 0, created_by_id = self.user.id, task_keyword = 'test_keyword')
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
    #test gallery & search view
    def test_call_view_load_gallery(self):
        response = self.client.get('/history', follow=True)
        self.assertRedirects(response, '/login/?next=/history')
        self.client.login(username='testuser', password='12345!a')
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history.html')
        response = self.client.post('/history', {'search_query' : 'testSearch'})
        self.assertEqual(response.status_code, 200)
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
    #test manage_tasks view
    def test_call_view_manage_tasks(self):
        self.client.login(username='testuser', password='12345!a')
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks.html')

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
        print('Not Blur 1: ' + str(blur_value1))
        #check if exists
        self.assertIsNotNone(blur_value1)
        #check type = str
        self.assertIsInstance(blur_value1, int)
        
        imageTest_image_2 = Image.objects.get(upload_Image = 'images/unitTestImage2.jpg')
        blur_value2 = blur_check(imageTest_image_2.upload_Image.url)
        print('Is Blur 2: ' + str(blur_value2))
        #check if exists
        self.assertIsNotNone(blur_value2)
        #check type = str
        self.assertIsInstance(blur_value2, int)
        
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
        
#test the fizesize validation function
class ValidateFilesizeTestCase(TestCase):
    
    def test_filesize_validation(self):
        testfile1 = File
        testfile1.size = 10485760 # <1MB
        self.assertIs(validate_file_size(testfile1), File)
        testfile2 = File
        testfile2.size = 10585760 # >1MB
        self.assertRaises(ValidationError, validate_file_size, testfile2)
        
#test the delete_image function        
class DeleteImageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage1.jpg')
        
    def test_delete_image(self):
        imageTest_image_1 = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        self.assertIsNotNone(imageTest_image_1)
        image_id = imageTest_image_1.id
        #print(image_id)
        response = self.client.post('/delete_image', {'image_id' : image_id})
        #print(response.status_code)
        self.assertFalse(Image.objects.filter(upload_Image = 'images/unitTestImage1.jpg').exists())
        
#test the Task Model        
class TaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        self.task = Task.objects.create(task_complete = 0, created_by_id = self.user.id, task_keyword = 'test_keyword')
    
    def testTaskData(self):
        taskTest1 = Task.objects.get(id=1)
        self.assertEquals(taskTest1.task_complete, 0)
        self.assertIsInstance(taskTest1.task_complete, int)
        self.assertEquals(taskTest1.task_keyword, 'test_keyword')
        self.assertIsInstance(taskTest1.task_keyword, str)

#test the function that checks if uploaded image keyword matches current task keyword requirement        
class CompleteTaskTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        self.task = Task.objects.create(task_complete = 0, created_by_id = self.user.id, task_keyword = 'test_keyword')
        
    def test_complete_task(self):
        login = self.client.login(username='testuser', password='12345!a')
        request = self.factory.get('/upload_image')#create a HTTP request
        request.user = self.user#set the HTTP request user variable to current user
        taskTest1 = Task.objects.get(id=1)
        #false positive test, should not trigger completion
        self.assertEquals(check_task_completion('different_keyword', request), 0)
        #positive test, should trigger completion
        self.assertEquals(check_task_completion('test_keyword', request), 1)

#test the caption rating system        
class RateCaptionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345!a')
        login = self.client.login(username='testuser', password='12345!a')
        Image.objects.create(created_by = self.user, upload_Image = 'images/unitTestImage1.jpg')
        
    def test_rate_caption(self):
        testImage = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        
        #test if init rating is 0
        self.assertEquals(testImage.rating, 0)
        rate_caption(testImage.id, '1') #rate caption positively
        testImage = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        self.assertEquals(testImage.rating, 1)
        rate_caption(testImage.id, '0') #rate caption negatively
        testImage = Image.objects.get(upload_Image = 'images/unitTestImage1.jpg')
        self.assertEquals(testImage.rating, -1)