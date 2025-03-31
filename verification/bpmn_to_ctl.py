from py4pm.bpmn.bpmn_importer import BpmnImporter
from py4pm.bpmn.bpmn_to_petri_net_converter import BpmnToPetriNetConverter
from py4pm.visualization.visualize_petri_net import visualize_petri_net


def convert_bpmn_to_petri_net(bpmn_file_path: str):
    bpmn_model = BpmnImporter().apply(bpmn_file_path)

    petri_net = BpmnToPetriNetConverter().apply(bpmn_model)

    visualize_petri_net(petri_net)


if __name__ == "__main__":
    convert_bpmn_to_petri_net("example.bpmn")
