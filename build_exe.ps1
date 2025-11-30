
Write-Host "Installing PyInstaller..."
pip install pyinstaller

Write-Host "Building Executable..."
python -m PyInstaller --noconfirm --onefile --windowed --name "ComputingMethods" --add-data "ui/styles.qss;ui" --collect-all "qtawesome" --clean --exclude-module torch --exclude-module tensorflow --exclude-module cv2 main.py

Write-Host "Build Complete. Executable is in the 'dist' folder."
