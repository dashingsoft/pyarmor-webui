import glob
import logging
import os
import shutil
import sys

from shlex import split as shell_split
from subprocess import Popen
from tempfile import TemporaryDirectory

from pyarmor.pyarmor import version as pyarmor_version

from pyarmor.cli.context import Context
from pyarmor.cli.register import Register
from pyarmor.cli.__main__ import main_entry as pyarmor_main


try:
    from .handler import BaseHandler, DirectoryHandler
except Exception:
    from handler import BaseHandler, DirectoryHandler


DEFAULT_RESTRICT_FLAG = 1
PRIVATE_MODULE_FLAG = 2
RESTRICT_PACKAGE_FLAG = 4
NO_RESTRICT_FLAG = 8


def enter_temp_path(func):

    def wrap(*args, **kwargs):
        oldpath = os.path.abspath(os.getcwd())
        with TemporaryDirectory() as tmpdirname:
            os.chdir(tmpdirname)
            try:
                return func(*args, **kwargs)
            finally:
                os.chdir(oldpath)

    return func


def call_pyinstaller(options):
    p = Popen([sys.executable, '-m', 'PyInstaller'] + options)
    p.wait()
    if p.returncode != 0:
        raise RuntimeError('Build bundle failed (%s)' % p.returncode)


def call_pyarmor(args, homepath=None, debug=False):
    logging.info('Call pyarmor: %s', args)
    extra_opts = ['--home', homepath] + (['-d'] if debug else [])
    pyarmor_main(extra_opts + args)


class RootHandler(BaseHandler):

    def __init__(self, config):
        super(RootHandler, self).__init__(config)
        self.children.extend([
            ProjectHandler(config),
            LicenseHandler(config),
            DirectoryHandler(config),
        ])

    @property
    def homepath(self):
        return self._config['homepath']

    def do_version(self, args=None):
        ctx = Context(self.homepath)
        info = Register(ctx).license_info
        pname = info['product']
        reginfo = 'License to: {0} ({1})'.format(
            info['regname'], 'non-profits' if pname in ('', 'TBD') else pname)
        return {
            'version': pyarmor_version,
            'regcode': info['licno'],
            'reginfo': reginfo,
            'server': self._config['version'],
            'python': '%s.%s.%s' % sys.version_info[:3],
            'v8mode': 1,
        }

    @enter_temp_path
    def do_register(self, args):
        from base64 import urlsafe_b64decode
        filename = args.get('filename')
        with open(filename, 'wb') as f:
            i = args['filedata'].find('base64,') + len('base64,')
            f.write(urlsafe_b64decode(args['filedata'][i:]))

        cmd_args = ['reg']
        is_initial = filename.endswith('.txt')
        if is_initial:
            self._check_arg('product', args)
            cmd_args.extend(['-y', '-p', args.get('product')])
            if filename[-8:-4].isdigit() and filename[-9] == '-':
                if int(filename[-8:-4]) < 4000:
                    cmd_args.append('-u')
        cmd_args.append(filename)
        call_pyarmor(cmd_args, homepath=self._config['homepath'])

        if is_initial:
            regfiles = glob.glob('pyarmor-reg*.zip')
            if not regfiles:
                raise RuntimeError('Abort registration')
            os.makedirs(self.homepath, exist_ok=True)
            dest = os.path.join(self.homepath, regfiles[0])
            logging.info('Store registration file "%s"', dest)
            os.rename(regfiles[0], dest)
            return dest
        return 'OK'


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

        if licfile and not licfile.endswith('pyarmor.rkey'):
            licfile = None

        def get_bool(x, v=0):
            return 1 if args.get(x) else v

        data = {
            'src': src,
            'manifest': None,
            'entry': ','.join(entry),
            'platform': ','.join([x[-1] for x in platforms]),
            'plugins': [x for x in plugins],
            'cross_protection': get_bool('crossProtection'),
            'restrict_mode': args.get('restrictMode', 1),
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

    @enter_temp_path
    def _build_target(self, path, args, debug=False):
        homepath = self._config['homepath']

        target = args.get('buildTarget')
        self._check_arg('target', target, valids=[0, 1, 2, 3])

        src = self._format_path(args.get('src'))
        name = args.get('bundleName')
        output = self._format_path(args.get('output'))
        if not output:
            output = os.path.join(src, 'dist')
        entries = args.get('entry', [])
        cmd_args = ['gen']

        if target:
            pack = args.get('pack', [])
            self._check_arg('pack', pack, types=list)
            pyi_options = self._handle_pack_options(src, pack)
            binext = '.exe' if sys.platform.startswith('win') else ''
            entryname = name if name else os.path.splitext(entries[0])[0]
            bundle = entryname + binext
            distpath = os.path.basename(output)
            if target in (2, 3):
                pyi_options.append('--onefile')
                distfile = os.path.join(distpath, bundle)
            else:
                distfile = os.path.join(distpath, entryname, bundle)
            pyi_options.extend(['--distpath', distpath])
            cmd_args.extend(['--pack', distfile])

            if name:
                pyi_options.extend(['--name', name])

            pyi_options.append(os.path.join(src, entries[0]))
            call_pyinstaller(pyi_options)

        else:
            if args.get('noRuntime'):
                cmd_args.append('--no-runtime')

            if name:
                cmd_args.append('-i')

            if args.get('platforms'):
                pnames = args.get('platforms')
                if any([x.startswith('themida.') for x in pnames]):
                    cmd_args.append('--enable-themida')
                    pnames = [x.replace('themida', 'windows') for x in pnames]
                cmd_args.extend(['--platform', ','.join(pnames)])

            cmd_args.extend(['--output', output])

        restrict_mode = args.get('restrictMode', DEFAULT_RESTRICT_FLAG)
        if restrict_mode & NO_RESTRICT_FLAG:
            call_pyarmor(['cfg', 'restrict_module', '0'], homepath=homepath)
        if restrict_mode & RESTRICT_PACKAGE_FLAG:
            cmd_args.append('--restrict')
        elif restrict_mode & PRIVATE_MODULE_FLAG:
            cmd_args.append('--private')

        if args.get('assertCall'):
            cmd_args.append('--assert-call')
        if args.get('assertImport'):
            cmd_args.append('--assert-import')

        if args.get('bccMode'):
            cmd_args.append('--enable-bcc')
        if args.get('rftMode'):
            cmd_args.append('--enable-rft')
        if args.get('mixStrings'):
            cmd_args.append('--mix-str')

        licfile = args.get('licenseFile')
        if target == 3 or licfile in ('false', 'outer'):
            cmd_args.append('--outer')
        elif licfile not in ('true', None, ''):
            if licfile.endswith('license.lic'):
                raise RuntimeError('This license file "%s" is not '
                                   'for Pyarmor 8' % licfile)
            if not os.path.exists(licfile):
                raise RuntimeError('no found license file "%s"' % licfile)
            cmd_args.append('--outer')

        if args.get('plugins'):
            plugins = ' '.join(args.get('plugins'))
            call_pyarmor(['cfg', 'plugins', '+', plugins], homepath=homepath)

        include = args.get('include', 'exact')
        excludes = args.get('exclude', [])

        for x in excludes:
            cmd_args.extend(['--exclude', os.path.join('*', x)])

        if include == 'exact':
            cmd_args.extend([os.path.join(src, x) for x in entries])
        elif name and not target:
            if include == 'all':
                cmd_args.append('-r')
            cmd_args.append(src)
        else:
            inputs = [(x.is_file(), x.path) for x in os.scandir(src)
                      if x not in excludes and not x.name.startswith('.')]
            if include == 'all':
                cmd_args.append('-r')
                cmd_args.extend([b for a, b in inputs if not a])
            cmd_args.extend([b for a, b in inputs if a and b.endswith('.py')])

        call_pyarmor(cmd_args, homepath=homepath, debug=debug)
        if target:
            if os.path.exists(output):
                if len(output) < 4:
                    # Do not rmtree too short path
                    raise RuntimeError('Output path "%s" is not empty', output)
                logging.info('Clean output path "%s"', output)
                shutil.rmtree(output)
            shutil.move(distpath, output)

        if isinstance(licfile, str) and os.path.exists(licfile):
            licpath = os.path.join(output, entryname if target == 1 else '')
            if target not in (2, 3):
                def is_runtime_package(p):
                    names = os.listdir(p)
                    return '__init__.py' in names and any([
                        x.startswith('pyarmor_runtime.') for x in names])

                for x in os.scandir(licpath):
                    if x.is_dir() and x.name.startswith('pyarmor_runtime_') \
                       and is_runtime_package(x.path):
                        licpath = x.path
                        break
                else:
                    raise RuntimeError('no found runtime package')
            shutil.copy2(licfile, licpath)

        return output

    def _build_temp(self, args, debug=False):
        self._build_data(args)

        name = 'project-%s' % self.temp_id
        path = os.path.join(self._get_path(), name)

        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

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
        self._build_data(args)

        c['projects'].append(args)
        c['counter'] = n
        self._set_config(c)

        logging.info('Create project: %s', args)
        return args

    def do_update(self, args):
        self._build_data(args)

        c, p = self._get_project(args)
        p.update(args)
        self._set_config(c)

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
        'harddisk': '*HARDDISK:',
        'ipv4': '*IFMAC:',
        'mac': '*IFIPV4:',
        'expired': '--expired',
        'extraData': '--bind-data',
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
        filepath = os.path.join(output, rcode)
        filename = os.path.join(filepath, 'pyarmor.rkey')
        if os.path.exists(filename) and not update:
            raise RuntimeError('The license "%s" already exists' % rcode)

        cmd_args = ['gen', 'key', '--output', filepath]
        device = []
        for name, opt in self.options.items():
            if name in args:
                v = args.get(name)
                if not v:
                    continue
                if opt.startswith('-'):
                    cmd_args.extend([opt, v])
                else:
                    device.append(opt + v)
        if device:
            cmd_args.extend(['-b', ''.join(device)])

        call_pyarmor(cmd_args, homepath=self._config['homepath'])
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
