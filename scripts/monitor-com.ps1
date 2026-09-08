param(
    [string]$Port = 'COM11',
    [int]$Baud = 115200,
    [Parameter(Mandatory = $true)][string]$LogPath,
    [Parameter(Mandatory = $true)][string]$PidPath,
    [switch]$ResetOnConnect
)

$ErrorActionPreference = 'Stop'
$encoding = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($PidPath, [string]$PID, $encoding)
$writer = New-Object System.IO.StreamWriter($LogPath, $true, $encoding)
$writer.AutoFlush = $true
$resetPending = $ResetOnConnect.IsPresent

function Write-MonitorLine([string]$Text) {
    $writer.WriteLine(('[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss.fff'), $Text))
}

try {
    Write-MonitorLine "Monitor PID=$PID port=$Port baud=$Baud 8N1 flow=none"
    while ($true) {
        $serial = New-Object System.IO.Ports.SerialPort($Port, $Baud, 'None', 8, 'One')
        $serial.Encoding = $encoding
        $serial.ReadTimeout = 1000
        $serial.Handshake = 'None'
        $serial.DtrEnable = $false
        $serial.RtsEnable = $false
        try {
            $serial.Open()
            Write-MonitorLine "Connected $Port"
            if ($resetPending) {
                $resetPending = $false
                Write-MonitorLine 'Resetting USB Serial/JTAG device for startup capture'
                # Match esptool HardReset(uses_usb=True).
                $serial.RtsEnable = $true
                Start-Sleep -Milliseconds 200
                $serial.RtsEnable = $false
                Start-Sleep -Milliseconds 200
            }
            while ($serial.IsOpen) {
                try {
                    Write-MonitorLine ($serial.ReadLine().TrimEnd("`r"))
                } catch [System.TimeoutException] {
                    continue
                }
            }
        } catch {
            Write-MonitorLine ("Serial error: {0}" -f $_.Exception.Message)
        } finally {
            $serial.Dispose()
        }
        Start-Sleep -Seconds 2
    }
} finally {
    $writer.Dispose()
}
