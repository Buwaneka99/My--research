# backup_claude_chats.ps1
# Copies every Claude Code transcript out of %USERPROFILE%\.claude and also
# renders each one as a readable .md file.
#
# Re-runnable: just run it again any time to pick up new sessions.
#   pwsh -File D:\Research\_claude_chat_backup\backup_claude_chats.ps1
#   pwsh -File ...\backup_claude_chats.ps1 -IncludeThinking

param(
    [string] $Source      = "$env:USERPROFILE\.claude",
    [string] $Destination = 'D:\Research\_claude_chat_backup',
    [switch] $IncludeThinking
)

$ErrorActionPreference = 'Stop'

$rawDir = Join-Path $Destination 'raw'
$mdDir  = Join-Path $Destination 'markdown'
foreach ($d in @($Destination, $rawDir, $mdDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

function Get-PartText {
    param($Content)

    # message.content is either a plain string or an array of typed parts.
    if ($Content -is [string]) { return @{ Text = $Content; Tools = @() } }

    $sb    = [System.Text.StringBuilder]::new()
    $tools = @()

    foreach ($p in $Content) {
        switch ($p.type) {
            'text' { [void]$sb.AppendLine($p.text); [void]$sb.AppendLine() }
            'thinking' {
                if ($IncludeThinking) {
                    [void]$sb.AppendLine('<details><summary>thinking</summary>')
                    [void]$sb.AppendLine()
                    [void]$sb.AppendLine($p.thinking)
                    [void]$sb.AppendLine()
                    [void]$sb.AppendLine('</details>')
                    [void]$sb.AppendLine()
                }
            }
            'image' { [void]$sb.AppendLine('`[image pasted]`'); [void]$sb.AppendLine() }
            'tool_use' {
                $i = $p.input
                $arg = $i.file_path
                if (-not $arg) { $arg = $i.notebook_path }
                if (-not $arg) { $arg = $i.command }
                if (-not $arg) { $arg = $i.pattern }
                if (-not $arg) { $arg = $i.prompt }
                if ($arg) {
                    $arg = ($arg -replace '\s+', ' ').Trim()
                    if ($arg.Length -gt 160) { $arg = $arg.Substring(0, 160) + '...' }
                }
                $tools += ('{0}{1}' -f $p.name, $(if ($arg) { " -> $arg" } else { '' }))
            }
            'tool_result' {
                # Skipped on purpose: tool output is what makes these files huge,
                # and the raw .jsonl still has all of it.
            }
        }
    }

    return @{ Text = $sb.ToString().TrimEnd(); Tools = $tools }
}

function Convert-Transcript {
    param([string] $JsonlPath, [string] $ProjectName, [string] $OutPath)

    $lines = Get-Content -LiteralPath $JsonlPath
    $turns = New-Object System.Collections.ArrayList
    $users = 0; $bots = 0
    $first = $null; $last = $null

    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { $o = $line | ConvertFrom-Json } catch { continue }
        if ($o.type -ne 'user' -and $o.type -ne 'assistant') { continue }

        $parsed = Get-PartText -Content $o.message.content
        $text   = $parsed.Text

        # Drop the machine-generated envelopes; keep what a human actually sees.
        if ($o.type -eq 'user' -and $text -match '^\s*<(system-reminder|command-name|command-message|local-command|ide_opened_file|ide_selection)') {
            continue
        }
        if ([string]::IsNullOrWhiteSpace($text) -and $parsed.Tools.Count -eq 0) { continue }

        $ts = $null
        if ($o.timestamp) { try { $ts = [datetime]$o.timestamp } catch { } }
        if ($ts) {
            if (-not $first -or $ts -lt $first) { $first = $ts }
            if (-not $last  -or $ts -gt $last)  { $last  = $ts }
        }

        if ($o.type -eq 'user') { $users++ } else { $bots++ }

        [void]$turns.Add([pscustomobject]@{
            Role  = $o.type
            Time  = $ts
            Text  = $text
            Tools = $parsed.Tools
        })
    }

    $sid = [System.IO.Path]::GetFileNameWithoutExtension($JsonlPath)
    $out = [System.Text.StringBuilder]::new()

    [void]$out.AppendLine("# Claude Code session - $ProjectName")
    [void]$out.AppendLine()
    [void]$out.AppendLine("| | |")
    [void]$out.AppendLine("|---|---|")
    [void]$out.AppendLine("| Session ID | ``$sid`` |")
    [void]$out.AppendLine("| Started | $(if ($first) { $first.ToString('yyyy-MM-dd HH:mm') } else { 'unknown' }) |")
    [void]$out.AppendLine("| Last activity | $(if ($last) { $last.ToString('yyyy-MM-dd HH:mm') } else { 'unknown' }) |")
    [void]$out.AppendLine("| Turns | $users user / $bots assistant |")
    [void]$out.AppendLine("| Raw transcript | ``raw/$ProjectName/$sid.jsonl`` |")
    [void]$out.AppendLine()
    [void]$out.AppendLine("> Tool output is omitted here for readability. The raw ``.jsonl`` has the complete record.")
    [void]$out.AppendLine()
    [void]$out.AppendLine('---')
    [void]$out.AppendLine()

    foreach ($t in $turns) {
        $who   = if ($t.Role -eq 'user') { 'User' } else { 'Claude' }
        $stamp = if ($t.Time) { $t.Time.ToString('yyyy-MM-dd HH:mm') } else { '' }
        [void]$out.AppendLine("## $who - $stamp")
        [void]$out.AppendLine()
        if ($t.Text) { [void]$out.AppendLine($t.Text); [void]$out.AppendLine() }
        foreach ($tool in $t.Tools) { [void]$out.AppendLine("- ``$tool``") }
        if ($t.Tools.Count -gt 0) { [void]$out.AppendLine() }
    }

    $out.ToString() | Set-Content -LiteralPath $OutPath -Encoding utf8
    return [pscustomobject]@{ Session = $sid; Project = $ProjectName; User = $users; Assistant = $bots; First = $first; Last = $last }
}

# ---- run ----------------------------------------------------------------

$projectsRoot = Join-Path $Source 'projects'
$transcripts  = Get-ChildItem -LiteralPath $projectsRoot -Recurse -File -Filter *.jsonl
$summaries    = New-Object System.Collections.ArrayList

foreach ($t in $transcripts) {
    $proj = $t.Directory.Name

    $rawProj = Join-Path $rawDir $proj
    $mdProj  = Join-Path $mdDir  $proj
    foreach ($d in @($rawProj, $mdProj)) {
        if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
    }

    Copy-Item -LiteralPath $t.FullName -Destination (Join-Path $rawProj $t.Name) -Force

    $mdPath = Join-Path $mdProj ($t.BaseName + '.md')
    $s = Convert-Transcript -JsonlPath $t.FullName -ProjectName $proj -OutPath $mdPath
    [void]$summaries.Add($s)
    Write-Host ("  {0,-58} -> {1} turns" -f "$proj/$($t.Name)", ($s.User + $s.Assistant))
}

# Claude's own memory files travel with the chats.
$memSrc = Join-Path $projectsRoot 'd--Research\memory'
if (Test-Path $memSrc) {
    $memDst = Join-Path $Destination 'memory'
    if (-not (Test-Path $memDst)) { New-Item -ItemType Directory -Path $memDst | Out-Null }
    Copy-Item -Path (Join-Path $memSrc '*') -Destination $memDst -Recurse -Force
    Write-Host '  memory/ copied'
}

# INDEX.md - the one file to hand back to Claude later.
$idx = [System.Text.StringBuilder]::new()
[void]$idx.AppendLine('# Claude Code chat backup')
[void]$idx.AppendLine()
[void]$idx.AppendLine("Backed up: $(Get-Date -Format 'yyyy-MM-dd HH:mm')  |  Source: ``$Source``")
[void]$idx.AppendLine()
[void]$idx.AppendLine('| Project | Session | Started | Last activity | Turns | Markdown |')
[void]$idx.AppendLine('|---|---|---|---|---|---|')
foreach ($s in ($summaries | Sort-Object First)) {
    $short = $s.Session.Substring(0, 8)
    [void]$idx.AppendLine(('| {0} | `{1}` | {2} | {3} | {4} | [md](markdown/{5}/{6}.md) |' -f `
        $s.Project, $short,
        $(if ($s.First) { $s.First.ToString('yyyy-MM-dd HH:mm') } else { '?' }),
        $(if ($s.Last)  { $s.Last.ToString('yyyy-MM-dd HH:mm') }  else { '?' }),
        ($s.User + $s.Assistant), $s.Project, $s.Session))
}
[void]$idx.AppendLine()
[void]$idx.AppendLine('## Layout')
[void]$idx.AppendLine()
[void]$idx.AppendLine('- `raw/<project>/<session>.jsonl` - byte-for-byte copy of the original transcript.')
[void]$idx.AppendLine('- `markdown/<project>/<session>.md` - readable version, tool output stripped.')
[void]$idx.AppendLine('- `memory/` - Claude''s saved memory notes for this project.')
[void]$idx.AppendLine()
[void]$idx.AppendLine('## Re-run')
[void]$idx.AppendLine()
[void]$idx.AppendLine('```powershell')
[void]$idx.AppendLine('pwsh -File D:\Research\_claude_chat_backup\backup_claude_chats.ps1')
[void]$idx.AppendLine('```')
$idx.ToString() | Set-Content -LiteralPath (Join-Path $Destination 'INDEX.md') -Encoding utf8

Write-Host ''
Write-Host ("Done. {0} sessions -> {1}" -f $summaries.Count, $Destination)
