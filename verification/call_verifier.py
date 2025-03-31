import os
import importlib.util
import xml.etree.ElementTree as ET
from typing import List


def load_ctl_expressions(ctl_path: str) -> List[str]:
    with open(ctl_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def load_bpmn_xml(bpmn_path: str) -> str:
    with open(bpmn_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_verifiers(verifiers_dir: str):
    verifiers = []
    for filename in os.listdir(verifiers_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_path = os.path.join(verifiers_dir, filename)
            module_name = filename[:-3]

            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "verify"):
                    verifiers.append(module.verify)
    return verifiers


def main(ctl_path: str, bpmn_path: str):
    ctl_expressions = load_ctl_expressions(ctl_path)
    bpmn_xml = load_bpmn_xml(bpmn_path)
    verifiers = load_verifiers("verifiers")

    failed_ctl = []

    for ctl in ctl_expressions:
        for verify_func in verifiers:
            try:
                result = verify_func(ctl, bpmn_xml)
                if not result:
                    failed_ctl.append(ctl)
                    break
            except Exception as e:
                print(f"Verifier error with CTL '{ctl}': {e}")
                failed_ctl.append(ctl)
                break

    print("Failed CTL expressions:")
    for ctl in failed_ctl:
        print(ctl)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python main.py <path_to_ctl_file> <path_to_bpmn_file>")
        exit(1)
    main(sys.argv[1], sys.argv[2])
