param(
  [string[]]$Files = @(
    'src/features/agent/SageView.tsx',
    'src/features/agent/StationStrip.tsx',
    'src/features/agent/FieldLog.tsx',
    'src/features/agent/LogEntry.tsx',
    'src/features/agent/SignalPath.tsx',
    'src/features/agent/Composer.tsx',
    'src/features/sensors/SensorStrip.tsx',
    'src/features/sensors/SensorCard.tsx',
    'src/features/showcase/Showcase.tsx'
  )
)

$ErrorActionPreference = 'Stop'

# Solo se bloquean valores que rompen el sistema de Teiba; los tokens Tailwind
# del tema (moss, surface, warn...) y los tamanos de texto no cuentan.
$patterns = @(
  @{ Name = 'color arbitrario'; Pattern = '(bg|text|border|from|to|fill|stroke)-\[#' },
  @{ Name = 'radio fuera de 4/6/8'; Pattern = 'rounded-\[(?!4px|6px|8px)' },
  @{ Name = 'sombra no declarada'; Pattern = 'shadow-' },
  @{ Name = 'fuente arbitraria'; Pattern = 'font-\[' },
  @{ Name = 'transition-all'; Pattern = 'transition-all' },
  @{ Name = 'color inline'; Pattern = 'style=\{\{[^}]*color' }
)

$violations = 0
foreach ($file in $Files) {
  if (-not (Test-Path -LiteralPath $file)) {
    Write-Error "No existe: $file"
    exit 1
  }
  $lines = Get-Content -LiteralPath $file
  for ($i = 0; $i -lt $lines.Count; $i++) {
    foreach ($p in $patterns) {
      if ($lines[$i] -match $p.Pattern) {
        Write-Output "${file}:$($i + 1): $($p.Name)"
        $violations++
      }
    }
  }
}

if ($violations -gt 0) {
  Write-Output "FALLA: $violations violaciones de tokens/estilos."
  exit 1
}
Write-Output 'OK: sin violaciones de tokens en los archivos del pilot.'
exit 0
