from unittest import mock
from unittest.mock import patch, PropertyMock
from django.test import TestCase, Client
from django.urls import reverse

from account.models import User
from .backend.rollershutter import Rollershutter


def create_users():
    # Create superuser
    user_staff = User.objects.create_superuser(username="fake_admin",
                                               email='fake_admin_mail@email.com')
    user_staff.set_password('fake_admin_password')
    user_staff.save()

    user = User.objects.create(username="fake_user",
                               email='fake_mail@email.com')
    user.set_password('fake_password')
    user.save()
    return user, user_staff


class NetworkViewTestCase(TestCase):
    def setUp(self):
        self.user, self.user_staff = create_users()

    def test_network_view(self):
        # If staff not authenticate -> redirect
        client = Client()
        response = client.get(reverse('homecenter:network'))
        client.force_login(self.user)
        self.assertEqual(response.status_code, 302)
        # Authenticate staff member
        client = Client()
        client.force_login(self.user_staff)
        response = client.get(reverse('homecenter:network'))
        self.assertEqual(response.status_code, 200)

    def test_ajax_Json_response_zwave_off_sw_state_on(self, *args, **kwargs):
        with mock.patch('homecenter.views.zwave') as zwave_patched:
            zwave_patched.network.is_ready = False
            client = Client()
            client.force_login(self.user_staff)
            # Test ajax request
            response = client.post(
                reverse('homecenter:network'), {'state': 'On'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), {
                    'nw_text_state': 'démarré !',
                    'messages': {'success': 'Le réseau z-wave est démarré !'}
                }
            )

    def test_ajax_Json_response_zwave_on_sw_state_off(self, *args, **kwargs):
        with mock.patch('homecenter.views.zwave') as zwave_patched:
            zwave_patched.network.is_ready = True
            client = Client()
            client.force_login(self.user_staff)
            # Test ajax request
            response = client.post(reverse('homecenter:network'),
                                   {'state': 'Off'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(),
                             {'nw_text_state': 'arrêté !',
                              'messages': {
                                  'success': 'Le réseau z-wave est arrêté !'}
                              }
                             )


class RollerShutterViewTestCase(TestCase):
    def setUp(self):
        self.user, self.user_staff = create_users()

    def test_roller_shutter_view(self):
        # If not authenticate -> redirect
        client = Client()
        response = client.get(reverse('homecenter:roller_shutter'))
        self.assertEqual(response.status_code, 302)
        # If authenticate -> display view
        client = Client()
        client.force_login(self.user)
        response = client.get(reverse('homecenter:roller_shutter'))
        self.assertEqual(response.status_code, 200)

    def test_roller_shutter_network_not_ready(self):
        with mock.patch('homecenter.views.zwave') as zwave_patched:
            zwave_patched.network.is_ready = False
            client = Client()
            client.force_login(self.user)
            response = client.post(reverse('homecenter:roller_shutter'),
                                   {'node_id': '2',
                                    'setLevel': 50,
                                    'stop': '0',
                                    'direction': '1'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.json(),
                             {'nw_state': 'Off',
                              'messages': {'warning':
                                               "Le réseau z-wave est à l'arrêt !"}})

    @mock.patch.object(Rollershutter, 'stop')
    def test_roller_shutter_stop_direction_0(self, mock_stop):
        with mock.patch('homecenter.views.zwave') as zwave_patched:
            zwave_patched.network.is_ready = True
            client = Client()
            client.force_login(self.user)
            mock_stop.return_value = ("Le volet a été stoppé !.", 60)
            response = client.post(reverse('homecenter:roller_shutter'),
                                   {'node_id': '2',
                                    'setLevel': 60,
                                    'stop': '1',
                                    'direction': '0'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.json(),
                             {'messages': {'success': 'Le volet a été stoppé !.'},
                              'level': 60})

    @mock.patch.object(Rollershutter, 'stop')
    def test_roller_shutter_stop_direction_1(self, mock_stop):
        with mock.patch('homecenter.views.zwave') as zwave_patched:
            zwave_patched.network.is_ready = True
            client = Client()
            client.force_login(self.user)
            mock_stop.return_value = ("Le volet a été stoppé !.", 50)
            response = client.post(reverse('homecenter:roller_shutter'),
                                   {'node_id': '2', 'setLevel': 50,
                                    'stop': '1', 'direction': '1'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.json(),
                             {'messages': {'success': 'Le volet a été stoppé !.'},
                              'level': 50})


class NodesConfigViewTestCase(TestCase):
    def setUp(self):
        self.user, self.user_staff = create_users()

    def test_nodes_config_view(self):
        # If staff not authenticate -> redirect
        client = Client()
        response = client.get(reverse('homecenter:nodes_config'))
        client.force_login(self.user)
        self.assertEqual(response.status_code, 302)
        # Authenticate staff member
        client = Client()
        client.force_login(self.user_staff)
        response = client.get(reverse('homecenter:nodes_config'))
        self.assertEqual(response.status_code, 200)


class TestLightViewTestCase(TestCase):
    def setUp(self):
        self.user, self.user_staff = create_users()

    def test_light_view(self):
        # If not authenticate -> redirect to login
        client = Client()
        response = client.get(reverse('homecenter:light'))
        self.assertEqual(response.status_code, 302)
        # If authenticate -> display view
        client = Client()
        client.force_login(self.user)
        response = client.get(reverse('homecenter:light'))
        self.assertEqual(response.status_code, 200)
