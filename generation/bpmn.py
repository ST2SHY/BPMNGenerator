# Generate BPMN
#!/usr/bin/env python3
# filename: generate_bpmn_from_lists.py
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import defaultdict

outputbpmn = ''


def prettify_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def generate_bpmn(pool, timer, task, gateway, flow, message_flow):
    ns = {
        'bpmn': "http://www.omg.org/spec/BPMN/20100524/MODEL",
        'bpmndi': "http://www.omg.org/spec/BPMN/20100524/DI",
        'omgdc': "http://www.omg.org/spec/DD/20100524/DC",
        'omgdi': "http://www.omg.org/spec/DD/20100524/DI"
    }
    ET.register_namespace('', ns['bpmn'])

    definitions = ET.Element('definitions', {
        'xmlns': ns['bpmn'],
        'xmlns:bpmndi': ns['bpmndi'],
        'xmlns:omgdc': ns['omgdc'],
        'xmlns:omgdi': ns['omgdi'],
        'id': 'Definitions_1',
        'targetNamespace': 'http://example.com/bpmn'
    })

    collaboration = ET.SubElement(definitions, 'collaboration', {
                                  'id': 'Collaboration_1'})

    pool_process_map = {}
    for actor_id in pool:
        process_id = f"Process_{actor_id}"
        pool_process_map[actor_id] = process_id
        ET.SubElement(collaboration, 'participant', {
            'id': f"Participant_{actor_id}",
            'processRef': process_id
        })

    processes = {pid: ET.SubElement(definitions, 'process', {'id': pid, 'isExecutable': 'true'})
                 for pid in pool_process_map.values()}

    for t in task:
        ET.SubElement(processes[pool_process_map[t['pool']]], 'task', {
            'id': t['id'],
            'name': t['name']
        })

    for g in gateway:
        ET.SubElement(processes[pool_process_map[g.get('pool', pool[0])]], f"{g['type']}Gateway", {
            'id': g['id'],
            'name': g['name']
        })

    for ti in timer:
        attached_to = ti['attached_to']
        event = ET.SubElement(processes[pool_process_map.get(ti.get('pool', pool[0]))], 'intermediateCatchEvent', {
            'id': ti['id']
        })
        timer_def = ET.SubElement(event, 'timerEventDefinition')
        ET.SubElement(timer_def, 'timeDate').text = ti['time_date']

    for f in flow:
        source_id, target_id = f['source'], f['target']
        for proc in processes.values():
            ET.SubElement(proc, 'sequenceFlow', {
                'id': f"Flow_{source_id}_to_{target_id}",
                'sourceRef': source_id,
                'targetRef': target_id
            })

    for m in message_flow:
        ET.SubElement(collaboration, 'messageFlow', {
            'id': f"Message_{m['from_id']}_to_{m['to_id']}",
            'sourceRef': m['from_id'],
            'targetRef': m['to_id']
        })

    return prettify_xml(definitions)


# Example usage (fill in real data before running)
if __name__ == '__main__':
    pool = get_pool()
    timer = get_timer()
    task = get_task()
    gateway = get_gateway()
    flow = get_flow()
    message_flow = get_message_flow()
    xml_str = generate_bpmn(pool, timer, task, gateway, flow, message_flow)
    with open(outputbpmn, 'w') as f:
        f.write(xml_str)
    print("BPMN file generated as output.bpmn")
