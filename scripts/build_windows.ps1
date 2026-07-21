param(
    [string]$IconPath = "",
    [string]$DistPath = "",
    [string]$WorkPath = "",
    [string]$SpecPath = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$qmlPath = Join-Path $projectRoot "src\white_cat_visualizer\ui\qml"
$appIconPath = Join-Path $projectRoot "src\white_cat_visualizer\ui\icon.svg"
$entryPoint = Join-Path $projectRoot "scripts\launch_app.py"
if (-not $DistPath) {
    $DistPath = Join-Path $projectRoot "dist"
}
if (-not $WorkPath) {
    $WorkPath = Join-Path $projectRoot "build"
}
if (-not $SpecPath) {
    $SpecPath = $projectRoot
}
$arguments = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name", "WhiteCatVisualizer",
    "--distpath", $DistPath,
    "--workpath", $WorkPath,
    "--specpath", $SpecPath,
    "--paths", (Join-Path $projectRoot "src"),
    "--add-data", "$qmlPath;white_cat_visualizer/ui/qml",
    "--add-data", "$appIconPath;white_cat_visualizer/ui"
)

if ($IconPath) {
    $resolvedIconPath = (Resolve-Path -LiteralPath $IconPath).Path
    $arguments += @("--icon", $resolvedIconPath)
}
$arguments += $entryPoint

Push-Location $projectRoot
try {
    python @arguments
} finally {
    Pop-Location
}
