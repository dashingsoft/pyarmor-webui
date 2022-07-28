import glob
import logging
import json
import os
import shutil
import sys

from fnmatch import fnmatch
from shlex import split as shell_split
from subprocess import Popen

from pyarmor.pyarmor import (main as pyarmor_main, pytransform_bootstrap,
                             get_registration_code, query_keyinfo,
                             version as pyarmor_version)
from pyarmor.project import Project


def call_pyarmor(args):
    logging.info('Call pyarmor: %s', args)
    pyarmor_main(args)


def run_pyarmor(args, debug=False):
    cmd = [sys.executable, '-d'] if debug else [sys.executable]
    p = Popen(cmd + ['-m', 'pyarmor.pyarmor'] + args)
    p.wait()
    if p.returncode != 0:
        raise RuntimeError('Build project failed (%s)' % p.returncode)


class BaseHandler(object):

    data_file = 'index.json'

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

    def _check_arg(self, name, value, valids=None, invalids=None, types=None):
        if value in (None, ''):
            raise RuntimeError('Missing argument "%s"' % name)
        if valids is not None and value not in valids:
            raise RuntimeError('Invalid argument "%s"' % name)
        if invalids is not None and value in invalids:
            raise RuntimeError('Invalid argument "%s"' % name)
        if types is not None and not isinstance(value, types):
            raise RuntimeError('Invalid argument "%s"' % name)

    def _check_path(self, path):
        if not os.path.exists(path):
            raise RuntimeError('This path %s does not exists' % path)

    def _format_path(self, path):
        return path.strip('/') if sys.platform == 'win32' else path

    def _get_path(self):
        c = self._config
        return os.path.join(c['homepath'], self.name + 's')

    def _config_filename(self):
        path = self._get_path()
        filename = os.path.join(path, self.data_file)
        if not os.path.exists(filename):
            if not os.path.exists(path):
                os.makedirs(path)
            data = dict(counter=0)
            data[self.name + 's'] = []
            with open(filename, 'w') as fp:
                json.dump(data, fp)
        return filename

    def _get_config(self):
        with open(self._config_filename(), 'r') as fp:
            return json.load(fp)

    def _set_config(self, data):
        with open(self._config_filename(), 'w') as fp:
            return json.dump(data, fp, indent=2)


class RootHandler(BaseHandler):

    def __init__(self, config):
        super(RootHandler, self).__init__(config)
        self.children.extend([
            ProjectHandler(config),
            LicenseHandler(config),
            DirectoryHandler(config),
            RuntimeHandler(config)
        ])

    def do_version(self, args=None):
        pytransform_bootstrap()
        rcode = get_registration_code()
        return {
            'version': pyarmor_version,
            'regcode': rcode if rcode else '',
            'reginfo': query_keyinfo(rcode) if rcode else '',
            'server': self._config['version'],
            'python': '%s.%s.%s' % sys.version_info[:3]
        }

    def do_register(self, regfile):
        if not regfile:
            for regfile in glob.glob('pyarmor-regfile*.zip'):
                break
        if regfile.endswith('.zip'):
            self._check_arg('file', regfile)
            self._check_path(regfile)
            regfile = os.path.expandvars(regfile).replace('\\', '/')
        cmd_args = ['register', regfile]
        call_pyarmor(cmd_args)
        return self.do_version()


class DirectoryHandler(BaseHandler):

    def __init__(self, config):
        super(DirectoryHandler, self).__init__(config)
        self.name = 'directory'

    def do_new(self, args):
        self._check_arg('path', args)

        if not os.path.exists(args):
            os.makedirs(args)
        return os.path.abspath(args)

    def do_remove(self, args):
        self._check_arg('path', args, invalids=['.', '/'])
        self._check_path(args)

        os.rmdir(args)
        return os.path.abspath(args)

    def do_list(self, args):
        path = os.path.expandvars(args.get('path', '/'))
        if sys.platform == 'win32':
            if path == '/':
                from ctypes import cdll
                drives = cdll.kernel32.GetLogicalDrives()
                result = []
                for i in range(26):
                    if drives & 1:
                        result.append(chr(i + 65) + ':')
                    drives >>= 1
                return {
                    'path': path,
                    'dirs': result,
                    'files': []
                }
            if path == '@':
                return {
                    'path': path,
                    'dirs': ['/',
                             '/' + os.path.expanduser('~').replace('\\', '/')],
                    'files': []
                }
            if path[0] == '/':
                path = path[1:]
            if len(path) == 2 and path[1] == ':':
                path += '/'

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
        super(ProjectHandler, self).__init__(config)
        self.name = 'project'

    def _build_data(self, args):
        src = self._format_path(args.get('src'))
        self._check_arg('src', src, types=str)
        self._check_path(src)

        entry = args.get('entry', [])
        self._check_arg('entry', entry, types=list)

        exclude = args.get('exclude', [])
        self._check_arg('exclude', exclude, types=list)

        licfile = args.get('licenseFile')
        self._check_arg('license', licfile, types=str)
        if licfile == 'false':
            licfile = 'outer'

        bootstrap = args.get('bootstrapCode')
        self._check_arg('bootstrap code', bootstrap, valids=[0, 1, 2, 3])

        obfcode = args.get('obfCode')
        if obfcode is True:
            obfcode = 1
        self._check_arg('obfCode', obfcode, valids=[0, 1, 2])

        obfmod = 2 if args.get('obfMod') is True else 0

        platforms = args.get('platforms', [])
        self._check_arg('platforms', platforms, types=list)

        plugins = args.get('plugins', [])
        self._check_arg('plugins', plugins, types=list)

        mixins = args.get('mixins')
        mixins = ['str'] if mixins is True else [] if not mixins else mixins

        include = args.get('include')
        self._check_arg('include', include,
                        valids=['exact', 'list', 'all'])

        manifest = []
        if include == 'exact':
            if entry:
                manifest.append('include ' + ' '.join(entry))
        elif include == 'all':
            manifest.append('global-include *.py')
        else:
            manifest.append('include *.py')
        for x in exclude:
            cmd = 'exclude' if x.endswith('.py') else 'prune'
            manifest.append('%s %s' % (cmd, x))

        if licfile and not licfile.endswith('license.lic'):
            licfile = None

        def get_bool(x, v=0):
            return 1 if args.get(x) else v

        data = {
            'src': src,
            'manifest': ','.join(manifest),
            'entry': ','.join(entry),
            'platform': ','.join([x[-1] for x in platforms]),
            'plugins': [x for x in plugins],
            'cross_protection': get_bool('crossProtection'),
            'restrict_mode': args.get('restrictMode', 2),
            'obf_mod': obfmod,
            'obf_code': obfcode,
            'wrap_mode': get_bool('wrapMode'),
            'advanced_mode': args.get('advancedMode', 0),
            'enable_suffix': get_bool('enableSuffix'),
            'license_file': licfile,
            'package_runtime': get_bool('packageRuntime'),
            'bootstrap_code': bootstrap,
            'is_package': 0,
            'mixins': mixins,
        }

        for k in ('name', 'title'):
            data[k] = args.get(k)

        output = self._format_path(args.get('output'))
        if not output:
            data['output'] = os.path.join(src, 'dist')

        return data

    def _handle_pack_options(self, src, options):
        result = []
        for item in options:
            for x in shell_split(item):
                if x:
                    result.extend(x.split('=', 1) if x.find('=') > 0 else [x])
        i = 0
        n = len(result)

        def _quote_path(s):
            if not os.path.isabs(s):
                s = os.path.join(src, s)
            s = s.replace('\\', '/')
            return ("'%s'" % s) if s.find(' ') > -1 else s

        while i < n:
            v = str(result[i])
            if v in ('--onefile', '-F', '--onefolder', '-D', '--name', '-N',
                     '--noconfirm', '-y', '--distpath', '--specpath'):
                raise RuntimeError('Option "%s" could not be used here' % v)
            if v in ('--add-data', '--add-binary'):
                i += 1
                if result[i].find(os.pathsep) == -1:
                    result[i] += os.pathsep + '.'
                result[i] = _quote_path(result[i])
            elif v in ('-i', '--icon', '-p', '--paths', '--runtime-hook',
                       '--additional-hooks-dir', '--version-file',
                       '-m', '--manifest', '-r', '--resource'):
                i += 1
                result[i] = _quote_path(result[i])
            i += 1
        return result

    def _build_target(self, path, args, debug=False):
        target = args.get('buildTarget')
        self._check_arg('target', target, valids=[0, 1, 2, 3])

        src = self._format_path(args.get('src'))
        name = args.get('bundleName')
        output = self._format_path(args.get('output'))
        if not output:
            output = os.path.join(src, 'dist')

        if target:
            cmd_args = ['pack']
            pack = args.get('pack', [])
            self._check_arg('pack', pack, types=list)
            options = self._handle_pack_options(src, pack)
            if target in (2, 3):
                options.append('--onefile')
            if target == 3:
                options.append('--runtime-hook')
                p = os.path.dirname(os.path.abspath(__file__))
                if p.find(' ') > -1:
                    s = "'%s'" % os.path.join(p, 'data', 'copy_license.py')
                else:
                    s = os.path.join(p, 'data', 'copy_license.py')
                options.append(s.replace('\\', '/'))

            if options:
                cmd_args.append('--options')
                cmd_args.append(" %s" % (' '.join(options)))
            if name:
                cmd_args.extend(['--name', name])
            if target == 3 or args.get('licenseFile') in ('false', 'outer'):
                cmd_args.append('--without-license')
        else:
            cmd_args = ['build']
            if args.get('noRuntime'):
                cmd_args.append('--no-runtime')

            if name:
                output = os.path.join(output, name)
        cmd_args.extend(['--output', output])

        cmd_args.append(path)
        run_pyarmor(cmd_args, debug=debug)

        return output

    def _build_temp(self, args, debug=False):
        data = self._build_data(args)

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

        return self._build_target(path, args, debug=debug)

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
        args['path'] = path
        if not args.get('title', ''):
            args['title'] = os.path.basename(args.get('src'))
        data = self._build_data(args)

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
        data = self._build_data(args)

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

    def do_build(self, args, debug=False):
        c, p = self._get_project(args, silent=True)
        if p is None:
            return self._build_temp(args, debug=debug)

        path = self._get_project_path(p)
        return self._build_target(path, args, debug=debug)

    def do_diagnose(self, args):
        return self.do_build(args, debug=True)

    def _get_project(self, args, silent=False):
        c = self._get_config()
        n = args.get('id')
        for p in c['projects']:
            if n == p['id']:
                return c, p
        if silent:
            return c, None
        raise RuntimeError('No project %s found' % n)

    def _get_project_path(self, project):
        return os.path.join(self._get_path(), 'project-%s' % project['id'])


class LicenseHandler(BaseHandler):

    template = 'reg-%06d'
    options = {
        'harddisk': '--bind-disk',
        'ipv4': '--bind-ipv4',
        'mac': '--bind-mac',
        'expired': '--expired',
        'extraData': '--bind-data',
        'disableRestrictMode': '--disable-restrict-mode',
        'enablePeriodMode': '--enable-period-mode',
    }
    switch_option_names = 'disableRestrictMode', 'enablePeriodMode'

    def __init__(self, config):
        super(LicenseHandler, self).__init__(config)
        self.name = 'license'

    def do_new(self, args):
        c = self._get_config()
        n = c['counter'] + 1
        rcode = args.get('rcode')
        if not rcode:
            args['rcode'] = rcode = self.template % n

        args['filename'] = self._create(args)

        args['id'] = n
        c['licenses'].append(args)
        c['counter'] = n
        self._set_config(c)

        return args

    def _create(self, args, update=False):
        path = self._get_path()
        output = self._format_path(args.get('output', path))

        rcode = args['rcode']
        filename = os.path.join(output, rcode, 'license.lic')
        if os.path.exists(filename) and not update:
            raise RuntimeError('The license "%s" already exists' % rcode)

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


class RuntimeHandler(BaseHandler):

    def __init__(self, config):
        super(RuntimeHandler, self).__init__(config)
        self.name = 'runtime'

    def do_new(self, args):
        cmd_args = ['runtime']
        output = self._format_path(args.get('output', self._get_path()))
        cmd_args.extend(['--output', output])

        for x in ('platform', 'mode', 'with_license'):
            if x in args:
                cmd_args.append('--%s' % x.replace('_', '-'))
                v = args.get(x)
                if v:
                    cmd_args.append(v)

        logging.info('Generate runtime package at %s', output)
        call_pyarmor(cmd_args)

        return output


if __name__ == '__main__':
    import doctest
    doctest.testmod()
