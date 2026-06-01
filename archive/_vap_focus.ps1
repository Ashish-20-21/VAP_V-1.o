
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

$proc = Get-Process -Id 17148 -ErrorAction SilentlyContinue

if ($proc -and $proc.MainWindowHandle -ne 0) {
    # SW_RESTORE (9) — restores window if minimized/hidden before focusing
    [Win32]::ShowWindow($proc.MainWindowHandle, 9)

    # Bring window to foreground and give it keyboard focus
    [Win32]::SetForegroundWindow($proc.MainWindowHandle)
}
