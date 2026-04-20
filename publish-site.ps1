param(
    [string]$FarePdf = ""
)

$python = "C:\Users\konoike\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$siteDir = Join-Path $PSScriptRoot "site"
$dataFile = Join-Path $siteDir "app-data.js"
$script = Join-Path $PSScriptRoot "build_data.py"

New-Item -ItemType Directory -Path $siteDir -Force | Out-Null

if ($FarePdf) {
    & $python $script --fare-pdf $FarePdf --output $dataFile
}
else {
    & $python $script --output $dataFile
}

Copy-Item -Path (Join-Path $PSScriptRoot "index.html") -Destination (Join-Path $siteDir "index.html") -Force
Set-Content -Path (Join-Path $siteDir ".nojekyll") -Value "" -Encoding utf8

Write-Host "公開用ファイルを更新しました:"
Write-Host $siteDir
