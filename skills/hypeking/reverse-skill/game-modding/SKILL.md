---
name: game-modding
description: "Game modding and reverse engineering orchestrator. Covers engine reconnaissance (Unity, Unreal, Bethesda, Godot, native, retro-decomp), memory hacking, mod loading (BepInEx, MelonLoader, UE4SS, SMAPI), binary patching, game automation, and cross-game mashups."
---

# Game Modding & Reverse Engineering Orchestrator

Unified game modding and binary exploration pipeline integrated from `universal-modder`.

## Modular Structure

```
game-modding/
├── SKILL.md                 ← Orchestrator (you are here)
├── game-recon/              ← Game & engine reconnaissance, loaders, anti-cheat detection
├── game-automation/         ← Windows/Linux game automation, headless interaction, memory inspection
├── mod-any-game/            ← Core modding workflows, lifecycle, and vertical slices
├── mashup-mods/             ← Cross-game asset & mechanics integration
└── references/engines/      ← Engine-specific modding & reverse engineering playbooks:
    ├── unity.md             (IL2CPP, Mono, BepInEx, MelonLoader, dnSpy, Cpp2IL)
    ├── unreal.md            (UAssetGUI, FModel, UE4SS, Kismet bytecode, Zen store)
    ├── bethesda.md          (Creation Kit, xEdit, ESM/ESP/ESL, Papyrus, SKSE)
    ├── godot.md             (GDScript decompile, PCK unpacking, GodotEnv)
    ├── native.md            (IDA Pro, Ghidra, x64dbg, MinHook, DLL injection)
    └── retro-decomp.md      (Disassembly, IDA decompiler, symbol recovery)
```

## Modding Pipeline

### 1. Engine Reconnaissance (`game-recon`)
Inspect target game directory, identify engine, binary architecture (x86/x64), runtime (Mono vs IL2CPP, CLR, native C++), anti-cheat status (EAC, BattlEye, Vanguard), and active mod loaders.
- Mono Unity: inspect `Managed/Assembly-CSharp.dll` with dnSpy/ILSpy.
- IL2CPP Unity: dump metadata with `Il2CppDumper` or `Cpp2IL`, inspect `global-metadata.dat`.
- Unreal Engine: locate `.pak`/`.ucas`/`.utoc` files, extract encryption keys using FModel or UE4SS.
- Native C++: find exports, string tables, entry points, and hookable APIs with Ghidra/IDA.

### 2. Mod Creation & Hooking (`mod-any-game`)
Develop the mod targeting the appropriate loader or injection vector:
- Unity: write BepInEx 5/6 plugin or Harmony patches for runtime method detours.
- Unreal: write Lua scripts or C++ mods for UE4SS, or patch cooked assets using UAssetGUI.
- Bethesda: build lightweight ESL/ESP plugins or SKSE runtime plugins.
- Native: compile a dynamic library (DLL / `.so`) with MinHook or inline assembly detours.

### 3. Verification & In-Game Automation (`game-automation`)
Verify mod behavior directly in game:
- Launch game in isolated test environment (offline mode).
- Verify hook execution, memory state, and logs.
- Capture execution evidence and logs.

### 4. Cross-Game Mashups (`mashup-mods`)
Translate mechanics, camera systems, or HUD elements between disparate engines.

### 5. Asset Generation
- **OPTIONAL_ON_DEMAND**: Fal/Blender generative asset pipelines (`fal-assets`, `asset-pipeline`) are strictly optional and invoked on demand. Core modding functions remain fully operable without external generative services.
