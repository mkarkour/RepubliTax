from PyInstaller.utils.hooks import (collect_data_files, collect_submodules,
                                     copy_metadata)

hiddenimports = collect_submodules('streamlit')
datas = copy_metadata('streamlit')
