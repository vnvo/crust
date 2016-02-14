from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from auth_lib.auth_helpers import ldap_get_user_cn



class RemoteUser(models.Model):
    username = models.CharField(max_length=256, unique=True)
    password = models.CharField(max_length=1024)
    auth_mode = models.CharField(max_length=32, blank=True, null=True, default='local')
    sshv2_public_key = models.TextField(blank=True)
    is_locked = models.BooleanField(default=False)
    email = models.CharField(max_length=256, blank=True)
    cell_phone = models.CharField(max_length=256, blank=True)
    comment = models.TextField(blank=True, default='')
    allow_ip = models.TextField(blank=True, null=True)
    ldap_cn = models.CharField(max_length=512, blank=True, null=True)


@receiver(post_save, sender=RemoteUser, dispatch_uid="update_ldapcn")
def update_ldapcn(sender, instance, **kwargs):
    print 'update_ldapcn', instance
    if instance.auth_mode == 'ldap':
        user_cn = ldap_get_user_cn(instance.username)
        print user_cn
        if user_cn:
            RemoteUser.objects.filter(id=instance.id).update(ldap_cn=user_cn[0])
