import io
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase 
from apps.accounts.models import User
import random
import string
from django.core.files.uploadedfile import SimpleUploadedFile
def generate_random_registration_data():
    # 生成随机用户名
    username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    # 生成随机密码
    password_length = 12
    password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=password_length))
    
    return {
        'username': username,
        'password': password,
        'password_confirm': password
    }


class UserRegistrationTests(APITestCase):
    """测试用户注册功能，遵循单一职责原则"""
    def setUp(self):
        self.registration_data = generate_random_registration_data()
    def test_user_registration_success(self):
        """测试使用有效数据注册新用户"""
        
        response = self.client.post(reverse('register-list'), self.registration_data)
        self.assertEqual(response.status_code, 201)  # 假设返回201 Created
        self.assertTrue(User.objects.filter(username=self.registration_data['username']).exists())
    
    def test_user_registration_with_existing_username(self):
        """测试使用已存在的用户名注册"""
        # 创建一个现有用户
        
        User.objects.create_user(username=self.registration_data['username'], password=self.registration_data['password'])
        response = self.client.post(reverse('register-list'), self.registration_data)
        self.assertContains(response, '"A user with that username already exists.', status_code=400)
    
    def test_user_registration_missing_required_fields(self):
        """测试缺少必要字段的注册请求"""
        # 测试缺少用户名
        
        response = self.client.post(reverse('register-list'), username = '',password = self.registration_data['password'],password_confirm = self.registration_data['password_confirm'])
        self.assertContains(response, 'This field is required.', status_code=400)
        
        # 测试缺少密码
        
        response = self.client.post(reverse('register-list'), username = self.registration_data['username'])
        self.assertContains(response, 'This field is required.', status_code=400)

class UserLoginTests(APITestCase):
    def setUp(self):
        self.registration_data = generate_random_registration_data()
        # 真正创建用户
        User.objects.create_user(
            username=self.registration_data['username'],
            password=self.registration_data['password']
        )
        self.login_data = {
            'username': self.registration_data['username'],
            'password': self.registration_data['password']
        }

    def test_user_login_success(self):
        """测试用户登录成功"""
        response = self.client.post(
            reverse('login'),
            data=self.login_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Login successful')
        
    def test_miss_password_login_failure(self):
        """测试用户登录缺少密码"""
        response = self.client.post(
            reverse('login'),
            data={'username': self.login_data['username'], 'password': ''},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid data')
    def test_miss_username_login_failure(self):
        """测试用户不存在"""
        response = self.client.post(
            reverse('login'),
            data={'username':'gfgdgfd','password': self.login_data['password']},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['message'], '用户不存在')

class UserLogoutTests(APITestCase):
    def setUp(self):
        self.registration_data = generate_random_registration_data()
        # 创建用户
        self.user = User.objects.create_user(
            username=self.registration_data['username'],
            password=self.registration_data['password']
        )
        self.login_data = {
            'username': self.registration_data['username'],
            'password': self.registration_data['password']
        }
    
    def test_user_logout_success(self):
        """测试用户登出成功"""
        login_response = self.client.post(
        reverse('login'),
        data=self.login_data,
        format='json'
    )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['data']['access']

        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Logout successful')
    
    def test_user_logout_without_login(self):
        """测试用户未登录时登出"""
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['detail'], 'Authentication credentials were not provided.')

    def test_user_logout_with_invalid_token(self):
        """测试使用无效的token登出"""
        
        # 设置无效token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        # 发送请求
        response = self.client.post(reverse('logout'))
        
        # 验证结果
        self.assertEqual(response.status_code, 401)
        self.assertIn('Given token not valid for any token type', str(response.data['detail']))

class test_SearchUserView(APITestCase):
    def setUp(self):
        self.registration_data = generate_random_registration_data()
        self.registration_data_2 = generate_random_registration_data()
        # 创建用户
        self.user = User.objects.create_user(
            username=self.registration_data['username'],
            password=self.registration_data['password']
        )
        self.login_data = {
            'username': self.registration_data_2['username'],
            'password': self.registration_data_2['password']
        }
    
    def test_search_user_success(self):
        # 创建用于登录的用户
        User.objects.create_user(
            username=self.login_data['username'],
            password=self.login_data['password']
        )

        # 登录并获取 token
        login_response = self.client.post(
            reverse('login'),
            data=self.login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['data']['access']

        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 发送搜索请求
        response = self.client.get(
            reverse('search'),
            data={'id': self.user.id},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'User found')
    
    def test_search_user_not_found(self):
        """
        测试搜索用户不存在的情况
        """
        User.objects.create_user(
            username=self.login_data['username'],
            password=self.login_data['password']
        )
        # 登录并获取 token
        login_response = self.client.post(
            reverse('login'),
            data=self.login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['data']['access']

        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(
            reverse('search'),
            data={'id': 1234354584},
            format='json'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'User not found')

class test_Refresh(APITestCase):

    def setUp(self):
        self.registration_data = generate_random_registration_data()
        # 创建用户
        self.user = User.objects.create_user(
            username=self.registration_data['username'],
            password=self.registration_data['password']
        )
        self.login_data = {
            'username': self.registration_data['username'],
            'password': self.registration_data['password']
        }    
    def test_refresh_success(self):
 

        # 登录并获取 token
        login_response = self.client.post(
            reverse('login'),
            data=self.login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['data']['access']

        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.post(
            reverse('refresh'),
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "Token refreshed successfully")

    def test_refrech_failure(self):


        # 登录并获取 token
        self.client.post(
            reverse('login'),
            data=self.login_data,
            format='json'
        )


        response = self.client.post(
            reverse('refresh'),
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['detail'], "Authentication credentials were not provided.")

class test_User_get_ProfileView(APITestCase):
    def setUp(self):
        self.registration_data = generate_random_registration_data()
        # 创建用户
        self.user = User.objects.create_user(
            username=self.registration_data['username'],
            password=self.registration_data['password']
        )
        self.login_data = {
            'username': self.registration_data['username'],
            'password': self.registration_data['password']
        }  
    def test_user_get_profile(self):
                # 登录并获取 token
        login_response = self.client.post(
            reverse('login'),
            data=self.login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['data']['access']

        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(
                reverse('getprofile'),
                format='json'
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "Profile retrieved successfully")

        user_data = response.json().get('data', {})
        self.assertTrue(user_data.get('id'))
        self.assertTrue(user_data.get('username'))
        # self.assertTrue(user_data.get('user_avatar'))
        self.assertTrue(user_data.get('user_status'))

class test_User_set_ProfileView(APITestCase):
    def setUp(self):
        self.registration_data = generate_random_registration_data()
        # 创建用户
        self.user = User.objects.create_user(
            username=self.registration_data['username'],
            password=self.registration_data['password']
        )
        self.login_data = {
            'username': self.registration_data['username'],
            'password': self.registration_data['password']
        }  

    def test_user_set_username(self):

        login_response = self.client.post(
            reverse('login'),
            data=self.login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['data']['access']

        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.patch(
                reverse('profile'),
                data={'username': 'test_username'},
                format='json'
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "Profile updated successfully")  
        self.assertEqual(response.json()['data']['username'], 'test_username')    
    
    def test_user_set_avatar(self):
        # 登录获取token
        login_response = self.client.post(
            reverse('login'),
            data=self.login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 生成测试图片
        avatar = io.BytesIO()
        image = Image.new('RGBA', size=(50, 50), color=(256, 0, 0))
        image.save(avatar, 'png')
        avatar.seek(0)

        # 上传头像
        response = self.client.patch(
            reverse('profile'),
            data={'user_avatar': SimpleUploadedFile(
                'test_avatar.png', 
                avatar.getvalue(),
                content_type='image/png'
            )},
            format='multipart'
        )

        # 验证响应
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['message'], "Profile updated successfully")
        self.assertTrue(response_data['data'].get('user_avatar'))

    def test_user_set_id_fali(self):

        login_response = self.client.post(
            reverse('login'),
            data=self.login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['data']['access']

        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.patch(
                reverse('profile'),
                data={'id': 1234567890},
                format='json'
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['data']['id'][0], 'id 不可修改。')   # 校验错误字段里包含 id

    def test_user_set_user_status_fail(self):
        # 1. 登录拿 token
        login_response = self.client.post(
            reverse('login'),
            data=self.login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 2. 尝试 PATCH 修改 user_status
        response = self.client.patch(
            reverse('profile'),
            data={'user_status': 'any_new_value'},
            format='json'
        )

        # 3. 断言返回 400 且包含对应错误
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['data']['user_status'][0], 'user_status 不可修改。')
