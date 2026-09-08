param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9]{1,8}\.[0-9]{1,8}\.[0-9]{1,8}$')]
    [string]$Version,
    [ValidateSet('test', 'stable')]
    [string]$Channel = 'test',
    [ValidatePattern('^[a-z0-9][a-z0-9.-]{0,95}$')]
    [string]$Board = 'laoyuanxiaozhi',
    [string]$SshConfig = (Join-Path $env:USERPROFILE '.ssh/config'),
    [string]$BuildDirectory = 'build'
)
$ErrorActionPreference = 'Stop'
$cache = Get-Content -LiteralPath (Join-Path $BuildDirectory 'CMakeCache.txt')
if (-not ($cache -match ('^BOARD_NAME:[^=]+=' + [regex]::Escape($Board) + '$'))) {
    throw 'Build board identity does not match requested release'
}
$firmware = (Resolve-Path -LiteralPath (Join-Path $BuildDirectory 'xiaozhi.bin')).Path
$assets = (Resolve-Path -LiteralPath (Join-Path $BuildDirectory 'generated_assets.bin')).Path
$bytes = [IO.File]::ReadAllBytes($firmware)
if ($bytes.Length -lt 288 -or $bytes[0] -ne 233) { throw 'Invalid application image' }
$binaryText = [Text.Encoding]::ASCII.GetString($bytes)
if (-not $binaryText.Contains($Board + [char]0)) {
    throw 'Application image does not contain the requested board identity; rebuild first'
}
$builtVersion = [Text.Encoding]::ASCII.GetString($bytes, 48, 32).TrimEnd([char]0)
if ($builtVersion -ne $Version) { throw "Binary version is $builtVersion, requested $Version" }
$stage = '/opt/xiaozhi-ota/staging/' + [Guid]::NewGuid().ToString('N')
ssh -F $SshConfig aliyun_ecs "mkdir -p '$stage'"
if ($LASTEXITCODE -ne 0) { throw 'Cannot create staging directory' }
scp -F $SshConfig $firmware $assets "aliyun_ecs:$stage/"
if ($LASTEXITCODE -ne 0) { throw 'Upload failed; release unchanged' }
ssh -F $SshConfig aliyun_ecs "/usr/bin/python3.6 /opt/xiaozhi-ota/app/publish_release.py --stage '$stage' --board '$Board' --version '$Version' --channel '$Channel'"
if ($LASTEXITCODE -ne 0) { throw 'Release validation or publication failed' }
Write-Host "Published $Board $Version to $Channel; staging retained at $stage"
