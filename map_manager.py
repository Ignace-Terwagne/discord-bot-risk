import xml.etree.ElementTree as ET
import uuid
import random
ns0_namespace = "http://www.w3.org/2000/svg"
class MapManager():
    def __init(self):
        pass
    def create_map(self):
        tree = ET.parse("map.svg")
        map_id = uuid.uuid4()
        tree.write(f"maps/map-{map_id}.svg")
        return map_id
    def update_country(self, map_id, country, color_code):
        filename = f'maps/map-{map_id}.svg'
        tree = ET.parse(filename)
        root = tree.getroot()
        target_country = root.find(".//"+"{http://www.w3.org/2000/svg}"+f"path[@id='{country}']")
        if target_country is not None:
            print(target_country.get("id"))
            target_country.set("style", f'opacity:1;fill:{color_code};fill-opacity:1;fill-rule:evenodd;stroke:#000000;stroke-width:1.20000005;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4.32165003;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:0.58527132;display:inline;filter:url(#filter13015)')
            tree.write(filename)
            return True
        return None
    def list_countries(self):
        filename = f'map.svg'
        tree = ET.parse(filename)
        root = tree.getroot()
        countries = root.find(".//"+"{http://www.w3.org/2000/svg}"+f"g[@id='layer4']")
        return  [country.get("id") for country in countries.iter()]
            
    
if __name__ == "__main__":
    mm = MapManager()
    map_id = mm.create_map()
    print(map_id)
    for i in mm.list_countries()[1:]:
        code="#"
        for x in range(6):
            code +=str(random.choice(["F",0,1,2,3,4,5,6,7,8,9]))
        print(code)
        print(mm.update_country(map_id, i, code))
    
    
