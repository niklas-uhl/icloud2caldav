import sys
import requests
import xmltodict
from pathlib import Path
import getpass
import xml.etree.ElementTree as ET

user = input('AppleID: ')
pwd = getpass.getpass()
auth = (user, pwd)

webdav_options = """<propfind xmlns='DAV:'>
                        <prop>
                            <current-user-principal/>
                        </prop>
                    </propfind>"""

r = requests.request('PROPFIND', 'https://caldav.icloud.com/',
                     auth=auth,
                     data=webdav_options
                     )
if not r.ok:
    sys.stderr.write("Your credentials are incorrect!")
    sys.exit(1)

print('Your calendars:')

xml_dict = xmltodict.parse(r.text, dict_constructor=dict)
href = xml_dict['multistatus']['response']['propstat']['prop']['current-user-principal']['href']['#text']
webdav_options = """<propfind xmlns='DAV:' xmlns:cd='urn:ietf:params:xml:ns:caldav'>
                        <prop>
                            <cd:calendar-home-set/>
                        </prop>
                    </propfind>"""
url = 'https://caldav.icloud.com' + href
r = requests.request('PROPFIND', url,
                     auth=auth,
                     data=webdav_options
                     )
xml_dict = xmltodict.parse(r.text, dict_constructor=dict)
url = xml_dict['multistatus']['response']['propstat']['prop']['calendar-home-set']['href']['#text']
webdav_options = """<propfind xmlns='DAV:'>
                        <prop>
                            <displayname/>
                        </prop>
                    </propfind>"""

r = requests.request('PROPFIND', url,
                     auth=auth,
                     headers={'Depth': '1'},
                     data=webdav_options
                     )
for response in xmltodict.parse(r.text, dict_constructor=dict)['multistatus']['response'][1:]:
    href = response['href']
    propstat = response['propstat']
    if isinstance(propstat, list):
        continue
    name = propstat['prop']['displayname']['#text']
    print(name, url + Path(href).parts[3])
