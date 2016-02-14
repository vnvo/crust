import ldap
from ldap.controls import SimplePagedResultsControl
ldap.set_option(ldap.OPT_REFERRALS, 0)


SERVER_IP = '172.16.28.12'
CRUST_LDAP_USER = 'Crust LDAP'
CRUST_LDAP_PASS = 'ra7Kie9gah@p'
BASE_DN = 'DC=asiatech,DC=net'
SEARCH_BY_SAMACCOUNT_FILTER = '(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))'


from distutils import version
if version.StrictVersion('2.4.0') <= version.StrictVersion(ldap.__version__):
    LDAP_CONTROL_PAGED_RESULTS = ldap.CONTROL_PAGEDRESULTS
else:
    LDAP_CONTROL_PAGED_RESULTS = ldap.LDAP_CONTROL_PAGE_OID


class MySimplePagedResultsControl(SimplePagedResultsControl):
    """
        Python LDAP 2.4 and later breaks the API. This is an abstraction class
        so that we can handle either.
    """

    def __init__(self, page_size=0, cookie=''):
        if version.StrictVersion('2.4.0') <= version.StrictVersion(ldap.__version__):
            SimplePagedResultsControl.__init__(
                    self,
                    size=page_size,
                    cookie=cookie)
        else:
            SimplePagedResultsControl.__init__(
                    self,
                    LDAP_CONTROL_PAGED_RESULTS,
                    critical,
                    (page_size, ''))

    def cookie(self):
        if version.StrictVersion('2.4.0') <= version.StrictVersion(ldap.__version__):
            return self.cookie
        else:
            return self.controlValue[1]

    def size(self):
        if version.StrictVersion('2.4.0') <= version.StrictVersion(ldap.__version__):
            return self.size
        else:
            return self.controlValue[0]


def ldap_get_user_cn(samaccount):
    try:
        ldap_obj = ldap.open(SERVER_IP)
        lc = MySimplePagedResultsControl(1000,'')
        ldap_obj.bind_s(CRUST_LDAP_USER, CRUST_LDAP_PASS)
        ldap_result_id = ldap_obj.search_ext(
                            BASE_DN, ldap.SCOPE_SUBTREE, SEARCH_BY_SAMACCOUNT_FILTER%samaccount,
                            attrlist = ('samaccountname', 'displayname', 'department'),
                            serverctrls=[lc])
        #while True:
        result_type, result_data, rmsgid, serverctrls = ldap_obj.result3(ldap_result_id)
        #for item in result_data:
        if result_data and result_data[0][0]:
            print result_type, result_data
            result_data = result_data[0]
            return result_data[1].get('displayName')

    except Exception as e:
        print e

    return None


def ldap_authenticate_user(samaccount, user_cn, password):
    try:
        ldap_obj = ldap.open(SERVER_IP)
        ldap_obj.bind_s(user_cn, password)
        return True
    except:
        pass

    return False
