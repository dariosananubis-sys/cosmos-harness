import json
import os
import socket
import subprocess
import tempfile
import textwrap
import threading
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install-claude.sh"


class TcpListener:
    def __enter__(self):
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen()
        self.port = self.sock.getsockname()[1]
        self.running = True

        def accept():
            while self.running:
                try:
                    conn, _ = self.sock.accept()
                    conn.close()
                except OSError:
                    return

        self.thread = threading.Thread(target=accept, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *_args):
        self.running = False
        self.sock.close()


class InstallerTests(unittest.TestCase):
    def environment(self, home: Path, port: int):
        config = home / "Library/Application Support/BrowserClaw/.browseros/config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"ports": {"proxy": port}}), encoding="utf-8")
        bindir = home / "bin"
        bindir.mkdir()
        fake = bindir / "claude"
        fake.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                set -euo pipefail
                STATE="$HOME/fake-mcp-url"
                if [ "${1:-}" = mcp ] && [ "${2:-}" = get ]; then
                  if [ "${FAKE_GET_MODE:-}" = error ]; then
                    echo 'credential store not found' >&2
                    exit 9
                  fi
                  if [ ! -f "$STATE" ]; then
                    echo 'No MCP server found with name: browseros-neo' >&2
                    exit 1
                  fi
                  URL=$(cat "$STATE")
                  printf 'browseros-neo:\n  Scope: User config\n  Status: Connected\n  Type: http\n  URL: %s\n' "$URL"
                elif [ "${1:-}" = mcp ] && [ "${2:-}" = add ]; then
                  URL="${@: -1}"
                  printf '%s\n' "$URL" > "$STATE"
                  printf '{"mcpServers":{"browseros-neo":{"url":"%s"}}}\n' "$URL" > "$HOME/.claude.json"
                  [ "${FAKE_ADD_MODE:-}" != partial-fail ] || exit 9
                  if [ "${FAKE_ADD_MODE:-}" = ledger-fail ]; then
                    mkdir "$HOME/.local/state/browseros-neo-vision-kit/install.json.tmp"
                  fi
                elif [ "${1:-}" = mcp ] && [ "${2:-}" = remove ]; then
                  rm -f "$STATE"
                  printf '{}\n' > "$HOME/.claude.json"
                else
                  exit 2
                fi
                """
            ),
            encoding="utf-8",
        )
        fake.chmod(0o755)
        env = os.environ.copy()
        env["HOME"] = str(home)
        env["PATH"] = str(bindir) + os.pathsep + env["PATH"]
        env.pop("XDG_STATE_HOME", None)
        return env

    def run_installer(self, mode: str, env: dict[str, str], *extra: str):
        return subprocess.run(
            [str(INSTALLER), mode, *extra],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_apply_is_idempotent_and_rollback_is_scoped(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            expected = f"http://127.0.0.1:{listener.port}/mcp"

            first = self.run_installer("--apply", env)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual((home / "fake-mcp-url").read_text().strip(), expected)
            state = home / ".local/state/browseros-neo-vision-kit/install.json"
            self.assertTrue(json.loads(state.read_text())["created"])

            before = (home / ".claude.json").read_bytes()
            second = self.run_installer("--apply", env)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((home / ".claude.json").read_bytes(), before)

            rollback = self.run_installer("--rollback", env)
            self.assertEqual(rollback.returncode, 0, rollback.stderr)
            self.assertFalse((home / "fake-mcp-url").exists())
            self.assertFalse(json.loads(state.read_text())["created"])

    def test_existing_different_server_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            existing = "http://127.0.0.1:65530/mcp"
            (home / "fake-mcp-url").write_text(existing + "\n", encoding="utf-8")

            result = self.run_installer("--apply", env)
            self.assertEqual(result.returncode, 4)
            self.assertEqual((home / "fake-mcp-url").read_text().strip(), existing)
            self.assertFalse(
                (home / ".local/state/browseros-neo-vision-kit/install.json").exists()
            )

    def test_dangling_claude_config_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            target = home / "redirected-config.json"
            (home / ".claude.json").symlink_to(target)

            result = self.run_installer("--apply", env)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stderr)
            self.assertTrue((home / ".claude.json").is_symlink())
            self.assertFalse(target.exists())
            self.assertFalse((home / "fake-mcp-url").exists())

    def test_partial_add_is_rolled_back(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            env["FAKE_ADD_MODE"] = "partial-fail"

            result = self.run_installer("--apply", env)

            self.assertEqual(result.returncode, 5)
            self.assertFalse((home / "fake-mcp-url").exists())
            self.assertFalse((home / ".claude.json").exists())
            self.assertFalse(
                (home / ".local/state/browseros-neo-vision-kit/pending.json").exists()
            )

    def test_ledger_failure_is_rolled_back(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            env["FAKE_ADD_MODE"] = "ledger-fail"

            result = self.run_installer("--apply", env)

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((home / "fake-mcp-url").exists())
            self.assertFalse((home / ".claude.json").exists())
            self.assertFalse(
                (home / ".local/state/browseros-neo-vision-kit/pending.json").exists()
            )

    def test_rollback_refuses_drifted_server(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            first = self.run_installer("--apply", env)
            self.assertEqual(first.returncode, 0, first.stderr)
            changed = "http://127.0.0.1:65530/mcp"
            (home / "fake-mcp-url").write_text(changed + "\n", encoding="utf-8")

            rollback = self.run_installer("--rollback", env)

            self.assertEqual(rollback.returncode, 4)
            self.assertEqual((home / "fake-mcp-url").read_text().strip(), changed)
            state = home / ".local/state/browseros-neo-vision-kit/install.json"
            self.assertTrue(json.loads(state.read_text())["created"])

    def test_rollback_recovers_interrupted_install(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            expected = f"http://127.0.0.1:{listener.port}/mcp"
            (home / "fake-mcp-url").write_text(expected + "\n", encoding="utf-8")
            (home / ".claude.json").write_text(
                json.dumps({"mcpServers": {"browseros-neo": {"url": expected}}}),
                encoding="utf-8",
            )
            state_dir = home / ".local/state/browseros-neo-vision-kit"
            state_dir.mkdir(parents=True)
            pending = state_dir / "pending.json"
            pending.write_text(
                json.dumps(
                    {
                        "server": "browseros-neo",
                        "url": expected,
                        "backup": "",
                        "config_existed": False,
                    }
                ),
                encoding="utf-8",
            )

            reapplied = self.run_installer("--apply", env)
            self.assertEqual(reapplied.returncode, 7)
            self.assertTrue((home / "fake-mcp-url").exists())

            rollback = self.run_installer("--rollback", env)

            self.assertEqual(rollback.returncode, 0, rollback.stderr)
            self.assertFalse((home / "fake-mcp-url").exists())
            self.assertFalse((home / ".claude.json").exists())
            self.assertFalse(pending.exists())

    def test_interrupted_install_with_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            expected = f"http://127.0.0.1:{listener.port}/mcp"
            changed = "http://127.0.0.1:65530/mcp"
            (home / "fake-mcp-url").write_text(changed + "\n", encoding="utf-8")
            state_dir = home / ".local/state/browseros-neo-vision-kit"
            state_dir.mkdir(parents=True)
            pending = state_dir / "pending.json"
            pending.write_text(
                json.dumps(
                    {
                        "server": "browseros-neo",
                        "url": expected,
                        "backup": "",
                        "config_existed": False,
                    }
                ),
                encoding="utf-8",
            )

            rollback = self.run_installer("--rollback", env)

            self.assertEqual(rollback.returncode, 4)
            self.assertEqual((home / "fake-mcp-url").read_text().strip(), changed)
            self.assertTrue(pending.exists())

    def test_recovery_preserves_pending_on_get_error(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            expected = f"http://127.0.0.1:{listener.port}/mcp"
            (home / "fake-mcp-url").write_text(expected + "\n", encoding="utf-8")
            state_dir = home / ".local/state/browseros-neo-vision-kit"
            state_dir.mkdir(parents=True)
            pending = state_dir / "pending.json"
            pending.write_text(
                json.dumps(
                    {
                        "server": "browseros-neo",
                        "url": expected,
                        "backup": "",
                        "config_existed": False,
                    }
                ),
                encoding="utf-8",
            )
            env["FAKE_GET_MODE"] = "error"

            rollback = self.run_installer("--rollback", env)

            self.assertEqual(rollback.returncode, 6)
            self.assertTrue((home / "fake-mcp-url").exists())
            self.assertTrue(pending.exists())

    def test_pending_recovery_wins_over_old_completed_rollback(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            expected = f"http://127.0.0.1:{listener.port}/mcp"
            first = self.run_installer("--apply", env)
            self.assertEqual(first.returncode, 0, first.stderr)
            first_rollback = self.run_installer("--rollback", env)
            self.assertEqual(first_rollback.returncode, 0, first_rollback.stderr)

            (home / "fake-mcp-url").write_text(expected + "\n", encoding="utf-8")
            (home / ".claude.json").write_text(
                json.dumps({"mcpServers": {"browseros-neo": {"url": expected}}}),
                encoding="utf-8",
            )
            state_dir = home / ".local/state/browseros-neo-vision-kit"
            pending = state_dir / "pending.json"
            pending.write_text(
                json.dumps(
                    {
                        "server": "browseros-neo",
                        "url": expected,
                        "backup": "",
                        "config_existed": False,
                    }
                ),
                encoding="utf-8",
            )

            reapplied = self.run_installer("--apply", env)
            self.assertEqual(reapplied.returncode, 7)

            recovered = self.run_installer("--rollback", env)

            self.assertEqual(recovered.returncode, 0, recovered.stderr)
            self.assertFalse((home / "fake-mcp-url").exists())
            self.assertFalse(pending.exists())

    def test_recovery_marks_a_finalized_ledger_inactive(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            expected = f"http://127.0.0.1:{listener.port}/mcp"
            first = self.run_installer("--apply", env)
            self.assertEqual(first.returncode, 0, first.stderr)
            state_dir = home / ".local/state/browseros-neo-vision-kit"
            state = state_dir / "install.json"
            pending = state_dir / "pending.json"
            pending.write_text(
                json.dumps(
                    {
                        "server": "browseros-neo",
                        "url": expected,
                        "backup": "",
                        "config_existed": False,
                    }
                ),
                encoding="utf-8",
            )

            recovered = self.run_installer("--rollback", env)

            self.assertEqual(recovered.returncode, 0, recovered.stderr)
            self.assertFalse((home / "fake-mcp-url").exists())
            self.assertFalse(pending.exists())
            self.assertFalse(json.loads(state.read_text())["created"])

    def test_check_redacts_existing_credentialed_url(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            canary = "NO_DEBE_APARECER"
            unsafe = f"http://user:{canary}@127.0.0.1:65530/mcp?token={canary}"
            (home / "fake-mcp-url").write_text(unsafe + "\n", encoding="utf-8")

            result = self.run_installer("--check", env)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(canary, result.stdout + result.stderr)
            self.assertIn("claude_mcp_matches_preflight=false", result.stdout)

    def test_explicit_config_is_forwarded(self):
        with tempfile.TemporaryDirectory() as directory, TcpListener() as listener:
            home = Path(directory)
            env = self.environment(home, listener.port)
            default = home / "Library/Application Support/BrowserClaw/.browseros/config.json"
            custom = home / "custom/runtime.json"
            custom.parent.mkdir()
            custom.write_text(default.read_text(), encoding="utf-8")
            default.unlink()

            result = self.run_installer("--apply", env, "--config", str(custom))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                (home / "fake-mcp-url").read_text().strip(),
                f"http://127.0.0.1:{listener.port}/mcp",
            )


if __name__ == "__main__":
    unittest.main()
