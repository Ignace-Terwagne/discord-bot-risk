import xml.etree.ElementTree as ET
import uuid
import random
ns0_namespace = "http://www.w3.org/2000/svg"
class MapManager():
    def __init(self):
        pass
    def create_map(self, game_id : str):
        tree = ET.parse("templates/map_named.svg")
        tree.write(f"maps/map-{game_id}.svg")
        return game_id
    def update_country(self, game_id, country, color_code):
        filename = f'maps/map-{game_id}.svg'
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
        region_list = [country.get("id") for country in countries.iter()]
        region_list.pop(0)
        return region_list

if __name__ == "__main__":
    mm = MapManager()
    game_id = mm.create_map()
    print(game_id)
    for i in mm.list_countries()[1:]:
        code="#"
        for x in range(6):
            code +=str(random.choice(["F",0,1,2,3,4,5,6,7,8,9]))
        print(code)
        print(mm.update_country(game_id, i, code))
    
    
