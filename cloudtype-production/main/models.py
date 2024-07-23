from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from accounts.models import Cafe

class UserManager(BaseUserManager):
    def create_user(self, user_id, name, password=None, **extra_fields):
        if not user_id:
            raise ValueError('Users must have a user ID')
        user = self.model(user_id=user_id, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(user_id, name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_guest = models.BooleanField(default=False)

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.user_id

class Seat(models.Model):
    id = models.AutoField(primary_key=True)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    seat_status = models.CharField(max_length=20, choices=[('available', '사용 가능'), ('occupied', '사용중'), ('requesting', '예약 진행중'), ('reserved', '예약 완료')])
    plug = models.BooleanField(null=True, blank=True)
    backseat = models.BooleanField(null=True, blank=True)
    seat_start_time = models.DateTimeField(null=True, blank=True)
    seat_use_time = models.DateTimeField(null=True, blank=True)
    seats_no = models.IntegerField(null=True, blank=True)
    seats_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.cafe.cafe_name} - {self.seats_no}"

class Favorite(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE, related_name='reservations')
    cafe = models.ForeignKey(Cafe, to_field='id', on_delete=models.CASCADE, related_name='cafe_reservations')
    seat = models.ForeignKey(Seat, to_field='id', on_delete=models.CASCADE, related_name='reservations')
    reservation_time = models.DateTimeField(default=timezone.now)
    number_of_people = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.name} - {self.cafe.cafe_name} - {self.seat.seats_no}"
