import sys, os

webapp_path = os.getcwd()+'/../crustwebapp/'
sys.path.append(webapp_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crustwebapp.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from remoteusers.models import RemoteUser

ru_obj =  RemoteUser.objects.get(id=1)
print ru_obj.username, ru_obj.password
