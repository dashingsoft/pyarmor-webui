import glob
import logging
import json
import os
import shutil
import sys

from fnmatch import fnmatch

from pyarmor.pyarmor import (main as pyarmor_main, pytransform_bootstrap,
                             get_registration_code, query_keyinfo,
                             version as pyarmor_version)
from pyarmor.project import Project


def call_pyarmor(args):
    pyarmor_main(args)


class BaseHandler():

    def __init__(self, config):
        self._config = config
        self.children = []

    def dispatch(self, path, args):
        i = path.find('/')
        if i == -1:
            if hasattr(self, 'do_' + path):
                return getattr(self, 'do_' + path)(args)
            raise RuntimeError('No route for %s', path)
        else:
            name = path[:i]
            for handler in self.children:
                if handler.name == name:
                    return handler.dispatch(path[i+1:], args)
            raise RuntimeError('No route for %s', name)


class RootHandler(BaseHandler):

    def __init__(self, config):
        super().__init__(config)
        self.children.extend([ProjectHandler(config), LicenseHandler(config)])

    def do_version(self, args=None):
        pytransform_bootstrap()
        rcode = get_registration_code()
        return {
            'version': pyarmor_version,
            'rcode': rcode if rcode else '',
            'info': query_keyinfo(rcode) if rcode else ''
        }

    def do_listdir(self, args):
        path = os.path.expandvars(args.get('path', '/'))
        if sys.platform == 'win32':
            if path == '/':
                from ctypes import cdll
                drives = cdll.kernel32.GetLogicalDrives()
                result = []
                for i in range(26):
                    if drives & 1:
                        result.append(chr(i + 65) + ':\\')
                    drives >>= 1
                return [(x, 1) for x in result]
            if path[0] == '/':
                path = path[1:]

        if path == '@':
            return {
                'path': path,
                'dirs': ['/', os.path.expanduser('~')],
                'files': []
            }

        path = os.path.normpath(path)
        if not os.path.exists(path):
            raise RuntimeError('No %s found' % path)

        dirs = []
        files = []
        pat = args.get('pattern', '*')
        for x in glob.glob(os.path.join(path, '*')):
            if os.path.isdir(x):
                dirs.append(os.path.basename(x).replace('\\', '/'))
            elif pat == '*' or fnmatch(os.path.basename(x), pat):
                files.append(os.path.basename(x).replace('\\', '/'))
        dirs.sort(key=str.lower)
        files.sort(key=str.lower)
        return {
            'path': os.path.abspath(path).replace('\\', '/'),
            'dirs': dirs,
            'files': files,
        }


class ProjectHandler(BaseHandler):

    data_file = 'index.json'
    temp_id = 0

    def __init__(self, config):
        super().__init__(config)
        self.name = 'project'

    def _check_args(self, args):
        src = args.get('src')
        if not src:
            raise RuntimeError('No project src')
        elif not os.path.exists(src):
            raise RuntimeError('The project src %s does not exists' % src)

        def get(x, v=None):
            a = args.get(x)
            return v if not a else a

        entry = get('entry', [])
        entryModes = get('entryMode', [])
        cross_protection = 0 if 'no-cross-protection' in entryModes else 0
        bootstrap_code = 0 if 'no-bootstrap-code' in entryModes else 0

        manifest = []
        include = get('include')
        if include == 'exact':
            manifest.append('include ' + entry.join(' '))
        elif include == 'normal':
            manifest.append('include *.py')
        elif include == 'recursive':
            manifest.append('global-include *.py')

        for x in get('exclude', []):
            manifest.append('exclude ' + x)

        data = {
            'src': src,
            'manifest': manifest.join(','),
            'entry': entry.join(','),
            'cross_protection': cross_protection,
            'bootstrap_code': bootstrap_code,
            'restrict_mode': get('restrictMode', 2),
            'obf_mode': 1 if get('obfMod') else 0,
            'obf_code': 1 if get('obfCode') else 0,
            'wrap_mode': 1 if get('wrapMode') else 0,
            'advanced_mode': 1 if get('advancedMode') else 0,
            'runtime_path': get('runtimePath'),
            'license': get('licenseFile'),
            'target': get('target'),
            'enable_suffix': 1 if get('enableSuffix') else 0,
            'is_package': 1 if get('isPackage') else 0,
            'package_runtime': get('packageRuntime', 1),
        }
        for k in ('name', 'title', 'output', 'platform', 'plugins'):
            data[k] = get(k)
        return data

    def do_build_temp(self, args):
        data = self._check_args(args)

        name = 'project-%s' % self.temp_id
        path = os.path.join(self._get_path(), name)

        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        cmd_args = ['init', '--src', data['src'], path]
        call_pyarmor(cmd_args)

        project = Project()
        project.open(path)

        project._update(data)
        project.save(path)

        cmd_args = ['build']
        target = args.get('target')
        if target:
            cmd_args.extend(['--target', target])
        output = args.get('output')
        if output:
            cmd_args.extend(['--output', output])

        cmd_args.append(path)
        call_pyarmor(cmd_args)

        return output if output else os.path.join(path, 'dist')

    def do_new(self, args):
        c = self._get_config()
        n = c['counter'] + 1

        while True:
            name = 'project-%d' % n
            path = os.path.join(self._get_path(), name)
            if not os.path.exists(path):
                logging.info('Make project path %s', path)
                os.mkdir(path)
                break
            n += 1

        args['id'] = n
        args['name'] = name
        if not args.get('title', ''):
            args['title'] = os.path.basename(args.get('src'))
        data = self._check_args(args)

        cmd_args = ['init', '--src', data['src'], path]
        call_pyarmor(cmd_args)

        project = Project()
        project.open(path)
        project._update(data)
        project.save(path)

        c['projects'].append(args)
        c['counter'] = n
        self._set_config(c)

        logging.info('Create project: %s', args)
        return args

    def do_update(self, args):
        data = self._check_args(args)

        c, p = self._get_project(args)
        p.update(args)
        self._set_config(c)

        path = self._get_project_path(p)
        project = Project()
        project.open(path)
        project._update(data)
        project.save(path)

        logging.info('Update project: %s', p)
        return p

    def do_list(self, args):
        c = self._get_config()
        return c['projects']

    def do_remove(self, args):
        c, p = self._get_project(args)

        if args.get('clean'):
            path = self._get_project_path(p)
            if os.path.exists(path):
                shutil.rmtree(path)

        logging.info('Remove project: %s', p)
        c['projects'].remove(p)
        self._set_config(c)

        return p

    def do_build(self, args):
        c, p = self._get_project(args)
        path = self._get_project_path(p)

        cmd_args = ['build']
        target = args.get('traget')
        if target:
            cmd_args.extend(['--target', target])
        output = args.get('output')
        if output:
            cmd_args.extend(['--output', output])
        cmd_args.append(path)
        call_pyarmor(cmd_args)

        return output if output else os.path.join(path, 'dist')

    def do_runtime(self, args):
        options = 'platform', 'package_runtime', 'enable_suffix', \
                   'with_license'

        cmd_args = ['runtime']
        output = args.get('output', self._get_path())
        cmd_args.extend(['--output', output])

        for x in options:
            if x in args:
                cmd_args.append('--%s' % x.replace('_', '-'))
                v = args.get(x)
                if v:
                    cmd_args.append(v)

        logging.info('Generate runtime package at %s', output)
        call_pyarmor(cmd_args)

        return output

    def _get_project(self, args):
        c = self._get_config()
        n = args.get('id')
        for p in c['projects']:
            if n == p['id']:
                return c, p
        raise RuntimeError('No project %s found' % n)

    def _get_project_path(self, project):
        return os.path.join(self._get_path(), 'project-%s' % project['id'])

    def _get_path(self):
        c = self._config
        return os.path.join(c['homepath'], c['propath'])

    def _config_filename(self):
        path = self._get_path()
        filename = os.path.join(path, self.data_file)
        if not os.path.exists(filename):
            if not os.path.exists(path):
                os.makedirs(path)
            with open(filename, 'w') as fp:
                json.dump(dict(counter=0, projects=[]), fp)
        return filename

    def _get_config(self):
        with open(self._config_filename(), 'r') as fp:
            return json.load(fp)

    def _set_config(self, data):
        with open(self._config_filename(), 'w') as fp:
            return json.dump(data, fp, indent=2)


class LicenseHandler(BaseHandler):

    data_file = 'index.json'
    template = 'reg-%06d'
    options = {
        'harddisk': '--bind-disk',
        'ipv4': '--bind-ipv4',
        'mac': '--bind-mac',
        'expired': '--expired',
        'extra_data': '--bind-data',
        'disable_restrict_mode': '--disable-restrict-mode',
    }
    switch_option_names = 'disable_restrict_mode',

    def __init__(self, config):
        super().__init__(config)
        self.name = 'license'

    def do_new(self, args):
        c = self._get_config()
        n = c['counter'] + 1
        rcode = args.get('rcode')
        if not rcode:
            args['rcode'] = rcode = self.template % n
        args['id'] = n
        args.setdefault('rcode', rcode)
        c['licenses'].append(args)
        c['counter'] = n
        self._set_config(c)

        args['filename'] = self._create(args)
        return args

    def _create(self, args, update=False):
        path = self._get_path()
        output = args.get('output', path)

        rcode = args['rcode']
        filename = os.path.join(output, rcode, 'license.lic')
        if os.path.exists(filename) and not update:
            raise RuntimeError('The license "%s" has been exists' % rcode)

        cmd_args = ['licenses', '--output', output]
        for name, opt in self.options.items():
            if name in args:
                v = args.get(name)
                if v:
                    cmd_args.append(opt)
                    if name not in self.switch_option_names:
                        cmd_args.append(v)
        cmd_args.append(rcode)

        call_pyarmor(cmd_args)
        return filename

    def do_update(self, args):
        c, p = self._get_license(args)
        p.update(args)
        self._set_config(c)

        self._create(args, update=True)
        return p

    def do_remove(self, args):
        c, p = self._get_license(args)

        path = self._get_path()
        rcode = p['rcode']
        licpath = os.path.join(path, rcode)
        if os.path.exists(licpath):
            shutil.rmtree(licpath)

        c['licenses'].remove(p)
        self._set_config(c)
        return p

    def do_list(self, args=None):
        c = self._get_config()
        return c['licenses']

    def _get_license(self, args):
        c = self._get_config()
        n = args.get('id')
        r = args.get('rcode')
        for p in c['licenses']:
            if n == p['id'] and r == p['rcode']:
                return c, p
        raise RuntimeError('No license %s found' % n)

    def _get_path(self):
        c = self._config
        return os.path.join(c['homepath'], c['licpath'])

    def _config_filename(self):
        path = self._get_path()
        filename = os.path.join(path, self.data_file)
        if not os.path.exists(filename):
            if not os.path.exists(path):
                os.makedirs(path)
            with open(filename, 'w') as fp:
                json.dump(dict(counter=0, licenses=[]), fp)
        return filename

    def _get_config(self):
        with open(self._config_filename(), 'r') as fp:
            return json.load(fp)

    def _set_config(self, data):
        with open(self._config_filename(), 'w') as fp:
            return json.dump(data, fp, indent=2)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
