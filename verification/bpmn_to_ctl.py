from py4pm.bpmn.bpmn_importer import BpmnImporter
from py4pm.bpmn.bpmn_to_petri_net_converter import BpmnToPetriNetConverter
from py4pm.visualization.visualize_petri_net import visualize_petri_net


def convert_bpmn_to_petri_net(bpmn_file_path: str):
    bpmn_model = BpmnImporter().apply(bpmn_file_path)

    petri_net = BpmnToPetriNetConverter().apply(bpmn_model)

    print("\nPlaces:")
    for place in petri_net.places:
        print(f" - {place.name}")

    print("\nTransitions:")
    for transition in petri_net.transitions:
        print(f" - {transition.name}")

    print("\nArcs:")
    for arc in petri_net.arcs:
        print(f" - {arc.source.name} -> {arc.target.name}")

    visualize_petri_net(petri_net)


if __name__ == "__main__":
    convert_bpmn_to_petri_net("example.bpmn")
