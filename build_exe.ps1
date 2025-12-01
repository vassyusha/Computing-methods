
Write-Host "Installing PyInstaller..."
pip install pyinstaller

Write-Host "Building Executable (Folder Mode)..."
python -m PyInstaller --noconfirm --onedir --windowed --name "ComputingMethods" --add-data "ui/styles.qss;ui" --collect-all "qtawesome" --clean `
    --exclude-module torch `
    --exclude-module tensorflow `
    --exclude-module cv2 `
    --exclude-module tkinter `
    --exclude-module xmlrpc `
    --exclude-module pandas `
    --exclude-module matplotlib.backends.backend_tkagg `
    --exclude-module matplotlib.backends.backend_wxagg `
    --exclude-module matplotlib.backends.backend_gtk3 `
    --exclude-module matplotlib.backends.backend_gtk4 `
    --exclude-module matplotlib.backends.backend_macosx `
    --exclude-module lib2to3 `
    main.py

Write-Host "Build Complete. Executable folder is in 'dist/ComputingMethods'."
$size = (Get-ChildItem "dist/ComputingMethods" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host ("Total folder size: {0:N2} MB" -f $size)

Write-Host "Now run Inno Setup to create the installer. It will compress this folder significantly."
