"""
BPMN to Petri Net Converter

This module provides functionality to convert BPMN diagrams to Petri nets,
supporting both single process and multi-lane collaboration diagrams.
"""

from typing import Dict, List, Tuple, Set, Any
import xml.etree.ElementTree as ET
import json

example = ''


class MultiLaneBpmnToPetriNetConverter:
    """
    Multi-lane BPMN to Petri Net Converter

    Supports multi-lane collaboration diagrams and message flow conversion
    """

    def __init__(self):
        self.lanes = {}  # Lane information
        self.message_flows = []  # Message flows
        self.petri_nets = {}  # Petri nets for each lane
        self.merged_petri_net = None  # Merged Petri net

    def parse_bpmn_collaboration(self, bpmn_file_path: str) -> Dict[str, Any]:
        """
        Parse BPMN collaboration diagram, extract lane and message flow information

        Args:
            bpmn_file_path: BPMN file path

        Returns:
            Dictionary containing lane and message flow information
        """
        tree = ET.parse(bpmn_file_path)
        root = tree.getroot()

        # Define BPMN namespace
        bpmn_ns = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}

        collaboration_info = {
            'lanes': {},
            'message_flows': [],
            'processes': {}
        }

        # Find collaboration element
        collaboration = root.find('.//bpmn:collaboration', bpmn_ns)
        if collaboration is not None:
            # Parse lanes
            for participant in collaboration.findall('.//bpmn:participant', bpmn_ns):
                participant_id = participant.get('id')
                participant_name = participant.get('name', participant_id)
                process_ref = participant.get('processRef')

                collaboration_info['lanes'][participant_id] = {
                    'name': participant_name,
                    'process_ref': process_ref,
                    'tasks': [],
                    'start_events': [],
                    'end_events': [],
                    'gateways': []
                }

            # Parse message flows
            for message_flow in collaboration.findall('.//bpmn:messageFlow', bpmn_ns):
                source_ref = message_flow.get('sourceRef')
                target_ref = message_flow.get('targetRef')

                collaboration_info['message_flows'].append({
                    'source': source_ref,
                    'target': target_ref,
                    'id': message_flow.get('id', f"mf_{source_ref}_{target_ref}")
                })

        # Parse processes
        for process in root.findall('.//bpmn:process', bpmn_ns):
            process_id = process.get('id')
            collaboration_info['processes'][process_id] = {
                'tasks': [],
                'start_events': [],
                'end_events': [],
                'gateways': [],
                'sequence_flows': []
            }

            # Parse tasks
            for task in process.findall('.//bpmn:task', bpmn_ns):
                collaboration_info['processes'][process_id]['tasks'].append({
                    'id': task.get('id'),
                    'name': task.get('name', task.get('id')),
                    'type': 'task'
                })

            # Parse start events
            for start_event in process.findall('.//bpmn:startEvent', bpmn_ns):
                collaboration_info['processes'][process_id]['start_events'].append({
                    'id': start_event.get('id'),
                    'name': start_event.get('name', start_event.get('id')),
                    'type': 'startEvent'
                })

            # Parse end events
            for end_event in process.findall('.//bpmn:endEvent', bpmn_ns):
                collaboration_info['processes'][process_id]['end_events'].append({
                    'id': end_event.get('id'),
                    'name': end_event.get('name', end_event.get('id')),
                    'type': 'endEvent'
                })

            # Parse gateways
            for gateway in process.findall('.//bpmn:*', bpmn_ns):
                if 'Gateway' in gateway.tag:
                    collaboration_info['processes'][process_id]['gateways'].append({
                        'id': gateway.get('id'),
                        'name': gateway.get('name', gateway.get('id')),
                        'type': gateway.tag.split('}')[-1]
                    })

            # Parse sequence flows
            for seq_flow in process.findall('.//bpmn:sequenceFlow', bpmn_ns):
                collaboration_info['processes'][process_id]['sequence_flows'].append({
                    'id': seq_flow.get('id'),
                    'source': seq_flow.get('sourceRef'),
                    'target': seq_flow.get('targetRef')
                })

        return collaboration_info

    def convert_lane_to_petri_net(self, lane_info: Dict[str, Any], process_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert single lane to Petri net

        Args:
            lane_info: Lane information
            process_info: Corresponding process information

        Returns:
            Petri net representation of the lane
        """
        petri_net = {
            'places': [],
            'transitions': [],
            'arcs': [],
            'initial_marking': {},
            'final_markings': []
        }

        # Add start and end places
        start_place = f"p_start_{lane_info['name']}"
        end_place = f"p_end_{lane_info['name']}"

        petri_net['places'].extend([start_place, end_place])
        petri_net['initial_marking'][start_place] = 1

        # Create transitions and places for each task
        for task in process_info['tasks']:
            task_id = task['id']
            pre_place = f"p_pre_{task_id}"
            post_place = f"p_post_{task_id}"
            transition = f"t_{task_id}"

            petri_net['places'].extend([pre_place, post_place])
            petri_net['transitions'].append(transition)
            petri_net['arcs'].extend([
                {'source': pre_place, 'target': transition},
                {'source': transition, 'target': post_place}
            ])

        # Create transitions and places for each gateway
        for gateway in process_info['gateways']:
            gateway_id = gateway['id']
            gateway_type = gateway['type']

            if 'Exclusive' in gateway_type or 'Inclusive' in gateway_type:
                # Exclusive or inclusive gateway
                pre_place = f"p_pre_{gateway_id}"
                post_place = f"p_post_{gateway_id}"
                transition = f"t_{gateway_id}"

                petri_net['places'].extend([pre_place, post_place])
                petri_net['transitions'].append(transition)
                petri_net['arcs'].extend([
                    {'source': pre_place, 'target': transition},
                    {'source': transition, 'target': post_place}
                ])
            elif 'Parallel' in gateway_type:
                # Parallel gateway
                pre_place = f"p_pre_{gateway_id}"
                post_place = f"p_post_{gateway_id}"
                transition = f"t_{gateway_id}"

                petri_net['places'].extend([pre_place, post_place])
                petri_net['transitions'].append(transition)
                petri_net['arcs'].extend([
                    {'source': pre_place, 'target': transition},
                    {'source': transition, 'target': post_place}
                ])

        # Connect places according to sequence flows
        for seq_flow in process_info['sequence_flows']:
            source = seq_flow['source']
            target = seq_flow['target']

            # Find corresponding places for source and target
            source_place = None
            target_place = None

            # Check if it's a start event
            if any(start['id'] == source for start in process_info['start_events']):
                source_place = start_place
            else:
                source_place = f"p_post_{source}"

            # Check if it's an end event
            if any(end['id'] == target for end in process_info['end_events']):
                target_place = end_place
            else:
                target_place = f"p_pre_{target}"

            # Add connection arc
            if source_place in petri_net['places'] and target_place in petri_net['places']:
                petri_net['arcs'].append({
                    'source': source_place,
                    'target': target_place
                })

        return petri_net

    def merge_petri_nets_with_message_flows(self, lane_petri_nets: Dict[str, Dict],
                                            message_flows: List[Dict]) -> Dict[str, Any]:
        """
        Merge multiple Petri nets and handle message flows

        Args:
            lane_petri_nets: Petri nets for each lane
            message_flows: List of message flows

        Returns:
            Merged Petri net
        """
        merged_net = {
            'places': [],
            'transitions': [],
            'arcs': [],
            'initial_marking': {},
            'final_markings': []
        }

        # Merge Petri nets from all lanes
        for lane_id, petri_net in lane_petri_nets.items():
            merged_net['places'].extend(petri_net['places'])
            merged_net['transitions'].extend(petri_net['transitions'])
            merged_net['arcs'].extend(petri_net['arcs'])
            merged_net['initial_marking'].update(petri_net['initial_marking'])

        # Handle message flows
        for msg_flow in message_flows:
            source = msg_flow['source']
            target = msg_flow['target']

            # Create message place for each message flow
            message_place = f"p_msg_{msg_flow['id']}"
            merged_net['places'].append(message_place)

            # Connect source transition to message place
            source_transition = f"t_{source}"
            if source_transition in merged_net['transitions']:
                merged_net['arcs'].append({
                    'source': source_transition,
                    'target': message_place
                })

            # Connect message place to target transition
            target_transition = f"t_{target}"
            if target_transition in merged_net['transitions']:
                merged_net['arcs'].append({
                    'source': message_place,
                    'target': target_transition
                })

        return merged_net

    def convert_collaboration_bpmn_to_petri_net(self, bpmn_file_path: str) -> Dict[str, Any]:
        """
        Convert collaboration BPMN to Petri net

        Args:
            bpmn_file_path: BPMN file path

        Returns:
            Merged Petri net
        """
        # Parse BPMN collaboration
        collaboration_info = self.parse_bpmn_collaboration(bpmn_file_path)

        # Create Petri net for each lane
        lane_petri_nets = {}
        for lane_id, lane_info in collaboration_info['lanes'].items():
            process_ref = lane_info['process_ref']
            if process_ref in collaboration_info['processes']:
                process_info = collaboration_info['processes'][process_ref]
                petri_net = self.convert_lane_to_petri_net(
                    lane_info, process_info)
                lane_petri_nets[lane_id] = petri_net

        # Merge Petri nets and handle message flows
        merged_petri_net = self.merge_petri_nets_with_message_flows(
            lane_petri_nets,
            collaboration_info['message_flows']
        )

        return merged_petri_net


def convert_bpmn_to_petri_net(bpmn_file_path: str):
    """
    Convert BPMN to Petri net (supports single process and multi-lane collaboration)

    Args:
        bpmn_file_path: BPMN file path
    """
    # Check if it's a collaboration diagram
    tree = ET.parse(bpmn_file_path)
    root = tree.getroot()
    bpmn_ns = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}

    collaboration = root.find('.//bpmn:collaboration', bpmn_ns)

    if collaboration is not None:
        # Multi-lane collaboration diagram
        print("Collaboration diagram detected, using multi-lane conversion algorithm...")
        converter = MultiLaneBpmnToPetriNetConverter()
        petri_net = converter.convert_collaboration_bpmn_to_petri_net(
            bpmn_file_path)

        print("Conversion completed!")
        print(f"Number of places: {len(petri_net['places'])}")
        print(f"Number of transitions: {len(petri_net['transitions'])}")
        print(f"Number of arcs: {len(petri_net['arcs'])}")
        print(f"Initial marking: {petri_net['initial_marking']}")

        # Save results
        output_file = bpmn_file_path.replace('.bpmn', '_petri_net.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(petri_net, f, ensure_ascii=False, indent=2)
        print(f"Petri net saved to: {output_file}")

    else:
        # Single process BPMN
        print("Single process BPMN detected, using simplified conversion...")
        # Implement simplified single process conversion logic
        converter = MultiLaneBpmnToPetriNetConverter()
        # Treat single process as collaboration with one lane
        petri_net = converter.convert_collaboration_bpmn_to_petri_net(
            bpmn_file_path)

        print("Conversion completed!")
        print(f"Number of places: {len(petri_net['places'])}")
        print(f"Number of transitions: {len(petri_net['transitions'])}")
        print(f"Number of arcs: {len(petri_net['arcs'])}")
        print(f"Initial marking: {petri_net['initial_marking']}")

        # Save results
        output_file = bpmn_file_path.replace('.bpmn', '_petri_net.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(petri_net, f, ensure_ascii=False, indent=2)
        print(f"Petri net saved to: {output_file}")


if __name__ == "__main__":
    convert_bpmn_to_petri_net(example)
