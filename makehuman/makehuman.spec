# -*- mode: python -*-
a = Analysis(['makehuman.py'],
             pathex=['lib','core','shared','apps','apps/gui', 'plugins'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None
             )

##### include mydir in distribution #######
def extra_datas(mydir):
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_datas = []
    for f in files:
        extra_datas.append((f, f, 'DATA'))

    return extra_datas
###########################################

# append the 'data' dir
a.datas += extra_datas('data')
a.datas += extra_datas('lib')
a.datas += extra_datas('core')
a.datas += extra_datas('shared')
a.datas += extra_datas('apps')
a.datas += extra_datas('plugins')
a.datas += extra_datas('tools')
a.datas += extra_datas('utils')
a.datas += extra_datas('icons')
#a.datas += extra_datas('qt_menu.nib')

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='makehuman',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='makehuman')
app = BUNDLE(coll,
             name='makehuman.app',
             icon=None)
