import xml.etree.ElementTree as ET
import glob

output_root = ET.Element("alien")
output_collection = ET.SubElement(output_root, "collection")

event_counter = 1  # starting event number

for file in glob.glob("*.xml"):
    tree = ET.parse(file)
    root = tree.getroot()

    collection = root.find("collection")
    if collection is None:
        continue

    for event in collection.findall("event"):
        # Make a deep copy so we don't move nodes between trees
        new_event = ET.fromstring(ET.tostring(event))

        # Renumber the event
        new_event.set("name", str(event_counter))
        event_counter += 1

        output_collection.append(new_event)

tree = ET.ElementTree(output_root)
tree.write("merged.xml", encoding="utf-8", xml_declaration=True)
