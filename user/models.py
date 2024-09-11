from typing import Optional
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserProfileManager(BaseUserManager['UserProfile']):
    """ Manager for user profiles """

    def create_user(self, email: str, name: str, password: Optional[str]=None) -> 'UserProfile':
        """ Create a new user profile """
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user: UserProfile = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email: str, name: str, password: Optional[str]) -> 'UserProfile':
        """ Create a new superuser profile """
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """ Database model for users in the system """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self) -> str:
        """ Return string representation of our user """
        return self.email