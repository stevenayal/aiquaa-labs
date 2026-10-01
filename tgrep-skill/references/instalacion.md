# Instalación — tgrep

La skill **nunca** instala tgrep por cuenta propia. Estos comandos se documentan para que el
usuario los ejecute (o confirme que el agente los ejecute).

## Homebrew (Linux, macOS)

```bash
brew install tgrep
```

## Desde el código fuente (requiere Rust/Cargo)

```bash
git clone https://github.com/stevenayal/tgrep.git
cd tgrep
cargo install --path tgrep-cli --locked
```

## Binarios pre-compilados

Desde las releases de GitHub (Linux musl, macOS Intel/Apple Silicon, Windows x64/ARM64).
Ejemplo Linux x86_64:

```bash
tmpdir="$(mktemp -d)"
gh release download --repo microsoft/tgrep -p '*x86_64-unknown-linux-musl.tar.gz' -D "$tmpdir"
tar xzf "$tmpdir"/tgrep-*-x86_64-unknown-linux-musl.tar.gz -C "$tmpdir"
install -Dm755 "$tmpdir/tgrep" "$HOME/.local/bin/tgrep"
rm -rf "$tmpdir"
```

Asegurarse de que `$HOME/.local/bin` esté en el `PATH`.

## Integración MCP para agentes (opcional)

El repo trae un instalador que registra herramientas MCP (`search_code`, `find_files`) y un
hook de arranque para Codex o pi (Linux/macOS, Python 3.11+):

```bash
./install-agent.sh install --agent codex --root /path/al/repo
./install-agent.sh doctor  --agent codex --root /path/al/repo
```

Ver `scripts/agent/README.md` en el repo de tgrep. Esta skill no lo ejecuta — modifica la
configuración del agente y requiere confirmación del usuario.

## Después de instalar

```bash
echo ".tgrep/" >> .gitignore
tgrep serve . &        # o: tgrep index .
tgrep status .
```
