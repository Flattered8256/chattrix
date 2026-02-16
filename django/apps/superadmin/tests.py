from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()


class SuperAdminUserTests(TestCase):
    """超级管理员用户管理功能测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建普通用户
        self.normal_user = User.objects.create_user(
            username='normaluser',
            password='testpass123'
        )
        
        # 创建超级管理员用户
        self.superuser = User.objects.create_superuser(
            username='superadmin',
            password='testpass123'
        )
        
        # 创建测试用户
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # 初始化API客户端
        self.client = APIClient()
        
        # 用户管理URL
        self.user_list_url = reverse('user-list')
        self.user_detail_url = lambda pk: reverse('user-detail', args=[pk])
    
    def test_normal_user_cannot_access(self):
        """测试普通用户无法访问用户管理功能"""
        # 登录普通用户
        self.client.force_authenticate(user=self.normal_user)
        
        # 尝试获取用户列表
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 403)
        
        # 尝试获取用户详情
        response = self.client.get(self.user_detail_url(self.test_user.id))
        self.assertEqual(response.status_code, 403)
    
    def test_superuser_can_access(self):
        """测试超级管理员可以访问用户管理功能"""
        # 登录超级管理员
        self.client.force_authenticate(user=self.superuser)
        
        # 尝试获取用户列表
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('用户列表获取成功', response.data['message'])
    
    def test_get_user_list(self):
        """测试获取用户列表功能"""
        # 登录超级管理员
        self.client.force_authenticate(user=self.superuser)
        
        # 获取用户列表
        response = self.client.get(self.user_list_url)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertIsInstance(response.data['data'], list)
        
        # 验证返回的数据结构
        if response.data['data']:
            user_data = response.data['data'][0]
            self.assertIn('id', user_data)
            self.assertIn('username', user_data)
            self.assertIn('user_avatar', user_data)
            self.assertIn('date_joined', user_data)
    
    def test_update_user(self):
        """测试更新用户信息功能"""
        # 登录超级管理员
        self.client.force_authenticate(user=self.superuser)
        
        # 准备更新数据
        update_data = {
            'username': 'updateduser'
        }
        
        # 发送更新请求
        response = self.client.put(self.user_detail_url(self.test_user.id), update_data, format='json')
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('用户信息更新成功', response.data['message'])
        self.assertEqual(response.data['data']['username'], 'updateduser')
        
        # 验证数据库中的数据是否更新
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, 'updateduser')
    
    def test_delete_user(self):
        """测试删除用户功能"""
        # 登录超级管理员
        self.client.force_authenticate(user=self.superuser)
        
        # 发送删除请求
        response = self.client.delete(self.user_detail_url(self.test_user.id))
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('用户删除成功', response.data['message'])
        
        # 验证用户是否被删除
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.test_user.id)
    
    def test_create_user_via_database(self):
        """测试通过数据库操作创建用户"""
        # 直接通过数据库创建用户
        new_user = User.objects.create_user(
            username='newuser',
            password='testpass123'
        )
        
        # 验证用户是否创建成功
        self.assertIsInstance(new_user, User)
        self.assertEqual(new_user.username, 'newuser')
        self.assertFalse(new_user.is_superuser)
        
        # 登录超级管理员
        self.client.force_authenticate(user=self.superuser)
        
        # 验证新创建的用户是否出现在列表中
        response = self.client.get(self.user_list_url)
        usernames = [user['username'] for user in response.data['data']]
        self.assertIn('newuser', usernames)
