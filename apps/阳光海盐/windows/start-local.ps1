param(
    [switch]$Share,
    [int]$Port = 43123
)

$ErrorActionPreference = "Stop"
$releaseRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$webRoot = Resolve-Path (Join-Path $releaseRoot "web")
$prefix = if ($Share) { "http://*:$Port/" } else { "http://127.0.0.1:$Port/" }
$openUrl = "http://127.0.0.1:$Port/index.html"

$mimeTypes = @{
    ".html" = "text/html; charset=utf-8"
    ".js" = "application/javascript; charset=utf-8"
    ".json" = "application/json; charset=utf-8"
    ".png" = "image/png"
    ".svg" = "image/svg+xml"
    ".webmanifest" = "application/manifest+json; charset=utf-8"
}

function Get-LanAddresses {
    try {
        return [System.Net.Dns]::GetHostAddresses([System.Net.Dns]::GetHostName()) |
            Where-Object { $_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork -and -not $_.ToString().StartsWith("127.") } |
            ForEach-Object { $_.ToString() } |
            Select-Object -Unique
    } catch {
        return @()
    }
}

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add($prefix)
$listener.Start()

Write-Host "Serving $webRoot"
Write-Host "Local: $openUrl"
if ($Share) {
    Get-LanAddresses | ForEach-Object {
        Write-Host ("LAN:   http://{0}:{1}/index.html" -f $_, $Port)
    }
}

Start-Process $openUrl | Out-Null

try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $requestPath = [Uri]::UnescapeDataString($context.Request.Url.AbsolutePath.TrimStart('/'))
        if ([string]::IsNullOrWhiteSpace($requestPath)) {
            $requestPath = "index.html"
        }

        $targetPath = Join-Path $webRoot $requestPath
        if (Test-Path $targetPath -PathType Container) {
            $targetPath = Join-Path $targetPath "index.html"
        }

        if (-not (Test-Path $targetPath -PathType Leaf)) {
            $context.Response.StatusCode = 404
            $buffer = [System.Text.Encoding]::UTF8.GetBytes("Not Found")
            $context.Response.OutputStream.Write($buffer, 0, $buffer.Length)
            $context.Response.OutputStream.Close()
            continue
        }

        $ext = [System.IO.Path]::GetExtension($targetPath).ToLowerInvariant()
        $context.Response.ContentType = $mimeTypes[$ext]
        if (-not $context.Response.ContentType) {
            $context.Response.ContentType = "application/octet-stream"
        }

        $bytes = [System.IO.File]::ReadAllBytes($targetPath)
        $context.Response.ContentLength64 = $bytes.Length
        $context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
        $context.Response.OutputStream.Close()
    }
} finally {
    $listener.Stop()
    $listener.Close()
}
