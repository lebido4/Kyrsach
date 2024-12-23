import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask import Response
import xml.etree.ElementTree as ET


app = Flask(__name__)
CORS(app)

# PostgreSQL connection details
DB_NAME = "vm_management"
DB_USER = "admin"
DB_PASSWORD = "secret"
DB_HOST = "postgres"
DB_PORT = "5432"

def get_db_connection():
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return connection



@app.route('/vm/<int:vm_id>/download', methods=['GET'])
def download_vm_config(vm_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Получаем информацию о виртуальной машине
    cursor.execute("SELECT id, name, cpu, ram, disk FROM virtual_machines WHERE id = %s", (vm_id,))
    vm = cursor.fetchone()
    connection.close()

    if not vm:
        return jsonify({'message': 'VM not found'}), 404

    # Формируем XML-конфигурацию для libvirt
    root = ET.Element("domain", type="kvm")
    name = ET.SubElement(root, "name")
    name.text = vm[1]

    memory = ET.SubElement(root, "memory", unit="KiB")
    memory.text = str(vm[3] * 1024 * 1024)  # RAM в килобайтах

    vcpu = ET.SubElement(root, "vcpu")
    vcpu.text = str(vm[2])  # Количество CPU

    os = ET.SubElement(root, "os")
    type_ = ET.SubElement(os, "type", arch="x86_64", machine="pc-i440fx-6.2")
    type_.text = "hvm"

    devices = ET.SubElement(root, "devices")
    disk = ET.SubElement(devices, "disk", type="file", device="disk")
    driver = ET.SubElement(disk, "driver", name="qemu", type="qcow2")
    source = ET.SubElement(disk, "source", file=f"/var/lib/libvirt/images/{vm[1]}.qcow2")
    target = ET.SubElement(disk, "target", dev="vda", bus="virtio")

    # Генерация XML
    xml_config = ET.tostring(root, encoding='unicode', method='xml')

    # Возвращаем файл XML пользователю
    response = Response(xml_config, content_type='application/xml')
    response.headers['Content-Disposition'] = f'attachment; filename={vm[1]}_config.xml'
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
