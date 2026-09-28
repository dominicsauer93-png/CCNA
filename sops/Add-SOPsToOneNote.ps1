<#
.SYNOPSIS
  Adds the network SOPs to a OneNote notebook (Microsoft 365) using Microsoft Graph.

.DESCRIPTION
  Reads onenote_pages.json (next to this script), creates the notebook and sections if they
  don't exist, and adds one OneNote page per SOP. Pages that already exist (same title in the
  same section) are skipped, so it is safe to run again after new SOPs are added.
  Use -Replace to delete and re-create existing pages with the latest content.

  First run installs the Microsoft.Graph.Authentication module for the current user and asks
  you to sign in with your Microsoft 365 account (Notes.ReadWrite permission).

.EXAMPLE
  .\Add-SOPsToOneNote.ps1
.EXAMPLE
  .\Add-SOPsToOneNote.ps1 -NotebookName "Network SOPs" -Replace
#>
[CmdletBinding()]
param(
    [string]$NotebookName = "Network SOPs",
    [string]$PagesFile = (Join-Path $PSScriptRoot "onenote_pages.json"),
    [switch]$Replace
)

$ErrorActionPreference = "Stop"
$base = "https://graph.microsoft.com/v1.0/me/onenote"

if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Authentication)) {
    Write-Host "Installing Microsoft.Graph.Authentication (current user only)..."
    Install-Module Microsoft.Graph.Authentication -Scope CurrentUser -Force
}
Import-Module Microsoft.Graph.Authentication
Connect-MgGraph -Scopes "Notes.ReadWrite" -NoWelcome

function Get-All([string]$uri) {
    $items = @()
    while ($uri) {
        $r = Invoke-MgGraphRequest -Method GET -Uri $uri
        $items += $r.value
        $uri = $r.'@odata.nextLink'
    }
    return $items
}

function Encode([string]$s) { [System.Net.WebUtility]::HtmlEncode($s) }

$pages = Get-Content $PagesFile -Raw -Encoding UTF8 | ConvertFrom-Json

# Notebook
$notebook = Get-All "$base/notebooks" | Where-Object { $_.displayName -eq $NotebookName } | Select-Object -First 1
if (-not $notebook) {
    Write-Host "Creating notebook '$NotebookName'"
    $notebook = Invoke-MgGraphRequest -Method POST -Uri "$base/notebooks" `
        -Body (@{ displayName = $NotebookName } | ConvertTo-Json) -ContentType "application/json"
}

# Sections, in the order they appear in the pages file
$sections = @{}
foreach ($s in Get-All "$base/notebooks/$($notebook.id)/sections") { $sections[$s.displayName] = $s }
foreach ($name in ($pages.section | Select-Object -Unique)) {
    if (-not $sections.ContainsKey($name)) {
        Write-Host "Creating section '$name'"
        $sections[$name] = Invoke-MgGraphRequest -Method POST -Uri "$base/notebooks/$($notebook.id)/sections" `
            -Body (@{ displayName = $name } | ConvertTo-Json) -ContentType "application/json"
    }
}

# Pages
$added = 0; $skipped = 0; $replaced = 0
foreach ($name in ($pages.section | Select-Object -Unique)) {
    $sectionId = $sections[$name].id
    $existing = Get-All "$base/sections/$sectionId/pages?`$select=id,title"
    foreach ($p in $pages | Where-Object { $_.section -eq $name }) {
        $match = $existing | Where-Object { $_.title -eq $p.title }
        if ($match) {
            if (-not $Replace) { Write-Host "  skip    $($p.title)"; $skipped++; continue }
            # The page list can lag behind deletes or repeat a page, so a 404 just means it's already gone.
            foreach ($id in ($match.id | Select-Object -Unique)) {
                try { Invoke-MgGraphRequest -Method DELETE -Uri "$base/pages/$id" | Out-Null }
                catch { if ("$_" -notmatch "404|20102") { throw } }
            }
            $replaced++
        }
        $html = "<!DOCTYPE html><html><head><title>$(Encode $p.title)</title>" +
                "<meta charset=`"utf-8`"></head><body>$($p.html)</body></html>"
        Invoke-MgGraphRequest -Method POST -Uri "$base/sections/$sectionId/pages" `
            -Body ([System.Text.Encoding]::UTF8.GetBytes($html)) -ContentType "text/html; charset=utf-8" | Out-Null
        Write-Host "  added   $name / $($p.title)"
        $added++
        Start-Sleep -Milliseconds 500   # stay well under Graph rate limits
    }
}

Write-Host ""
Write-Host "Done. Added $added page(s) ($replaced replaced), skipped $skipped existing."
Write-Host "Open OneNote and look for the '$NotebookName' notebook (it may take a minute to sync)."
