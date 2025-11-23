$base = Get-Content "static/css/style.css" -TotalCount 980
$profile = Get-Content "temp_profile_css.css"
$auth = Get-Content "temp_auth_css.css"
$casino = Get-Content "static/css/casino.css"
$animations = Get-Content "static/css/animations.css"

$all = $base + $profile + $auth + $casino + $animations
$all | Set-Content "static/css/style.css" -Encoding UTF8
Write-Host "CSS Reconstructed Successfully"
