import json
import xml.etree.ElementTree as ET


class NmapXmlInfo:
    def __init__(self, xml: str, path: bool = False) -> None:
        '''
        Парсинга `XML` отчетов утилиты `nmap`
        `xml`: строковые данные формата `XML` ИЛИ путь до `XML` файла
        `path`: флаг, если истина, то аргумент `xml` воспринимается как путь до `XML` файла
        '''
        if path:
            self.xml_root = ET.parse(xml)
        else:
            self.xml_root = ET.fromstring(xml)
        self.info = self.parse_xml(self.xml_root)

    def parse_xml(self, xml_root: ET) -> dict:
        '''
        Метод парсинга `XML`
        `xml_root`: дерево элементов `XML` файла
        '''
        results = []
        time = int(xml_root.find('runstats').find('finished').get('time'))
        for host in xml_root.findall('host'):
            info = {
                'ip': host.find('address').get('addr'),
                'time_scan': time,
                'hostnames': self.__parse_hostnames(host),
                'ports': self.__parse_ports(host),
                'os_info': self.__parse_os(host)
            }
            results.append(info)
        return results

    def __parse_os(self, host: ET.Element) -> dict:
        '''
        Метод парсинга данных об OS
        `host`: элемент `host` из дерева
        '''
        result = {}
        for os in host.find('os').findall('osmatch'):
            for osc in os.findall('osclass'):
                result.update({
                    os.get('name'): {
                        'type': osc.get('type'),
                        'vendor': osc.get('vendor'),
                        'osfamily': osc.get('osfamily'),
                        'osgen': osc.get('osgen')
                    }
                })
        return result

    def __parse_hostnames(self, host: ET.Element) -> list:
        '''
        Метод парсинга данных о доменах
        `host`: элемент `host` из дерева
        '''
        result = []
        for hostname in host.find('hostnames').findall('hostname'):
            result.append(
                {
                    'name': hostname.get('name'),
                    'type': hostname.get('type')
                }
            )
        return result

    def __parse_ports(self, host: ET.Element) -> dict:
        '''
        Метод парсинга данных о портах
        `host`: элемент `host` из дерева
        '''
        result = {}
        for port in host.findall('ports')[0].findall('port'):
            result.update({
                port.get('portid'): {
                    'state': port.find('state').get('state'),
                    'protocol': port.get('protocol'),
                    'service': port.find('service').get('name'),
                    'version': port.find('service').get('version')
                }
            })
        return result


if __name__ == '__main__':
    example = NmapXmlInfo('scan.xml', True)
    print(json.dumps(example.info, indent=4))
