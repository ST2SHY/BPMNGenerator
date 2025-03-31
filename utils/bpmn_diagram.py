from bpmn_diagram_layout.layout import layout_bpmn_diagram

MODELNAME = ''

with open(MODELNAME, "r") as f:
    bpmn_xml = f.read()

bpmn_with_di = layout_bpmn_diagram(bpmn_xml)

with open(MODELNAME, "w") as f:
    f.write(bpmn_with_di)
