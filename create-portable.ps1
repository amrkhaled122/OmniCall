# OmniCall Portable Distribution Builder

$version = "1.0.0"
$folderName = "OmniCall-v$version-Portable"
$zipName = "$folderName.zip"

Write-Host "Building portable distribution..." -ForegroundColor Cyan

# Clean up old builds
if (Test-Path $folderName) {
    Remove-Item $folderName -Recurse -Force
}
if (Test-Path $zipName) {
    Remove-Item $zipName -Force
}

# Create distribution folder
New-Item -ItemType Directory -Path $folderName | Out-Null

# Copy essential files
Write-Host "Copying files..." -ForegroundColor Yellow
Copy-Item "dist\OmniCall\OmniCall.exe" "$folderName\" -Force
Copy-Item "dist\OmniCall\_internal" "$folderName\_internal" -Recurse -Force
Copy-Item "dist\OmniCall\Accept.png" "$folderName\" -Force
Copy-Item "README.md" "$folderName\" -Force
Copy-Item "LICENSE" "$folderName\" -Force

# Create a quick start file
$quickStart = @"
# OmniCall - Quick Start

## How to Run

1. Double-click **OmniCall.exe** to launch the app
2. Follow the on-screen setup wizard to pair your phone
3. Keep the app running while playing Dota 2

## First-Time Windows Warning

If Windows shows a security warning:
1. Click "More info"
2. Click "Run anyway"

This is normal for new apps without expensive code signing certificates.

## Need Help?

- Documentation: README.md
- Issues: https://github.com/amrkhaled122/OmniCall/issues
- PWA: https://amrkhaled122.github.io/OmniCall/
"@

Set-Content -Path "$folderName\QUICK_START.txt" -Value $quickStart -Force

# Create ZIP
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
Compress-Archive -Path "$folderName\*" -DestinationPath $zipName -Force

# Cleanup
Remove-Item $folderName -Recurse -Force

Write-Host "`n✅ Build complete: $zipName" -ForegroundColor Green
Write-Host "📦 Size: $([math]::Round((Get-Item $zipName).Length / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Test the portable version" -ForegroundColor White
Write-Host "  2. Upload $zipName to GitHub Releases" -ForegroundColor White
Write-Host "  3. (Optional) Build installer with Inno Setup" -ForegroundColor White
