# Frontend patch: VTube Studio parameter routing in `lappmodel.ts`

Apply the four hunks below to the OLVT-Web frontend submodule
(`Open-LLM-VTuber-Web`) at `src/renderer/WebSDK/src/lappmodel.ts`,
then rebuild the frontend (`npm run build` or equivalent) and update
the `frontend` submodule pointer in this repo.

This patch makes the renderer read the model's `*.vtube.json`
(VTube Studio config that lives next to `*.model3.json`), parse its
`ParameterSettings` block (face-tracker input → Live2D parameter
routing), and apply the routing rules every frame between expression
update and breath. It also force-pins `ParamWatermarkOFF=1` every
frame so VTS-extracted models stop showing their built-in watermark
even if the idle motion isn't running.

Mouse drag is fed into the routing as synthetic FaceAngleX/Y/Z so
head tracking starts working for any rig wired to the `*IN` parameter
twins (e.g. Kasane Teto). Models that don't ship a `.vtube.json`
silently degrade to the original behavior.

## Hunk 1 — add field

In the field declarations (the block ending with `_consistency: boolean;`),
add at the end:

```ts
  _vtubeRoutings: Array<{
    input: string;
    inputLow: number;
    inputHigh: number;
    outputLow: number;
    outputHigh: number;
    clampInput: boolean;
    clampOutput: boolean;
    outputId: CubismIdHandle;
  }>;
```

## Hunk 2 — initialize in constructor

In `public constructor()`, after `this._consistency = false;`, add:

```ts
    this._vtubeRoutings = [];
```

## Hunk 3 — load `.vtube.json` from `loadAssets`

In `public loadAssets(dir: string, fileName: string): void {`, after
`this._modelHomeDir = dir;`, add:

```ts
    this._loadVtubeRouting(fileName);
```

Then add this new private method to the class (anywhere — next to
`loadAssets` is fine):

```ts
  private _loadVtubeRouting(modelFileName: string): void {
    const vtubeFile = modelFileName.replace(/\.model3\.json$/, ".vtube.json");
    if (vtubeFile === modelFileName) return;

    fetch(`${this._modelHomeDir}${vtubeFile}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((cfg: any) => {
        if (!cfg || !Array.isArray(cfg.ParameterSettings)) return;
        const idMgr = CubismFramework.getIdManager();
        this._vtubeRoutings = cfg.ParameterSettings
          .filter(
            (p: any) =>
              p && typeof p.Input === "string" && typeof p.OutputLive2D === "string"
          )
          .map((p: any) => ({
            input: String(p.Input),
            inputLow: Number(p.InputRangeLower),
            inputHigh: Number(p.InputRangeUpper),
            outputLow: Number(p.OutputRangeLower),
            outputHigh: Number(p.OutputRangeUpper),
            clampInput: !!p.ClampInput,
            clampOutput: !!p.ClampOutput,
            outputId: idMgr.getId(String(p.OutputLive2D)),
          }));
        CubismLogInfo(
          `[VTubeRouting] Loaded ${this._vtubeRoutings.length} routes from ${vtubeFile}`
        );
      })
      .catch(() => {
        /* .vtube.json absent or invalid — keep stock behavior */
      });
  }
```

## Hunk 4 — apply routing + watermark fix in `update()`

In `public update()`, find this block:

```ts
    if (this._expressionManager != null) {
      this._expressionManager.updateMotion(this._model, deltaTimeSeconds); // 表情でパラメータ更新（相対変化）
    }
```

Immediately AFTER the closing brace of that `if`, BEFORE the
`// ドラッグによる変化` comment, insert:

```ts
    // VTube Studio parameter routing (Option A patch).
    // Synthesizes face-tracker inputs from drag and applies the model's
    // .vtube.json ParameterSettings rules to the *IN-suffixed twins
    // that the rig is actually bound to. No-op if the model doesn't
    // ship a .vtube.json.
    if (this._vtubeRoutings.length > 0) {
      const dx = this._dragX;
      const dy = this._dragY;
      const inputs: { [k: string]: number } = {
        FaceAngleX: dx * 30,
        FaceAngleY: -dy * 30,
        FaceAngleZ: -dx * 30 * 0.5,
        FacePositionX: dx * 0.3,
        FacePositionY: -dy * 0.3,
        FacePositionZ: 0,
        EyeLeftX: dx,
        EyeLeftY: dy,
        EyeRightX: dx,
        EyeRightY: dy,
        EyeOpenLeft: 1,
        EyeOpenRight: 1,
        BrowLeftY: 0,
        BrowRightY: 0,
        MouthOpen: 0,
        MouthSmile: 0,
        MouthX: 0,
        JawOpen: 0,
        CheekPuff: 0,
        MouthPucker: 0,
        MouthFunnel: 0,
        TongueOut: 0,
      };
      for (const r of this._vtubeRoutings) {
        let v = inputs[r.input] ?? 0;
        if (r.clampInput) {
          v = Math.max(r.inputLow, Math.min(r.inputHigh, v));
        }
        const span = r.inputHigh - r.inputLow;
        const t = span !== 0 ? (v - r.inputLow) / span : 0;
        let out = r.outputLow + t * (r.outputHigh - r.outputLow);
        if (r.clampOutput) {
          const lo = Math.min(r.outputLow, r.outputHigh);
          const hi = Math.max(r.outputLow, r.outputHigh);
          out = Math.max(lo, Math.min(hi, out));
        }
        this._model.setParameterValueById(r.outputId, out);
      }
    }

    // Watermark: force-off every frame for VTS-extracted models that
    // bake a watermark drawable controlled by ParamWatermarkOFF.
    // setParameterValueById is a no-op for parameters that don't exist,
    // so this is safe for non-VTS models.
    this._model.setParameterValueById(
      CubismFramework.getIdManager().getId("ParamWatermarkOFF"),
      1
    );
```

## Build & ship

```sh
cd path/to/Open-LLM-VTuber-Web
git checkout -b feat/vtube-routing
# apply hunks above
npm install
npm run build           # produces dist/
git add -A && git commit -m "feat: VTS .vtube.json parameter routing + watermark fix"

# back in this repo:
cd path/to/Open-LLM-VTuber
cd frontend
git fetch <your fork> feat/vtube-routing
git checkout <commit-sha>
cd ..
git add frontend
git commit -m "chore(frontend): bump submodule for VTS routing"
```

## What this fixes

- **Head/body tracking on Teto and other VTS-extracted models.**
  Mouse drag is mapped to FaceAngleX/Y/Z and routed through
  `ParamAngleXIN`/`YIN`/`ZIN` (and the body equivalents) per the
  `.vtube.json` rules, instead of getting added to the unbound
  `ParamAngleX` etc. that the stock LAppModel hardcodes.
- **Watermark on VTS-extracted models.** Independent of the idle
  motion — pinned every frame.

## What it does NOT fix

- Real face tracking from a camera. There is no tracker; drag is the
  only synthetic input. Mouth/brow/cheek inputs default to 0 (so the
  mouth IN parameters sit neutral until lip-sync overrides them).
- VTube Studio hotkey-based outfit toggles (`【SV】Mic`, `Baguette`,
  etc.). Those are expression files; switching them works through
  the existing expression API.
- Per-model FIX/correction parameters (`ParamXFIX`, `ParamBODYFIXX`,
  etc.) that are driven by VTS through non-`ParameterSettings` rules.
  If alignment artifacts remain after this patch, a second pass would
  bake their values into the model's idle motion.
