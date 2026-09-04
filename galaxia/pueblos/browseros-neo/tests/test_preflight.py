import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/preflight.py"
SPEC = importlib.util.spec_from_file_location("neo_preflight", MODULE_PATH)
preflight = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(preflight)


class PreflightTests(unittest.TestCase):
    def write_config(self, data):
        directory = tempfile.TemporaryDirectory(dir=Path.home())
        path = Path(directory.name) / "config.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.addCleanup(directory.cleanup)
        return path

    def test_loopback_ipv4(self):
        self.assertTrue(preflight.is_loopback_host("127.0.0.1"))

    def test_loopback_localhost(self):
        self.assertTrue(preflight.is_loopback_host("localhost"))

    def test_loopback_ipv6(self):
        self.assertTrue(preflight.is_loopback_host("::1"))
        self.assertEqual(
            preflight.validate_loopback_url("http://[::1]:9010/mcp", "/mcp"),
            "http://[::1]:9010/mcp",
        )

    def test_rejects_external_host(self):
        with self.assertRaisesRegex(ValueError, "no es loopback"):
            preflight.validate_loopback_url("https://example.com:9010/mcp", "/mcp")

    def test_rejects_missing_port(self):
        with self.assertRaisesRegex(ValueError, "no declara puerto"):
            preflight.validate_loopback_url("http://127.0.0.1/mcp", "/mcp")

    def test_rejects_credentials_query_and_fragment(self):
        unsafe = [
            "http://user:canary@127.0.0.1:9010/mcp",
            "http://127.0.0.1:9010/mcp?token=canary",
            "http://127.0.0.1:9010/mcp#canary",
        ]
        for url in unsafe:
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "credenciales"):
                preflight.validate_loopback_url(url, "/mcp")

    def test_extracts_sidecar_ports(self):
        result = preflight.extract_endpoints(
            {"ports": {"proxy": 9010, "cdp": 9117, "server": 9211}}
        )
        self.assertEqual(result["mcp_url"], "http://127.0.0.1:9010/mcp")
        self.assertEqual(result["cdp_url"], "http://127.0.0.1:9117")
        self.assertEqual(result["server_url"], "http://127.0.0.1:9211")

    def test_extracts_single_runtime_mcp_url(self):
        result = preflight.extract_endpoints(
            {"runtime": {"mcpUrl": "http://127.0.0.1:9200/mcp"}}
        )
        self.assertEqual(result["mcp_url"], "http://127.0.0.1:9200/mcp")

    def test_extracts_runtime_base_url(self):
        result = preflight.extract_endpoints({"url": "http://127.0.0.1:9200"})
        self.assertEqual(result["mcp_url"], "http://127.0.0.1:9200/mcp")

    def test_rejects_ambiguous_runtime_urls(self):
        with self.assertRaisesRegex(ValueError, "varios endpoints"):
            preflight.extract_endpoints(
                {
                    "a": "http://127.0.0.1:9200/mcp",
                    "b": "http://127.0.0.1:9201/mcp",
                }
            )

    def test_rejects_symlink_config(self):
        with tempfile.TemporaryDirectory(dir=Path.home()) as directory:
            root = Path(directory)
            real = root / "real.json"
            link = root / "link.json"
            real.write_text("{}", encoding="utf-8")
            link.symlink_to(real)
            with self.assertRaisesRegex(ValueError, "symlink"):
                preflight.read_json(link)

    def test_rejects_symlink_parent_inside_home(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            real = home / "real"
            real.mkdir()
            (real / "config.json").write_text("{}", encoding="utf-8")
            linked = home / "linked"
            linked.symlink_to(real, target_is_directory=True)
            with mock.patch.dict("os.environ", {"HOME": str(home)}):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    preflight.read_json(linked / "config.json")

    def test_inspect_does_not_expose_install_id(self):
        path = self.write_config(
            {
                "ports": {"proxy": 9},
                "instance": {"install_id": "must-not-appear"},
            }
        )
        report = preflight.inspect(str(path))
        self.assertNotIn("install_id", json.dumps(report))
        self.assertNotIn("must-not-appear", json.dumps(report))

    def test_missing_config_is_not_ready(self):
        report = preflight.inspect("/definitely/missing/neo-config.json")
        self.assertFalse(report["base_ready"])
        self.assertTrue(report["issues"])

    @mock.patch.object(preflight, "tcp_probe", return_value=True)
    @mock.patch.object(preflight, "cdp_probe", return_value=(True, "Chrome/Test"))
    def test_matching_sidecar_and_runtime_are_accepted(self, _cdp, _tcp):
        sidecar = self.write_config(
            {"ports": {"proxy": 9010, "cdp": 9117, "server": 9211}}
        )
        runtime = self.write_config({"url": "http://127.0.0.1:9010"})
        with mock.patch.object(preflight, "candidate_paths", return_value=[sidecar, runtime]):
            report = preflight.inspect()
        self.assertTrue(report["base_ready"])
        self.assertEqual(len(report["config_sources"]), 2)
        self.assertEqual(report["cdp_url"], "http://127.0.0.1:9117")

    def test_conflicting_sources_fail_closed(self):
        first = self.write_config({"url": "http://127.0.0.1:9010"})
        second = self.write_config({"url": "http://127.0.0.1:9011"})
        with mock.patch.object(preflight, "candidate_paths", return_value=[first, second]):
            report = preflight.inspect()
        self.assertFalse(report["base_ready"])
        self.assertIn("discrepan", " ".join(report["issues"]))

    def test_conflicting_cdp_sources_fail_closed(self):
        first = self.write_config(
            {"ports": {"proxy": 9010, "cdp": 9117, "server": 9211}}
        )
        second = self.write_config(
            {"ports": {"proxy": 9010, "cdp": 9222, "server": 9211}}
        )
        with mock.patch.object(preflight, "candidate_paths", return_value=[first, second]):
            report = preflight.inspect()
        self.assertFalse(report["base_ready"])
        self.assertIn("cdp_url", " ".join(report["issues"]))


if __name__ == "__main__":
    unittest.main()
