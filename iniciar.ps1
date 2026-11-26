param(
    [switch]$Comprobar,
    [switch]$SinNavegador,
    [int]$LanzadorId,
    [string]$EjecutablePython,
    [string]$EjecutableNode
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$backend = Join-Path $PSScriptRoot 'backend'
$frontend = Join-Path $PSScriptRoot 'frontend'
$logs = Join-Path $env:LOCALAPPDATA 'Zeno/logs'
$apiUrl = 'http://127.0.0.1:8000'
$webUrl = 'http://127.0.0.1:3000'

function Iniciar-Servidor([string]$Nombre, [string]$Ejecutable, [string]$Argumentos, [string]$Directorio) {
    $opciones = @{
        FilePath = $Ejecutable
        ArgumentList = $Argumentos
        WorkingDirectory = $Directorio
        WindowStyle = 'Hidden'
        RedirectStandardOutput = Join-Path $logs "$Nombre.log"
        RedirectStandardError = Join-Path $logs "$Nombre-error.log"
        PassThru = $true
    }
    Start-Process @opciones
}

if ($LanzadorId) {
    $lanzador = [System.Diagnostics.Process]::GetProcessById($LanzadorId)
    $null = $lanzador.Handle

    # Los hijos heredan el Job Object. Windows los termina incluso si se cierra la consola.
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;

public static class GrupoZeno
{
    private const uint KillOnJobClose = 0x2000;
    private const int ExtendedLimitInformation = 9;

    [StructLayout(LayoutKind.Sequential)]
    private struct BasicLimits
    {
        public long ProcessTime, JobTime;
        public uint Flags;
        public UIntPtr MinWorkingSet, MaxWorkingSet;
        public uint ActiveProcesses;
        public UIntPtr Affinity;
        public uint Priority, Scheduling;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct IoCounters
    {
        public ulong ReadOperations, WriteOperations, OtherOperations;
        public ulong ReadBytes, WriteBytes, OtherBytes;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct ExtendedLimits
    {
        public BasicLimits Basic;
        public IoCounters Io;
        public UIntPtr ProcessMemory, JobMemory, PeakProcessMemory, PeakJobMemory;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr CreateJobObject(IntPtr attributes, IntPtr name);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetInformationJobObject(IntPtr job, int kind, ref ExtendedLimits limits, uint length);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);

    [DllImport("kernel32.dll")]
    private static extern IntPtr GetCurrentProcess();

    [DllImport("kernel32.dll")]
    private static extern bool CloseHandle(IntPtr handle);

    public static void Vincular()
    {
        IntPtr job = CreateJobObject(IntPtr.Zero, IntPtr.Zero);
        if (job == IntPtr.Zero)
            throw new Win32Exception(Marshal.GetLastWin32Error());

        var limits = new ExtendedLimits { Basic = new BasicLimits { Flags = KillOnJobClose } };
        if (!SetInformationJobObject(job, ExtendedLimitInformation, ref limits, (uint)Marshal.SizeOf(limits))
            || !AssignProcessToJobObject(job, GetCurrentProcess()))
        {
            int error = Marshal.GetLastWin32Error();
            CloseHandle(job);
            throw new Win32Exception(error);
        }
        // El handle no se hereda y se cierra al terminar este supervisor.
    }
}
'@
    [GrupoZeno]::Vincular()
    if ($lanzador.HasExited) { exit 0 }
    $api = Iniciar-Servidor 'backend' $EjecutablePython '-B -m uvicorn src.app:app --host 127.0.0.1 --port 8000' $backend
    $web = Iniciar-Servidor 'frontend' $EjecutableNode 'node_modules/next/dist/bin/next dev --hostname 127.0.0.1 --port 3000' $frontend

    while (-not $lanzador.WaitForExit(500)) {
        if ($api.HasExited) { throw 'Se detuvo FastAPI. Revisa backend-error.log.' }
        if ($web.HasExited) { throw 'Se detuvo Next.js. Revisa frontend-error.log.' }
    }
    exit 0
}

function Comprobar-PuertoLibre([int]$Puerto) {
    $socket = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Puerto)
    $socket.Server.ExclusiveAddressUse = $true
    try {
        $socket.Start()
    } catch {
        $ocupante = Get-NetTCPConnection -LocalPort $Puerto -State Listen -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($ocupante) { throw "El puerto $Puerto esta ocupado por el proceso $($ocupante.OwningProcess)." }
        throw "No se pudo abrir el puerto $Puerto. Windows puede tenerlo reservado."
    } finally {
        $socket.Stop()
    }
}

function Esperar-Respuesta([string]$Url, [System.Diagnostics.Process]$Supervisor) {
    $limite = [DateTime]::UtcNow.AddSeconds(120)
    while ([DateTime]::UtcNow -lt $limite) {
        if ($Supervisor.HasExited) { throw "Se detuvo un servidor. Revisa los registros en $logs." }
        try {
            $respuesta = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($respuesta.StatusCode -eq 200) { return }
        } catch {
            Start-Sleep -Milliseconds 400
        }
    }
    throw "No respondio $Url. Revisa los registros en $logs."
}

$mutex = [System.Threading.Mutex]::new($false, 'Local\Zeno.Iniciar')
$tieneMutex = $false
$supervisor = $null
$resultado = 0
try {
    try {
        $tieneMutex = $mutex.WaitOne(0)
    } catch [System.Threading.AbandonedMutexException] {
        $tieneMutex = $true
    }
    if (-not $tieneMutex) { throw 'Ya hay una ventana de Zeno iniciando o ejecutando los servidores.' }
    if (-not (Test-Path -LiteralPath (Join-Path $backend '.env') -PathType Leaf)) {
        throw 'Falta backend/.env. Configura DATABASE_URL y JWT_SECRET a partir de backend/.env.example.'
    }
    Comprobar-PuertoLibre 8000
    Comprobar-PuertoLibre 3000

    $python = Join-Path $backend 'venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        Write-Host 'Creando entorno virtual de Python...'
        $py = Get-Command py.exe -ErrorAction SilentlyContinue
        if ($py) {
            & $py.Source -3 -m venv (Join-Path $backend 'venv')
        } else {
            $pythonBase = Get-Command python.exe -ErrorAction SilentlyContinue
            if (-not $pythonBase) { throw 'Instala Python 3.11 o superior.' }
            & $pythonBase.Source -m venv (Join-Path $backend 'venv')
        }
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $python)) { throw 'No se pudo crear el entorno virtual.' }
    }

    $nodeEnPath = (Get-Command node.exe -ErrorAction SilentlyContinue).Source
    $nodePortable = Join-Path $env:LOCALAPPDATA 'Pulso/tools/node/node.exe'
    $node = $null
    foreach ($candidato in @($nodeEnPath, $nodePortable)) {
        if (-not $candidato -or -not (Test-Path -LiteralPath $candidato)) { continue }
        $version = & $candidato -p 'process.versions.node'
        if ($LASTEXITCODE -eq 0 -and [version]$version -ge [version]'20.9') {
            $node = $candidato
            break
        }
    }
    if (-not $node) { throw 'Instala Node.js 20.9 o superior para iniciar el frontend.' }
    $env:Path = "$(Split-Path -Parent $node);$env:Path"

    Push-Location $backend
    try {
        & $python -B -c 'from importlib.util import find_spec; raise SystemExit(not all(map(find_spec, (''fastapi'', ''uvicorn'', ''sqlalchemy'', ''psycopg2'', ''pydantic_settings'', ''email_validator'', ''jose'', ''passlib''))))'
        if ($LASTEXITCODE -ne 0) {
            Write-Host 'Instalando dependencias del backend...'
            & $python -m pip install -r requirements.txt
            if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias de Python.' }
        }
        Write-Host 'Verificando PostgreSQL y las tablas de inversiones...'
        & $python -B -m src.inversiones_app
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar PostgreSQL. Revisa el servicio y backend/.env.' }
    } finally {
        Pop-Location
    }

    if (-not (Test-Path -LiteralPath (Join-Path $frontend 'node_modules/next/dist/bin/next'))) {
        $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
        if (-not $npm) { throw 'No se encontro npm.cmd en la instalacion de Node.js.' }
        Push-Location $frontend
        try {
            Write-Host 'Instalando dependencias del frontend...'
            & $npm.Source ci --no-audit --no-fund
            if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias de Next.js.' }
        } finally {
            Pop-Location
        }
    }

    New-Item -ItemType Directory -Path $logs -Force | Out-Null
    $env:API_URL = $apiUrl
    $powershell = Join-Path $env:SystemRoot 'System32/WindowsPowerShell/v1.0/powershell.exe'
    $argumentos = "-NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -LanzadorId $PID -EjecutablePython `"$python`" -EjecutableNode `"$node`""
    Write-Host 'Iniciando FastAPI y Next.js...'
    $supervisor = Iniciar-Servidor 'supervisor' $powershell $argumentos $PSScriptRoot
    Esperar-Respuesta "$apiUrl/health" $supervisor
    Esperar-Respuesta "$webUrl/login" $supervisor
    Esperar-Respuesta "$webUrl/api/activos" $supervisor

    Write-Host ""
    Write-Host "Frontend: $webUrl"
    Write-Host "Backend:  $apiUrl"
    Write-Host "Swagger:  $apiUrl/docs"
    Write-Host "Registros: $logs"
    if (-not $Comprobar) {
        if (-not $SinNavegador) {
            try { Start-Process $webUrl } catch { Write-Host "Abri el panel en $webUrl." }
        }
        Write-Host 'Presiona Enter o cierra esta ventana para detener ambos servidores.'
        while (-not $supervisor.WaitForExit(300)) {
            if (-not [Console]::IsInputRedirected -and [Console]::KeyAvailable) {
                if ([Console]::ReadKey($true).Key -eq [ConsoleKey]::Enter) { break }
            }
        }
        if ($supervisor.HasExited) { throw "Se detuvo un servidor. Revisa los registros en $logs." }
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    $resultado = 1
} finally {
    if ($supervisor -and -not $supervisor.HasExited) {
        try { $supervisor.Kill() } catch { if (-not $supervisor.HasExited) { throw } }
        $null = $supervisor.WaitForExit(5000)
    }
    if ($tieneMutex) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
exit $resultado
