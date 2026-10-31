# Detector Impeccable para la estación Teiba.
# Localiza el launcher local (.opencode/skills/impeccable/scripts/impeccable.cmd)
# o el global (%USERPROFILE%/.config/opencode/skills/impeccable/scripts/impeccable.cmd),
# cambia a la raíz del repo y ejecuta `detect --json frontend/src`.
$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontend = Split-Path -Parent $here
$repo = Split-Path -Parent $frontend

$candidates = @(
  (Join-Path $repo '.opencode/skills/impeccable/scripts/impeccable.cmd'),
  (Join-Path $env:USERPROFILE '.config/opencode/skills/impeccable/scripts/impeccable.cmd')
)
$launcher = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $launcher) {
  Write-Error "No se encontró el launcher de Impeccable en: $($candidates -join ' | ')"
  exit 1
}

Set-Location -LiteralPath $repo
& $launcher detect --json frontend/src
exit $LASTEXITCODE
