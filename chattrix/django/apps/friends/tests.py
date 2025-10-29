import random
import string
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from apps.accounts.models import User
from apps.friends.models import Friend, FriendBlock, FriendGroup, FriendGroupMembership, FriendNickname, FriendRequest
# Create your tests here.
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

class FriendTests(TestCase):
    def setUp(self):
        self.user1_data = generate_random_registration_data()
        self.user2_data = generate_random_registration_data()

        self.user1 = User.objects.create_user(
            username=self.user1_data['username'],
            password=self.user1_data['password']
        )
        self.user2 = User.objects.create_user(
            username=self.user2_data['username'],
            password=self.user2_data['password']
        )
        
    def test_friend_success(self):
        # 测试创建好友关系
        friend_relation = Friend.objects.create(
            owner=self.user1,
            friend=self.user2
        )
        
        # 验证好友关系已创建
        self.assertEqual(friend_relation.owner, self.user1)
        self.assertEqual(friend_relation.friend, self.user2)
        self.assertIsNotNone(friend_relation.created_at)
        
        # 验证可以从owner获取好友关系
        owner_friends = Friend.objects.filter(owner=self.user1)
        self.assertIn(friend_relation, owner_friends)
        
        # 验证可以从friend获取被好友关系
        friend_of_relations = Friend.objects.filter(friend=self.user2)
        self.assertIn(friend_relation, friend_of_relations)
        
    def test_cannot_friend_oneself(self):
        # 测试不能添加自己为好友
        with self.assertRaises(Exception):
            Friend.objects.create(
                owner=self.user1,
                friend=self.user1
            )
            
    def test_unique_friend_constraint(self):
        # 测试唯一性约束
        Friend.objects.create(owner=self.user1, friend=self.user2)
        
        # 尝试创建重复的好友关系应该失败
        with self.assertRaises(Exception):
            Friend.objects.create(owner=self.user1, friend=self.user2)

class FriendRequestTests(TestCase):
    def setUp(self):
        self.user1_data = generate_random_registration_data()
        self.user2_data = generate_random_registration_data()

        self.user1 = User.objects.create_user(
            username=self.user1_data['username'],
            password=self.user1_data['password']
        )
        self.user2 = User.objects.create_user(
            username=self.user2_data['username'],
            password=self.user2_data['password']
        )

    def test_friend_request_creation(self):
        # 测试创建好友申请
        friend_request = FriendRequest.objects.create(
            sender=self.user1,
            receiver=self.user2
        )
        
        # 验证好友申请已创建
        self.assertEqual(friend_request.sender, self.user1)
        self.assertEqual(friend_request.receiver, self.user2)
        self.assertEqual(friend_request.status, 'pending')
        self.assertIsNotNone(friend_request.created_at)
        self.assertIsNotNone(friend_request.updated_at)
        
        # 验证可以通过关系获取申请
        sent_requests = FriendRequest.objects.filter(sender=self.user1)
        received_requests = FriendRequest.objects.filter(receiver=self.user2)
        self.assertIn(friend_request, sent_requests)
        self.assertIn(friend_request, received_requests)
        
    def test_cannot_send_request_to_self(self):
        # 测试不能向自己发送好友申请
        with self.assertRaises(Exception):
            FriendRequest.objects.create(
                sender=self.user1,
                receiver=self.user1
            )
            
    def test_unique_friend_request_constraint(self):
        # 测试唯一性约束（不能重复发送好友申请）
        FriendRequest.objects.create(
            sender=self.user1,
            receiver=self.user2
        )
        
        # 尝试再次发送相同的好友申请应该失败
        with self.assertRaises(Exception):
            FriendRequest.objects.create(
                sender=self.user1,
                receiver=self.user2
            )
            

    def test_friend_request_rejected_status(self):
        # 测试拒绝好友申请
        friend_request = FriendRequest.objects.create(
            sender=self.user1,
            receiver=self.user2
        )
        
        # 更新状态为已拒绝
        friend_request.status = 'rejected'
        friend_request.save()
        
        # 验证状态已更新为已拒绝
        updated_request = FriendRequest.objects.get(pk=friend_request.pk)
        self.assertEqual(updated_request.status, 'rejected')
        
    def test_friend_request_accepted_status(self):
        # 测试接受好友申请
        friend_request = FriendRequest.objects.create(
            sender=self.user1,
            receiver=self.user2
        )
        
        # 更新状态为已接受
        friend_request.status = 'accepted'
        friend_request.save()
        
        # 验证状态已更新为已接受
        updated_request = FriendRequest.objects.get(pk=friend_request.pk)
        self.assertEqual(updated_request.status, 'accepted')

    def test_friend_request_str_representation(self):
        # 测试好友申请的字符串表示
        friend_request = FriendRequest.objects.create(
            sender=self.user1,
            receiver=self.user2
        )
        
        expected_str = f'{self.user1} -> {self.user2} [pending]'
        self.assertEqual(str(friend_request), expected_str)

class FriendViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1_data = generate_random_registration_data()
        self.user2_data = generate_random_registration_data()
        
        self.user1 = User.objects.create_user(
            username=self.user1_data['username'],
            password=self.user1_data['password']
        )
        self.user2 = User.objects.create_user(
            username=self.user2_data['username'],
            password=self.user2_data['password']
        )
        self.client.force_authenticate(user=self.user1)
        
    def test_create_friend(self):
        # 测试创建好友关系
        friend_data = {
            'friend': self.user2.id
        }
        response = self.client.post(reverse('friend-list'), friend_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friend.objects.count(), 1)
        self.assertEqual(Friend.objects.get().owner, self.user1)
        self.assertEqual(Friend.objects.get().friend, self.user2)
        
    def test_get_friends_list(self):
        # 测试获取好友列表
        Friend.objects.create(owner=self.user1, friend=self.user2)
        response = self.client.get(reverse('friend-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_delete_friend(self):
        # 测试删除好友关系
        friend = Friend.objects.create(owner=self.user1, friend=self.user2)
        response = self.client.delete(reverse('friend-detail', kwargs={'pk': friend.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Friend.objects.count(), 0)

class FriendRequestViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1_data = generate_random_registration_data()
        self.user2_data = generate_random_registration_data()
        
        self.user1 = User.objects.create_user(
            username=self.user1_data['username'],
            password=self.user1_data['password']
        )
        self.user2 = User.objects.create_user(
            username=self.user2_data['username'],
            password=self.user2_data['password']
        )
        self.client.force_authenticate(user=self.user1)
        
    def test_create_friend_request(self):
        # 测试创建好友请求
        request_data = {
            'receiver': self.user2.id
        }
        response = self.client.post(reverse('friendrequest-list'), request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendRequest.objects.count(), 1)
        self.assertEqual(FriendRequest.objects.get().sender, self.user1)
        self.assertEqual(FriendRequest.objects.get().receiver, self.user2)
        self.assertEqual(FriendRequest.objects.get().status, 'pending')
        
    def test_cannot_send_request_to_self(self):
        # 测试不能向自己发送好友请求
        request_data = {
            'receiver': self.user1.id
        }
        response = self.client.post(reverse('friendrequest-list'), request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_get_friend_requests(self):
        # 测试获取好友请求列表
        FriendRequest.objects.create(sender=self.user2, receiver=self.user1)
        response = self.client.get(reverse('friendrequest-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # 由于sender是隐藏字段，所以我们检查receiver
        self.assertEqual(response.data[0]['receiver'], self.user1.id)
        self.assertEqual(response.data[0]['status'], 'pending')
        
    def test_accept_friend_request(self):
        # 测试接受好友请求
        friend_request = FriendRequest.objects.create(sender=self.user2, receiver=self.user1)
        # 切换用户身份
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(reverse('friendrequest-accept', kwargs={'pk': friend_request.id}))
        # 切换回原用户
        self.client.force_authenticate(user=self.user1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 用正确的用户接受请求
        response = self.client.post(reverse('friendrequest-accept', kwargs={'pk': friend_request.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friend_request.refresh_from_db()
        self.assertEqual(friend_request.status, 'accepted')
        
        # 验证好友关系已创建
        self.assertTrue(Friend.objects.filter(owner=self.user1, friend=self.user2).exists())
        self.assertTrue(Friend.objects.filter(owner=self.user2, friend=self.user1).exists())
        
    def test_reject_friend_request(self):
        # 测试拒绝好友请求
        friend_request = FriendRequest.objects.create(sender=self.user2, receiver=self.user1)
        response = self.client.post(reverse('friendrequest-reject', kwargs={'pk': friend_request.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friend_request.refresh_from_db()
        self.assertEqual(friend_request.status, 'rejected')

class FriendGroupViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = generate_random_registration_data()
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_friend_group(self):
        # 测试创建好友分组
        group_data = {
            'name': '测试分组'
        }
        response = self.client.post(reverse('friendgroup-list'), group_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendGroup.objects.count(), 1)
        self.assertEqual(FriendGroup.objects.get().owner, self.user)
        self.assertEqual(FriendGroup.objects.get().name, '测试分组')
        
    def test_get_friend_groups(self):
        # 测试获取好友分组列表
        FriendGroup.objects.create(owner=self.user, name='测试分组1')
        FriendGroup.objects.create(owner=self.user, name='测试分组2')
        response = self.client.get(reverse('friendgroup-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_get_group_members(self):
        # 测试获取分组成员
        group = FriendGroup.objects.create(owner=self.user, name='测试分组')
        friend = Friend.objects.create(owner=self.user, friend=User.objects.create_user(
            username='friend_user', password='friend_password'))
        FriendGroupMembership.objects.create(group=group, friend=friend)
        response = self.client.get(reverse('friendgroup-members', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class FriendGroupMembershipViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = generate_random_registration_data()
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.client.force_authenticate(user=self.user)
        self.group = FriendGroup.objects.create(owner=self.user, name='测试分组')
        self.friend = Friend.objects.create(owner=self.user, friend=User.objects.create_user(
            username='friend_user', password='friend_password'))
        
    def test_create_group_membership(self):
        # 测试创建分组成员关系
        membership_data = {
            'group': self.group.id,
            'friend': self.friend.id
        }
        response = self.client.post(reverse('friendgroupmembership-list'), membership_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendGroupMembership.objects.count(), 1)
        self.assertEqual(FriendGroupMembership.objects.get().group, self.group)
        self.assertEqual(FriendGroupMembership.objects.get().friend, self.friend)
        
    def test_cannot_add_others_friend_to_group(self):
        # 测试不能将别人的好友添加到自己的分组
        other_user = User.objects.create_user(username='other_user', password='other_password')
        other_friend = Friend.objects.create(owner=other_user, friend=User.objects.create_user(
            username='other_friend_user', password='other_friend_password'))
        membership_data = {
            'group': self.group.id,
            'friend': other_friend.id
        }
        response = self.client.post(reverse('friendgroupmembership-list'), membership_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class FriendNicknameViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = generate_random_registration_data()
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.client.force_authenticate(user=self.user)
        self.friend = Friend.objects.create(owner=self.user, friend=User.objects.create_user(
            username='friend_user', password='friend_password'))
        self.nickname_obj = FriendNickname.objects.create(friend=self.friend, nickname='')
        
    def test_update_friend_nickname(self):
        # 测试更新好友备注
        nickname_data = {
            'nickname': '好友备注'
        }
        response = self.client.patch(reverse('friendnickname-detail', kwargs={'pk': self.nickname_obj.id}), 
                                   nickname_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nickname_obj.refresh_from_db()
        self.assertEqual(self.nickname_obj.nickname, '好友备注')
        
    def test_cannot_update_others_friend_nickname(self):
        # 测试不能更新别人好友的备注
        other_user = User.objects.create_user(username='other_user', password='other_password')
        other_friend = Friend.objects.create(owner=other_user, friend=User.objects.create_user(
            username='other_friend_user', password='other_friend_password'))
        other_friend_nickname = FriendNickname.objects.create(friend=other_friend, nickname='')
        nickname_data = {
            'nickname': '错误备注'
        }
        response = self.client.patch(reverse('friendnickname-detail', kwargs={'pk': other_friend_nickname.id}), 
                                   nickname_data, format='json')
        # 因为我们无法访问不属于自己的FriendNickname对象，所以应该返回404而不是403
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class FriendBlockViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = generate_random_registration_data()
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.client.force_authenticate(user=self.user)
        self.friend = Friend.objects.create(owner=self.user, friend=User.objects.create_user(
            username='friend_user', password='friend_password'))
        self.block_obj = FriendBlock.objects.create(friend=self.friend, is_blocked=False)
        
    def test_block_friend(self):
        # 测试屏蔽好友
        block_data = {
            'is_blocked': True
        }
        response = self.client.patch(reverse('friendblock-detail', kwargs={'pk': self.block_obj.id}), 
                                   block_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.block_obj.refresh_from_db()
        self.assertTrue(self.block_obj.is_blocked)
        
    def test_cannot_block_others_friend(self):
        # 测试不能屏蔽别人的好友
        other_user = User.objects.create_user(username='other_user', password='other_password')
        other_friend = Friend.objects.create(owner=other_user, friend=User.objects.create_user(
            username='other_friend_user', password='other_friend_password'))
        other_friend_block = FriendBlock.objects.create(friend=other_friend, is_blocked=False)
        block_data = {
            'is_blocked': True
        }
        response = self.client.patch(reverse('friendblock-detail', kwargs={'pk': other_friend_block.id}), 
                                   block_data, format='json')
        # 因为我们无法访问不属于自己的FriendBlock对象，所以应该返回404而不是403
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
