import sys
import platform
import requests
import os
from tqdm import tqdm
import hashlib
import shutil

def not_support():
    print('Your system is not supported.')
    sys.exit()

def get_system_architecture():
    architecture = platform.machine()
    if platform.system() == 'Windows':
        if architecture == 'AMD64':
            return 'x64'
        elif architecture == 'x86':
            return 'ia32'
    elif platform.system() == 'Linux':
        if architecture == 'x86_64':
            return 'x64'
        elif architecture == 'i686':
            return 'ia32'
    return 'x64'
    not_support()
    
def extract_file(file_path, extract_to):
    if file_path.endswith('.zip'):
        import zipfile
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # 计算zip文件中的文件数量
            total = len(zip_ref.namelist())
            for member in tqdm(zip_ref.namelist(), total=total, desc='Extracting '):
                zip_ref.extract(member, extract_to)
    elif file_path.endswith('.tar.gz'):
        import tarfile
        with tarfile.open(file_path, 'r:gz') as tar_ref:
            # 计算tar.gz文件中的文件数量
            total = len(tar_ref.getmembers())
            for member in tqdm(tar_ref.getmembers(), total=total, desc='Extracting '):
                tar_ref.extract(member, extract_to)

def verify_checksum(file_path, hash_text):
    for line in hash_text.split('\n'):
        if file_path in line:
            expected_checksum, _ = line.strip().split('  ')
            return calculate_sha256(file_path) == expected_checksum
    return False

def calculate_sha256(filename):
    sha256_hash = hashlib.sha256()
    total_size = os.path.getsize(filename)
    progress = tqdm(total=total_size, unit='B', unit_scale=True, desc='Validate')

    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            progress.update(len(byte_block))

    progress.close()  # 完成进度条

    return sha256_hash.hexdigest()
    
def download():
    url = f'{base_url}/{file_name}'
    print('Downloading NW.js')
    # 发送HEAD请求以获取文件大小
    
    response = requests.head(url)
    if response.status_code == 200:
        file_size = int(response.headers.get('Content-Length', 0))
    
        # 发送GET请求并使用tqdm显示进度条
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(file_name, 'wb') as f, tqdm(
                    total=file_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                        bar.update(len(chunk))
            
        except requests.exceptions.RequestException as e:
            print('Error during download:', e)
    else:
        print(f'Error: Unable to access the URL {url}')
    
version = '0.90.0'
base_url = f'https://dl.nwjs.io/v{version}'

bit = get_system_architecture()

if sys.platform.startswith('win32'):
    base_name = f'nwjs-sdk-v{version}-win-{bit}'
    file_name = f'nwjs-sdk-v{version}-win-{bit}.zip'
elif sys.platform.startswith('linux'):
    base_name = f'nwjs-sdk-v{version}-linux-{bit}'
    file_name = f'nwjs-sdk-v{version}-linux-{bit}.tar.gz'
else:
    not_support()

while True:
    #download()
    req = requests.get(f'https://dl.nwjs.io/v{version}/SHASUMS256.txt')
    if verify_checksum(file_name, req.text):
        print(f'Download completed: {file_name}')
        break
    else:
        print('Verification passed')


if os.path.exists(base_name):
    shutil.rmtree(base_name)
    
elif os.path.exists('sdk'):
    shutil.rmtree('sdk')
    
extract_file(file_name, '.')

os.rename(base_name, 'sdk')