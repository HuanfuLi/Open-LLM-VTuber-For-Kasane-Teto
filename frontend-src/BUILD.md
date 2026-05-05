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

The combined patch (both Option A routing and body-bob extension) is in
`lappmodel-vtube-routing.patch`. The `body-bob-extension.patch` documents
the body-bob changes but the combined diff is applied via the routing patch
(both patches modify the same file in overlapping regions).

```sh
cd frontend-src/web
git apply ../patches/lappmodel-vtube-routing.patch
```

### createRenderer hot-patch (Pitfall 3 from RESEARCH.md)

The patch already includes `createRenderer(4)` changes. If re-applying to
a new upstream commit, verify:

```sh
grep -n createRenderer frontend-src/web/src/renderer/WebSDK/src/lappmodel.ts
```

All occurrences should use `createRenderer(4)`.

## Build

The upstream uses `npm run build:web` (not `npm run build`) for the
web-only renderer output. The output goes to `frontend-src/web/dist/web/`
(controlled by `vite.config.ts` `outDir: path.join(__dirname, 'dist/web')`).

```sh
cd frontend-src/web
npm install
npm run build:web   # output: dist/web/
```

Verify the output:

```sh
ls frontend-src/web/dist/web/
# Must contain index.html and assets/
ls frontend-src/web/dist/web/assets/*.js
# Must contain main-*.js
```

## Ship

```sh
# From repo root, replace frontend/ with the new build output:
rm -rf frontend
mkdir -p frontend
cp -r frontend-src/web/dist/web/. frontend/
# Record the source commit + patches applied:
cd frontend-src/web
SHA=$(git rev-parse HEAD)
cd ../..
printf 'upstream: Open-LLM-VTuber/Open-LLM-VTuber-Web\ncommit: %s\npatches:\n  - patches/lappmodel-vtube-routing.patch\n  - patches/body-bob-extension.patch\nbuild_command: npm run build:web\nbuild_output: dist/web/\nbuilt_on: %s\n' "$SHA" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > frontend/.bundle-source
```

Windows PowerShell equivalent for the bundle-source recording:

```powershell
cd frontend-src\web
$SHA = git rev-parse HEAD
cd ..\..
$built = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
"upstream: Open-LLM-VTuber/Open-LLM-VTuber-Web`ncommit: $SHA`npatches:`n  - patches/lappmodel-vtube-routing.patch`n  - patches/body-bob-extension.patch`nbuild_command: npm run build:web`nbuild_output: dist/web/`nbuilt_on: $built" | Out-File -FilePath frontend\.bundle-source -Encoding utf8
```

## Verify

```sh
grep -l FaceAngleX frontend/assets/*.js         # Option A routing patch landed
grep -l ParamBodyAngleY frontend/assets/*.js    # body-bob extension landed
grep -l ParamWatermarkOFF frontend/assets/*.js  # watermark fix landed
```

All three commands must print at least one matching file.

Note: `ParamAngleXIN` does NOT appear directly in the bundle — it is a
runtime string parsed from the model's `.vtube.json` ParameterSettings.
The Option A patch is generic: it reads any OutputLive2D values from the
JSON and routes them. `FaceAngleX` and `ParameterSettings` ARE in the
bundle as proof that the routing code compiled in.
