# Auto-Resume Script para Claude Code en VS Code
# Types "continua" in VS Code terminal at 04:00 AM (or specified time).

param (
    [string]$TargetTime = "04:00",
    [string]$Keys = "continua{ENTER}"
)

# Load assembly for SendKeys
Add-Type -AssemblyName System.Windows.Forms

# C# helper for SetForegroundWindow (using TypeDefinition for a full class)
$TypeDefinition = @"
    using System;
    using System.Runtime.InteropServices;
    public class WindowUtils {
        [DllImport("user32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool SetForegroundWindow(IntPtr hWnd);
    }
"@

# Try-Catch to avoid errors if already loaded in the session
try {
    Add-Type -TypeDefinition $TypeDefinition -ErrorAction SilentlyContinue
} catch {}

Write-Host "--- Auto-Resume Claude Code ---"
Write-Host "Hora objetivo: $TargetTime"
Write-Host "Buscando ventana de VS Code..."

function Get-VSCodeProcess {
    # 1. Buscar por titulos de ventana que contengan el proyecto o VS Code
    $procs = Get-Process | Where-Object { 
        $_.MainWindowHandle -ne 0 -and 
        ($_.MainWindowTitle -like "*Visual Studio Code*" -or $_.MainWindowTitle -like "*TuProyecto*") 
    }
    if ($procs) { return $procs | Select-Object -First 1 }
    
    # 2. Fallback por nombre de proceso
    $procs = Get-Process | Where-Object { $_.ProcessName -eq "Code" -and $_.MainWindowHandle -ne 0 }
    if ($procs) { return $procs | Select-Object -First 1 }

    return $null
}

$Proc = Get-VSCodeProcess
if ($Proc) {
    Write-Host "Detectado: $($Proc.ProcessName) - $($Proc.MainWindowTitle)"
} else {
    Write-Warning "No se detecto VS Code abierto. El script esperara a la hora marcada por si se abre."
}

Write-Host "IMPORTANTE: Debes tener abierta la pestaña de Claude Code en VS Code antes de las $TargetTime."
Write-Host "Esperando hasta las $TargetTime para enviar: '$Keys'..."

while ($true) {
    $Now = Get-Date -Format "HH:mm"
    if ($Now -eq $TargetTime) {
        Write-Host "[$(Get-Date)] Requisitando foco y enviando teclas..."
        
        $Proc = Get-VSCodeProcess
        if ($Proc) {
            $hWnd = $Proc.MainWindowHandle
            # Traer al frente
            [WindowUtils]::SetForegroundWindow($hWnd)
            Start-Sleep -Milliseconds 1500 
            # Enviar teclas
            [System.Windows.Forms.SendKeys]::SendWait($Keys)
            Write-Host "¡Comando enviado con exito!"
        } else {
            Write-Error "No se pudo encontrar VS Code en el momento final."
        }
        break
    }
    Start-Sleep -Seconds 10
}
