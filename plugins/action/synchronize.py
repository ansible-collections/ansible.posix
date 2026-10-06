# -*- coding: utf-8 -*-

# (c) 2012-2013, Timothy Appnel <tim@appnel.com>
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os.path
import shutil
import stat
import tempfile
from collections.abc import MutableSequence
from shlex import quote as shlex_quote

from ansible import constants as C
from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.plugins.loader import connection_loader


DOCKER = ['docker', 'community.general.docker', 'community.docker.docker']
PODMAN = ['podman', 'ansible.builtin.podman', 'containers.podman.podman']
BUILDAH = ['buildah', 'containers.podman.buildah']

VAULT_HEADER = b'$ANSIBLE_VAULT'


class ActionModule(ActionBase):

    def _get_absolute_path(self, path):
        original_path = path

        #
        # Check if we have a local relative path and do not process
        # * remote paths (some.server.domain:/some/remote/path/...)
        # * URLs (rsync://...)
        # * local absolute paths (/some/local/path/...)
        #
        if ':' in path or path.startswith('/'):
            return path

        if self._task._role is not None:
            path = self._loader.path_dwim_relative(self._task._role._role_path, 'files', path)
        else:
            path = self._loader.path_dwim_relative(self._loader.get_basedir(), 'files', path)

        if original_path and original_path[-1] == '/' and path[-1] != '/':
            # make sure the dwim'd path ends in a trailing "/"
            # if the original path did
            path += '/'

        return path

    def _host_is_ipv6_address(self, host):
        return ':' in to_text(host, errors='surrogate_or_strict')

    def _format_rsync_rsh_target(self, host, path, user):
        ''' formats rsync rsh target, escaping ipv6 addresses if needed '''

        user_prefix = ''

        if path.startswith('rsync://'):
            return path

        # If using docker or buildah, do not add user information
        if self._remote_transport not in DOCKER + PODMAN + BUILDAH and user:
            user_prefix = '%s@' % (user, )

        if self._host_is_ipv6_address(host):
            return '[%s%s]:%s' % (user_prefix, host, path)

        # preserve formatting of remote paths if host or user@host is explicitly defined in the path
        if ':' not in path:
            return '%s%s:%s' % (user_prefix, host, path)
        elif '@' not in path:
            return '%s%s' % (user_prefix, path)
        else:
            return path

    def _process_origin(self, host, path, user):

        if host not in C.LOCALHOST:
            return self._format_rsync_rsh_target(host, path, user)

        path = self._get_absolute_path(path=path)
        return path

    def _process_remote(self, task_args, host, path, user, port_matches_localhost_port):
        """
        :arg host: hostname for the path
        :arg path: file path
        :arg user: username for the transfer
        :arg port_matches_localhost_port: boolean whether the remote port
            matches the port used by localhost's sshd.  This is used in
            conjunction with seeing whether the host is localhost to know
            if we need to have the module substitute the pathname or if it
            is a different host (for instance, an ssh tunnelled port or an
            alternative ssh port to a vagrant host.)
        """
        transport = self._connection.transport
        # If we're connecting to a remote host or we're delegating to another
        # host or we're connecting to a different ssh instance on the
        # localhost then we have to format the path as a remote rsync path
        if host not in C.LOCALHOST or transport != "local" or \
                (host in C.LOCALHOST and not port_matches_localhost_port):
            # If we're delegating to non-localhost and but the
            # inventory_hostname host is localhost then we need the module to
            # fix up the rsync path to use the controller's public DNS/IP
            # instead of "localhost"
            if port_matches_localhost_port and host in C.LOCALHOST:
                task_args['_substitute_controller'] = True
            return self._format_rsync_rsh_target(host, path, user)

        path = self._get_absolute_path(path=path)
        return path

    def _get_src_path(self, src):
        ''' returns src without the trailing slash or dot that makes rsync transfer the content of a directory '''
        path = src
        while path.endswith('/') or path.endswith('/.'):
            path = path[:-1]
        return path or '/'

    def _copy_owner(self, st, staged_path):
        for uid, gid in ((st.st_uid, -1), (-1, st.st_gid)):
            try:
                os.lchown(staged_path, uid, gid)
            except OSError:
                pass

    def _copy_stat(self, path, staged_path):
        self._copy_owner(os.stat(path), staged_path)
        shutil.copystat(path, staged_path)

    def _is_encrypted_file(self, path):
        try:
            with open(path, 'rb') as f:
                return f.read(len(VAULT_HEADER)) == VAULT_HEADER
        except OSError:
            return False

    def _fail_walk(self, error):
        raise AnsibleError("Failed to decrypt %s: the directory cannot be read: %s" % (error.filename, to_text(error.strerror)))

    def _get_encrypted_files(self, src):
        ''' returns the vault encrypted files that rsync would transfer for src, symlinks are not followed '''
        src_path = self._get_src_path(src)
        encrypted = set()

        if src == src_path and os.path.isfile(src_path) and self._is_encrypted_file(src_path):
            encrypted.add(src_path)

        if os.path.isdir(src_path):
            for root, dummy, files in os.walk(src_path, onerror=self._fail_walk):
                for name in files:
                    path = os.path.join(root, name)
                    if stat.S_ISREG(os.lstat(path).st_mode) and self._is_encrypted_file(path):
                        encrypted.add(path)
        return encrypted

    def _copy_file(self, path, staged_path, stat_path):
        with open(path, 'rb') as src, os.fdopen(os.open(staged_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as dest:
            shutil.copyfileobj(src, dest)
        self._copy_stat(stat_path, staged_path)

    def _stage_file(self, path, staged_path):
        try:
            os.link(path, staged_path)
        except OSError as e:
            if not stat.S_ISREG(os.lstat(path).st_mode):
                raise AnsibleError("Failed to decrypt %s: a hard link to this special file cannot be created in %s: %s" % (
                    path, C.DEFAULT_LOCAL_TMP, to_text(e)))
            self._copy_file(path, staged_path, path)

    def _stage_symlink(self, path, staged_path):
        st = os.lstat(path)
        target = os.readlink(path)
        if not target.startswith('/'):
            level = 0
            for name in os.path.realpath(os.path.dirname(path)).split('/') + target.split('/'):
                if name == '..':
                    level -= 1
                elif name not in ('', '.'):
                    level += 1
                if level < 0:
                    raise AnsibleError("Failed to decrypt %s: the symbolic link points above the root directory and cannot be mirrored" % path)
        os.symlink(target, staged_path)
        self._copy_owner(st, staged_path)
        os.utime(staged_path, ns=(st.st_atime_ns, st.st_mtime_ns), follow_symlinks=False)

    def _stage_decrypted_file(self, path, staged_path):
        real_path = os.path.realpath(path)
        if to_text(self._loader.path_dwim(real_path)) != real_path:
            raise AnsibleError("Failed to decrypt %s: the file name is not supported" % path)
        try:
            decrypted_path = self._loader.get_real_file(real_path, decrypt=True)
        except AnsibleError as e:
            raise AnsibleError("Failed to decrypt %s: %s" % (path, to_text(e)))
        local_tmp = os.path.join(os.path.realpath(C.DEFAULT_LOCAL_TMP), '')
        if not os.path.realpath(decrypted_path).startswith(local_tmp):
            raise AnsibleError("Failed to decrypt %s: no decrypted copy was created" % path)
        try:
            self._copy_file(decrypted_path, staged_path, path)
        finally:
            self._loader.cleanup_tmp_file(decrypted_path)

    def _stage_src(self, src, staging_dir, encrypted):
        ''' mirrors src below staging_dir with the encrypted files decrypted, returns the mirror of src to use as the rsync source '''
        src_path = self._get_src_path(src)
        staged_dirs = {}
        staged_links = []

        real_dir = '/'
        staged_dir = staging_dir if '/./' in src else os.path.join(staging_dir, '.')
        for name in os.path.dirname(src_path).split('/'):
            if not name or (name == '..' and os.path.samefile(staged_dir, staging_dir)):
                continue
            real_dir = os.path.join(real_dir, name)
            staged_dir = os.path.join(staged_dir, name)
            if name not in ('.', '..') and not os.path.isdir(staged_dir):
                os.mkdir(staged_dir, 0o700)
                staged_dirs[staged_dir] = real_dir

        staged_path = os.path.join(staged_dir, os.path.basename(src_path))
        if src_path in encrypted:
            self._stage_decrypted_file(src_path, staged_path)
        else:
            if not os.path.isdir(staged_path):
                os.mkdir(staged_path, 0o700)
                staged_dirs[staged_path] = src_path
            for root, dirs, files in os.walk(src_path, onerror=self._fail_walk):
                staged_root = staged_path + root[len(src_path):]
                for name in dirs:
                    path = os.path.join(root, name)
                    staged = os.path.join(staged_root, name)
                    if os.path.islink(path):
                        self._stage_symlink(path, staged)
                        staged_links.append((path, staged))
                    elif not os.path.isdir(staged):
                        os.mkdir(staged, 0o700)
                        staged_dirs[staged] = path
                for name in files:
                    path = os.path.join(root, name)
                    staged = os.path.join(staged_root, name)
                    if os.path.islink(path):
                        self._stage_symlink(path, staged)
                        staged_links.append((path, staged))
                    elif path in encrypted:
                        self._stage_decrypted_file(path, staged)
                    else:
                        self._stage_file(path, staged)

        real_staging_dir = os.path.join(os.path.realpath(staging_dir), '')
        for path, staged in staged_links:
            if not os.readlink(staged).startswith('/') and not os.path.realpath(staged).startswith(real_staging_dir):
                raise AnsibleError("Failed to decrypt %s: the symbolic link points outside of the mirror of src and cannot be mirrored" % path)

        for staged_dir in sorted(staged_dirs, reverse=True):
            self._copy_stat(staged_dirs[staged_dir], staged_dir)

        return staged_path + src[len(src_path):]

    def _remove_staging_dir(self, staging_dir):
        for root, dirs, dummy in os.walk(staging_dir):
            for name in dirs:
                path = os.path.join(root, name)
                if not os.path.islink(path):
                    os.chmod(path, 0o700)
        shutil.rmtree(staging_dir, ignore_errors=True)

    def _override_module_replaced_vars(self, task_vars):
        """ Some vars are substituted into the modules.  Have to make sure
        that those are correct for localhost when synchronize creates its own
        connection to localhost."""

        # Clear the current definition of these variables as they came from the
        # connection to the remote host
        if 'ansible_syslog_facility' in task_vars:
            del task_vars['ansible_syslog_facility']
        for key in list(task_vars.keys()):
            if key.startswith("ansible_") and key.endswith("_interpreter"):
                del task_vars[key]

        # Add the definitions from localhost
        for host in C.LOCALHOST:
            if host in task_vars['hostvars']:
                localhost = task_vars['hostvars'][host]
                break
        if 'ansible_syslog_facility' in localhost:
            task_vars['ansible_syslog_facility'] = localhost['ansible_syslog_facility']
        for key in localhost:
            if key.startswith("ansible_") and key.endswith("_interpreter"):
                task_vars[key] = localhost[key]

    def run(self, tmp=None, task_vars=None):
        ''' generates params and passes them on to the rsync module '''
        # When modifying this function be aware of the tricky convolutions
        # your thoughts have to go through:
        #
        # In normal ansible, we connect from controller to inventory_hostname
        # (playbook's hosts: field) or controller to delegate_to host and run
        # a module on one of those hosts.
        #
        # So things that are directly related to the core of ansible are in
        # terms of that sort of connection that always originate on the
        # controller.
        #
        # In synchronize we use ansible to connect to either the controller or
        # to the delegate_to host and then run rsync which makes its own
        # connection from controller to inventory_hostname or delegate_to to
        # inventory_hostname.
        #
        # That means synchronize needs to have some knowledge of the
        # controller to inventory_host/delegate host that ansible typically
        # establishes and use those to construct a command line for rsync to
        # connect from the inventory_host to the controller/delegate.  The
        # challenge for coders is remembering which leg of the trip is
        # associated with the conditions that you're checking at any one time.
        if task_vars is None:
            task_vars = dict()

        # We make a copy of the args here because we may fail and be asked to
        # retry. If that happens we don't want to pass the munged args through
        # to our next invocation. Munged args are single use only.
        _tmp_args = self._task.args.copy()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        # Store remote connection type
        self._remote_transport = self._connection.transport
        use_ssh_args = _tmp_args.pop('use_ssh_args', False)

        if use_ssh_args and self._connection.transport == 'ssh':
            ssh_args = [
                self._connection.get_option('ssh_args'),
                self._connection.get_option('ssh_common_args'),
                self._connection.get_option('ssh_extra_args'),
            ]
            _tmp_args['_ssh_args'] = ' '.join([a for a in ssh_args if a])

        # Handle docker connection options
        if self._remote_transport in DOCKER:
            self._docker_cmd = self._connection.docker_cmd
            if self._play_context.docker_extra_args:
                self._docker_cmd = "%s %s" % (self._docker_cmd, self._play_context.docker_extra_args)
        elif self._remote_transport in PODMAN:
            self._docker_cmd = self._connection._options['podman_executable']
            if self._connection._options.get('podman_extra_args'):
                self._docker_cmd = "%s %s" % (self._docker_cmd, self._connection._options['podman_extra_args'])

        # self._connection accounts for delegate_to so
        # remote_transport is the transport ansible thought it would need
        # between the controller and the delegate_to host or the controller
        # and the remote_host if delegate_to isn't set.

        remote_transport = False
        if self._connection.transport != 'local':
            remote_transport = True

        try:
            delegate_to = self._task.delegate_to
        except (AttributeError, KeyError):
            delegate_to = None

        # ssh paramiko docker buildah and local are fully supported transports.  Anything
        # else only works with delegate_to
        if delegate_to is None and self._connection.transport not in [
                'ssh', 'paramiko', 'local'] + DOCKER + PODMAN + BUILDAH:
            result['failed'] = True
            result['msg'] = (
                "synchronize uses rsync to function. rsync needs to connect to the remote "
                "host via ssh, docker client or a direct filesystem "
                "copy. This remote host is being accessed via %s instead "
                "so it cannot work." % self._connection.transport)
            return result

        # Parameter name needed by the ansible module
        _tmp_args['_local_rsync_path'] = task_vars.get('ansible_rsync_path') or 'rsync'

        # rsync thinks that one end of the connection is localhost and the
        # other is the host we're running the task for  (Note: We use
        # ansible's delegate_to mechanism to determine which host rsync is
        # running on so localhost could be a non-controller machine if
        # delegate_to is used)
        src_host = '127.0.0.1'
        inventory_hostname = task_vars.get('inventory_hostname')
        dest_host_inventory_vars = task_vars['hostvars'].get(inventory_hostname)
        # If the user did not set ansible_host, ansible fills it in with the address
        # of the delegate host when delegating, so only use ansible_host when not delegating.
        dest_host = ((task_vars.get('ansible_host') if delegate_to is None else None)
                     or dest_host_inventory_vars.get('ansible_host')
                     or inventory_hostname)
        if self._templar is not None:
            dest_host = self._templar.template(dest_host)

        dest_host_ids = [hostid for hostid in (dest_host_inventory_vars.get('inventory_hostname'),
                                               dest_host_inventory_vars.get('ansible_host'),
                                               dest_host)
                         if hostid is not None]

        localhost_ports = set()
        for host in C.LOCALHOST:
            localhost_vars = task_vars['hostvars'].get(host, {})
            for port_var in C.MAGIC_VARIABLE_MAPPING['port']:
                port = localhost_vars.get(port_var, None)
                if port:
                    break
            else:
                port = C.DEFAULT_REMOTE_PORT
            localhost_ports.add(port)

        # dest_is_local tells us if the host rsync runs on is the same as the
        # host rsync puts the files on.  This is about *rsync's connection*,
        # not about the ansible connection to run the module.
        dest_is_local = False
        if delegate_to is None and remote_transport is False:
            dest_is_local = True
        elif delegate_to is not None and delegate_to in dest_host_ids:
            dest_is_local = True

        # CHECK FOR NON-DEFAULT SSH PORT
        inv_port = task_vars.get('ansible_port', None) or C.DEFAULT_REMOTE_PORT
        if _tmp_args.get('dest_port', None) is None:
            if inv_port is not None:
                _tmp_args['dest_port'] = inv_port

        # Set use_delegate if we are going to run rsync on a delegated host
        # instead of localhost
        use_delegate = False
        if delegate_to is not None and delegate_to in dest_host_ids:
            # edge case: explicit delegate and dest_host are the same
            # so we run rsync on the remote machine targeting its localhost
            # (itself)
            dest_host = '127.0.0.1'
            use_delegate = True
        elif delegate_to is not None and remote_transport:
            # If we're delegating to a remote host then we need to use the
            # delegate_to settings
            use_delegate = True

        # Delegate to localhost as the source of the rsync unless we've been
        # told (via delegate_to) that a different host is the source of the
        # rsync
        if not use_delegate and remote_transport:
            # Unlike port, there can be only one shell
            localhost_shell = None
            for host in C.LOCALHOST:
                localhost_vars = task_vars['hostvars'].get(host, {})
                for shell_var in C.MAGIC_VARIABLE_MAPPING['shell']:
                    localhost_shell = localhost_vars.get(shell_var, None)
                    if localhost_shell:
                        break
                if localhost_shell:
                    break
            else:
                localhost_shell = os.path.basename(C.DEFAULT_EXECUTABLE)
            self._play_context.shell = localhost_shell

            # Unlike port, there can be only one executable
            localhost_executable = None
            for host in C.LOCALHOST:
                localhost_vars = task_vars['hostvars'].get(host, {})
                for executable_var in C.MAGIC_VARIABLE_MAPPING['executable']:
                    localhost_executable = localhost_vars.get(executable_var, None)
                    if localhost_executable:
                        break
                if localhost_executable:
                    break
            else:
                localhost_executable = C.DEFAULT_EXECUTABLE
            self._play_context.executable = localhost_executable

            try:
                new_connection = connection_loader.get('local', self._play_context)
            except TypeError:
                # Needed for ansible-core < 2.15
                new_connection = connection_loader.get('local', self._play_context, self._connection._new_stdin)
            self._connection = new_connection
            # Override _remote_is_local as an instance attribute specifically for the synchronize use case
            # ensuring we set local tmpdir correctly
            self._connection._remote_is_local = True
            self._override_module_replaced_vars(task_vars)

        # SWITCH SRC AND DEST HOST PER MODE
        if _tmp_args.get('mode', 'push') == 'pull':
            (dest_host, src_host) = (src_host, dest_host)

        # MUNGE SRC AND DEST PER REMOTE_HOST INFO
        src = _tmp_args.get('src', None)
        dest = _tmp_args.get('dest', None)
        if src is None or dest is None:
            return dict(failed=True, msg="synchronize requires both src and dest parameters are set")

        # Determine if we need a user@ and a password
        user = None
        password = task_vars.get('ansible_ssh_pass', None) or task_vars.get('ansible_password', None)
        if not dest_is_local:
            # Src and dest rsync "path" handling
            if boolean(_tmp_args.get('set_remote_user', 'yes'), strict=False):
                if use_delegate:
                    user = task_vars.get('ansible_delegated_vars', dict()).get('ansible_user', None)
                    if not user:
                        user = task_vars.get('ansible_user') or self._play_context.remote_user
                    if not user:
                        user = C.DEFAULT_REMOTE_USER
                else:
                    user = task_vars.get('ansible_user') or self._play_context.remote_user

            if self._templar is not None:
                user = self._templar.template(user)

            # Private key handling
            # Use the private_key parameter if passed else use context private_key_file
            _tmp_args['private_key'] = _tmp_args.get('private_key', self._play_context.private_key_file)

            # use the mode to define src and dest's url
            if _tmp_args.get('mode', 'push') == 'pull':
                # src is a remote path: <user>@<host>, dest is a local path
                src = self._process_remote(_tmp_args, src_host, src, user, inv_port in localhost_ports)
                dest = self._process_origin(dest_host, dest, user)
            else:
                # src is a local path, dest is a remote path: <user>@<host>
                src = self._process_origin(src_host, src, user)
                dest = self._process_remote(_tmp_args, dest_host, dest, user, inv_port in localhost_ports)

            password = (task_vars.get('ansible_ssh_pass')
                        or task_vars.get('ansible_password')
                        or dest_host_inventory_vars.get('ansible_ssh_pass', None)
                        or dest_host_inventory_vars.get('ansible_password', None))
            if self._templar is not None:
                password = self._templar.template(password)
        else:
            # Still need to munge paths (to account for roles) even if we aren't
            # copying files between hosts
            src = self._get_absolute_path(path=src)
            dest = self._get_absolute_path(path=dest)

        _tmp_args['_local_rsync_password'] = password
        _tmp_args['src'] = src
        _tmp_args['dest'] = dest

        # Allow custom rsync path argument
        rsync_path = _tmp_args.get('rsync_path', None)

        # backup original become as we are probably about to unset it
        become = self._play_context.become

        if not dest_is_local:
            # don't escalate for docker. doing --rsync-path with docker exec fails
            # and we can switch directly to the user via docker arguments
            if self._play_context.become and not rsync_path and self._remote_transport not in DOCKER + PODMAN:
                # If no rsync_path is set, become was originally set, and dest is
                # remote then add privilege escalation here.
                if self._play_context.become_method == 'sudo':
                    if self._play_context.become_user:
                        rsync_path = 'sudo -u %s rsync' % self._play_context.become_user
                    else:
                        rsync_path = 'sudo rsync'
                # TODO: have to add in the rest of the become methods here

            # We cannot use privilege escalation on the machine running the
            # module.  Instead we run it on the machine rsync is connecting
            # to.
            self._play_context.become = False

        _tmp_args['rsync_path'] = rsync_path

        # If launching synchronize against docker container
        # use rsync_opts to support container to override rsh options
        if self._remote_transport in DOCKER + BUILDAH + PODMAN and not use_delegate:
            # Replicate what we do in the module argumentspec handling for lists
            if not isinstance(_tmp_args.get('rsync_opts'), MutableSequence):
                tmp_rsync_opts = _tmp_args.get('rsync_opts', [])
                if isinstance(tmp_rsync_opts, str):
                    tmp_rsync_opts = tmp_rsync_opts.split(',')
                elif isinstance(tmp_rsync_opts, (int, float)):
                    tmp_rsync_opts = [to_text(tmp_rsync_opts)]
                _tmp_args['rsync_opts'] = tmp_rsync_opts

            if '--blocking-io' not in _tmp_args['rsync_opts']:
                _tmp_args['rsync_opts'].append('--blocking-io')

            if self._remote_transport in DOCKER + PODMAN:
                if become and self._play_context.become_user:
                    _tmp_args['rsync_opts'].append('--rsh=' + shlex_quote('%s exec -u %s -i' % (self._docker_cmd, self._play_context.become_user)))
                elif user is not None:
                    _tmp_args['rsync_opts'].append('--rsh=' + shlex_quote('%s exec -u %s -i' % (self._docker_cmd, user)))
                else:
                    _tmp_args['rsync_opts'].append('--rsh=' + shlex_quote('%s exec -i' % self._docker_cmd))
            elif self._remote_transport in BUILDAH:
                _tmp_args['rsync_opts'].append('--rsh=' + shlex_quote('buildah run --'))

        decrypt = boolean(_tmp_args.get('decrypt', False), strict=False)
        if decrypt:
            if _tmp_args.get('mode', 'push') == 'pull' or (use_delegate and remote_transport) or not src.startswith('/'):
                result['failed'] = True
                result['msg'] = (
                    "decrypt can only be used when the source is on the Ansible controller. "
                    "It does not support mode=pull, delegation to a remote host or a remote src.")
                return result

            src_path = self._get_src_path(src)
            if os.path.basename(src_path) in ('', '..'):
                result['failed'] = True
                result['msg'] = "decrypt cannot be used with a src that is the root directory or ends with '..': %s" % src
                return result

            if src == src_path and os.path.islink(src_path):
                result['failed'] = True
                result['msg'] = (
                    "decrypt cannot be used with a src that is a symbolic link: %s. "
                    "Add a trailing slash to synchronize the content of the directory it points to or use its target as src." % src)
                return result

            local_tmp = os.path.join(os.path.realpath(C.DEFAULT_LOCAL_TMP), '')
            if local_tmp.startswith(os.path.join(os.path.realpath(src_path), '')):
                result['failed'] = True
                result['msg'] = "decrypt cannot be used with a src that contains the local temporary directory %s: %s" % (C.DEFAULT_LOCAL_TMP, src)
                return result

            if os.path.expandvars(src) != src:
                result['failed'] = True
                result['msg'] = "decrypt cannot be used with a src that contains a reference to an environment variable: %s" % src
                return result

        staging_dir = None
        try:
            if decrypt:
                try:
                    encrypted = self._get_encrypted_files(src)
                    if encrypted:
                        staging_dir = tempfile.mkdtemp(dir=C.DEFAULT_LOCAL_TMP)
                        _tmp_args['src'] = self._stage_src(src, staging_dir, encrypted)
                except AnsibleError as e:
                    result['failed'] = True
                    result['msg'] = to_text(e)
                    return result
                except OSError as e:
                    result['failed'] = True
                    result['msg'] = "Failed to decrypt %s: %s" % (src, to_text(e))
                    return result

            # run the module and store the result
            result.update(self._execute_module('ansible.posix.synchronize', module_args=_tmp_args, task_vars=task_vars))
        finally:
            if staging_dir is not None:
                self._remove_staging_dir(staging_dir)

        return result
