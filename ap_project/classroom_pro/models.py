from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, role, department, password=None):
        print("Inside model:")
        print(email)
        print(name)
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # user = self.model(Email=email, Name=name, Role=role, Department=department, user_password=password)
        user = self.model(Email=email, Name=name, Role=role, Department=department)
        user.set_password(password)
        user.save(using=self._db)
        return user
class CustomUser(AbstractBaseUser):
    UserID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=255)
    Email = models.EmailField(unique=True)
    Role = models.CharField(max_length=30)
    Department = models.CharField(max_length=100, blank=True, null=True)
    #user_password = models.CharField(max_length=100)

    objects = CustomUserManager()

    USERNAME_FIELD = 'Email'
    EMAIL_FIELD = 'Email'

    #class Meta:
        #db_table = 'classroom_pro_CustomUser'


#class User(models.Model):
#    UserID = models.AutoField(primary_key=True)
#    Name = models.CharField(max_length=255)
#    Email = models.EmailField(unique=True)
#    Role = models.CharField(max_length=30)
#    Department = models.CharField(max_length=100, blank=True, null=True)  # Only for faculty
#    user_password = models.CharField(max_length=100)
#
#
#    def __str__(self):
#        return self.Name
#
class Room(models.Model):
    RoomID = models.AutoField(primary_key=True)
    RoomName = models.CharField(max_length=100)
    Facilities = models.CharField(max_length=255)
    Capacity = models.IntegerField()
    Location = models.CharField(max_length=100)

    def __str__(self):
        return self.RoomName

class RoomAvailability(models.Model):
    Room = models.ForeignKey(Room, on_delete=models.CASCADE)
    Date = models.DateField()
    TimeSlot = models.CharField(max_length=100)
    AvailabilityStatus = models.CharField(max_length=20, choices=[('available', 'Available'), ('booked', 'Booked')])

    class Meta:
        unique_together = ('Room', 'Date', 'TimeSlot')

class Booking(models.Model):
    BookingID = models.AutoField(primary_key=True)
    User = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    Room = models.ForeignKey(Room, on_delete=models.CASCADE)
    Date = models.DateField()
    TimeSlot = models.CharField(max_length=100)
    Status = models.CharField(max_length=100, default='pending')
    Comments = models.CharField(max_length=100, default='no comments')


    def __str__(self):
        return f"Booking {self.BookingID}"

class Approval(models.Model):
    ApprovalID = models.AutoField(primary_key=True)
    Booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    ApprovedBy = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ApprovalStatus = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    Comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Approval {self.ApprovalID}"