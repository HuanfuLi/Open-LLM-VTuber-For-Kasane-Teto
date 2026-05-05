# Frontend rebuild runbook (Phase 4 D-04)

This directory holds the build pipeline for the OLVT frontend bundle
used by this fork. The cloned source tree (frontend-src/web/) is
gitignored; only the patches and this BUILD.md are tracked. The output
of running these steps is the frontend/ directory in the repo root.

## Prerequisites

- Node.js 22.x (verified working at 22.19.0 — see RESEARCH.md)
- npm 10.x (verified working at 10.9.3)

## One-time clone

```sh
cd frontend-src
git clone https://github.com/Open-LLM-VTuber/Open-LLM-VTuber-Web.git web
cd web
# Pin to a specific commit for reproducibility (recorded in
# frontend/.bundle-source on rebuild):
# git checkout <COMMIT_SHA>
```

## Apply patches

```sh
cd frontend-src/web
git apply ../patches/lappmodel-vtube-routing.patch
git apply ../patches/body-bob-extension.patch
```

### createRenderer hot-patch (Pitfall 3 from RESEARCH.md)

Verify the upstream lappmodel.ts has createRenderer(4) or equivalent
buffer-size argument. If the upstream default is smaller, manually
edit before building. Pitfall 3 documents why: Teto rig clips body
parts at smaller buffer sizes.

Search:

```sh
grep -n createRenderer frontend-src/web/src/renderer/WebSDK/src/lappmodel.ts
```

If the call uses a small numeric argument or no argument, edit it to
createRenderer(4) before building.

## Build

```sh
cd frontend-src/web
npm install
npm run build       # output: out/renderer/
```

## Ship

```sh
# From repo root, replace frontend/ with the new build output:
rm -rf frontend
mkdir -p frontend
cp -r frontend-src/web/out/renderer/. frontend/
# Record the source commit + patches applied:
cd frontend-src/web
SHA=$(git rev-parse HEAD)
cd ../..
printf 'upstream: Open-LLM-VTuber/Open-LLM-VTuber-Web\ncommit: %s\npatches:\n  - patches/lappmodel-vtube-routing.patch\n  - patches/body-bob-extension.patch\nbuilt_on: %s\n' "$SHA" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > frontend/.bundle-source
```

Windows PowerShell equivalent for the bundle-source recording:

```powershell
cd frontend-src\web
$SHA = git rev-parse HEAD
cd ..\..
$built = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
"upstream: Open-LLM-VTuber/Open-LLM-VTuber-Web`ncommit: $SHA`npatches:`n  - patches/lappmodel-vtube-routing.patch`n  - patches/body-bob-extension.patch`nbuilt_on: $built" | Out-File -FilePath frontend\.bundle-source -Encoding utf8
```

## Verify

```sh
grep -l ParamAngleXIN frontend/assets/*.js     # Option A patch landed
grep -l ParamBodyAngleY frontend/assets/*.js   # body-bob extension landed
grep -l ParamWatermarkOFF frontend/assets/*.js # watermark fix landed
```

All three commands must print at least one matching file.
