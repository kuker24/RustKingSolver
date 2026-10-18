# cli-pentestv1 — omp ready-to-use bundle

Kumpulan **skills**, **MCP config**, dan **AGENTS.md** untuk OpenCode / omp (`oh-my-pi`).
Repo ini adalah bundle restore: clone/pull, lalu taruh file-nya ke `~/.omp/agent/`.

## Isi repo

| Path | Fungsi |
|---|---|
| `skills/` | Seluruh skill `hypeking` (pwn / reverse / CTF / log-SIEM / red-team, dst). |
| `mcp.json` | Daftar MCP server (scopesentry, playwright, jshook, idapro, ghidra, sliver). |
| `AGENTS.md` | File instruksi agent. |
| `config.yml` | Setelan omp (model role, thinking level). |
| `models.yml` | Definisi provider/model. |

## Cara pasang (restore)

Jalankan dari root repo ini. Asumsi target `~/.omp/agent/` sudah ada.

```bash
TARGET="$HOME/.omp/agent"
mkdir -p "$TARGET/skills"

# 1. skills
rsync -a skills/ "$TARGET/skills/"

# 2. config + MCP + instruksi agent
cp mcp.json config.yml models.yml AGENTS.md "$TARGET/"
```

Lalu isi nilai yang di-redact (lihat bawah) di environment kamu sebelum menjalankan omp.

## Environment variable yang wajib di-set

Kredensial **tidak** ada di repo ini — semua ditulis sebagai placeholder `${...}`.

| Variable | Dipakai oleh | Keterangan |
|---|---|---|
| `NINEROUTER_API_KEY` | `models.yml` | API key gateway 9router (mis. `sk-...`). Diisi manual. |
| `SCOPESENTRY_API_KEY` | `mcp.json` | Header `X-API-Key` untuk server MCP `scopesentry`. |
| `SLIVER_MULTIPLAYER_CFG` | `mcp.json` | Path ke config client sliver. |

Contoh (jangan di-commit):

```bash
export NINEROUTER_API_KEY="sk-xxxxxxxxxxxxxxxx"
export SCOPESENTRY_API_KEY="xxxxxxxx"
export SLIVER_MULTIPLAYER_CFG="$HOME/.sliver-client/configs"
```

## Catatan

- `models.yml` semula berisi API key asli; di repo ini sudah diganti `${NINEROUTER_API_KEY}`.
- Folder runtime (`sessions/`, `cache/`, `blobs/`, `logs/`, `*.db`) **sengaja tidak** disertakan — lihat `.gitignore`.
- Sebagian MCP server di `mcp.json` berstatus `enabled: false`; aktifkan sesuai kebutuhan.

## Sync balik (backup dari mesin kerja)

```bash
# dari ~/.omp/agent
rsync -a --exclude '__pycache__' --exclude '*.pyc' skills/ /path/to/cli-pentestv1/skills/
cp mcp.json config.yml AGENTS.md /path/to/cli-pentestv1/
# edit models.yml → ganti apiKey jadi ${NINEROUTER_API_KEY}
```
