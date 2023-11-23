import sys
import site

python_home = '/home/smarthmdhub/api/venv'
python_version = '.'.join(map(str, sys.version_info[:2]))
site_packages = python_home + '/lib/python%s/site-packages' % python_version
# print('site_packages:' + site_packages)
site.addsitedir(site_packages)

prev_sys_path = list(sys.path)
site.addsitedir(site_packages)
new_sys_path = []

for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)

sys.path[:0] = new_sys_path
