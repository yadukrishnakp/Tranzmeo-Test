from django.test import TestCase
from django.urls import reverse
from apps.lat_long.models import Ride
from apps.users.models import Users
from rest_framework import status
from rest_framework.test import APIClient


class RideRequestApiViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rider = Users.objects.create(username= "yadu", name= "yadukrishna", email= "yadu@yopmail.com", password= "123",is_active= True,user_type= "Rider")

    def test_create_ride_request(self):

        url = reverse('create-lat_long-request')
        data = {
            'pickup_latitude':'Your Pickup Latitude',
            'pickup_longitude':'Your Pickup Longitude',
            'dropoff_latitude':'Your Dropoff Latitude',
            'dropoff_longitude':'Your Dropoff Longitude'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Ride.objects.filter(status='Requested').exists())

    def test_update_ride_request(self):
        lat_long = Ride.objects.create(rider=self.rider, pickup_latitude='Your Pickup Latitude', pickup_longitude='Your Pickup Longitude', dropoff_latitude='Your Dropoff Latitude', dropoff_longitude='Your Dropoff Longitude', status='Requested')
        url = reverse('create-lat_long-request', kwargs={'pk': lat_long.id})
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 200)
        lat_long.refresh_from_db()
        self.assertEqual(lat_long.status, 'Accepted')
