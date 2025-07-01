import subprocess
import sys
import os


def layout_bpmn_with_bpmnjs(input_bpmn, output_bpmn, node_script='bpmn_layout.js'):
    """
    Call Node.js script to layout BPMN and generate DI info using bpmn-js.
    """
    subprocess.run(['node', node_script, input_bpmn, output_bpmn], check=True)


def main():
    if len(sys.argv) < 3:
        print("Usage: python bpmn_diagram.py <input.bpmn> <output_with_di.bpmn>")
        sys.exit(1)
    input_bpmn = sys.argv[1]
    output_bpmn = sys.argv[2]
    layout_bpmn_with_bpmnjs(input_bpmn, output_bpmn)
    print(f"BPMN layout with DI generated: {output_bpmn}")


if __name__ == '__main__':
    main()
