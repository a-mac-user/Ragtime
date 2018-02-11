from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email,
                                password=password,
                                name=name,
                                )
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    name = models.CharField(max_length=32)
    token = models.CharField(u'token', max_length=128, default=None, blank=True, null=True)
    department = models.CharField(u'部门', max_length=32, default=None, blank=True, null=True)
    tel = models.CharField(u'座机', max_length=32, default=None, blank=True, null=True)
    mobile = models.CharField(u'手机', max_length=32, default=None, blank=True, null=True)

    memo = models.TextField(u'备注', blank=True, null=True, default=None)
    date_joined = models.DateTimeField(blank=True, auto_now_add=True)
    valid_begin_time = models.DateTimeField(default=timezone.now)
    valid_end_time = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_perms(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        verbose_name = u'用户信息'
        verbose_name_plural = u"用户信息"

    def __unicode__(self):
        return self.name

    objects = UserManager()
