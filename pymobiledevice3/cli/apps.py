import click
import logging

from pymobiledevice3.cli.cli_common import Command, print_json
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.house_arrest import HouseArrestService
from pymobiledevice3.services.installation_proxy import InstallationProxyService
from pymobiledevice3.services.afc import AfcShell, AfcService
import os

@click.group()
def cli():
    """ apps cli """
    pass


@cli.group()
def apps():
    """ application options """
    pass


@apps.command('list', cls=Command)
@click.option('--color/--no-color', default=True)
@click.option('--json/--no-json', default=True)
@click.option('-u', '--user', is_flag=True, help='include user apps')
@click.option('-s', '--system', is_flag=True, help='include system apps')
def apps_list(lockdown: LockdownClient, json, color, user, system):
    """ list installed apps """
    app_types = []
    if user:
        app_types.append('User')
    if system:
        app_types.append('System')
    apps_list = InstallationProxyService(lockdown=lockdown).get_apps(app_types)
    if json:
        print_json(apps_list, colored=color)
    else:
        for app in apps_list:
            if app.get("ApplicationType") != "System":
                if app["CFBundleIdentifier"] == "fr.nartex.visorando":
                    print(app)
                    exit()
                print(app["CFBundleIdentifier"], "=>", app.get("Container"))
            else:
                print(app["CFBundleIdentifier"], "=> N/A")


@apps.command('uninstall', cls=Command)
@click.argument('bundle_id')
def uninstall(lockdown: LockdownClient, bundle_id):
    """ uninstall app by given bundle_id """
    InstallationProxyService(lockdown=lockdown).uninstall(bundle_id)


@apps.command('install', cls=Command)
@click.argument('ipa_path', type=click.Path(exists=True))
def install(lockdown: LockdownClient, ipa_path):
    """ install given .ipa """
    InstallationProxyService(lockdown=lockdown).install_from_local(ipa_path)


@apps.command('afc', cls=Command)
@click.argument('bundle_id')
def afc(lockdown: LockdownClient, bundle_id):
    """ open an AFC shell for given bundle_id, assuming its profile is installed """
    HouseArrestService(lockdown=lockdown).shell(bundle_id)

@apps.command('pull', cls=Command)
@click.argument('src', type=click.Path(file_okay=True, dir_okay=True, exists=False), nargs=1)
@click.argument('dst', type=click.Path(file_okay=False, dir_okay=True, exists=False), nargs=1)
@click.argument('bundle_id', nargs=1)
def pull(lockdown, src, dst, bundle_id):
    """ pull application files with AFC service for given bundle_id, assuming its profile is installed """
    print(bundle_id,src, dst)
    if not os.path.exists(dst):
        os.makedirs(dst)

    def log(src, dst):
        logging.info(f'{src} --> {dst}')

    client = HouseArrestService(lockdown=lockdown)
    client.send_command(bundle_id, cmd='VendDocuments')
    print(client)
    #client.listdir(src)
    client.pull(src, dst, callback=log)

