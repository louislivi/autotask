# -*- mode: python -*-

block_cipher = None


a = Analysis(['C:\\Users\\\xc0\xee\xce\xa1\\Desktop\\pythontask\\autotask\\code\\run.py'],
             pathex=['C:\\Users\\\xc0\xee\xce\xa1\\Desktop\\pythontask\\autotask\\package'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='autotask',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='C:\\Users\\¿ÓŒ°\\Desktop\\pythontask\\autotask\\package\\log\\rd.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='autotask')
