param(
    [string]$FarePdf = "C:\Users\konoike\konoike Dropbox\貴志大地\ダウンロード（クラウド）\①料金表（帰省手当航空機利用者向け）.pdf"
)

$python = "C:\Users\konoike\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$script = Join-Path $PSScriptRoot "build_data.py"
$output = Join-Path $PSScriptRoot "app-data.js"

& $python $script --fare-pdf $FarePdf --output $output
