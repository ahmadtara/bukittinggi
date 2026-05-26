import streamlit as st
import zipfile
import tempfile
import os
from lxml import etree

st.set_page_config(
    page_title="KML Polygon Description Editor",
    layout="wide"
)

st.title("KML / KMZ Polygon Description Editor")

st.write(
    "Upload file KML atau KMZ lalu semua description polygon akan otomatis disamakan dengan nama judul utama."
)

uploaded_file = st.file_uploader(
    "Upload KML / KMZ",
    type=["kml", "kmz"]
)

def process_kml(kml_path):

    parser = etree.XMLParser(remove_blank_text=True)

    tree = etree.parse(
        kml_path,
        parser
    )

    root = tree.getroot()

    ns = {
        'kml': 'http://www.opengis.net/kml/2.2'
    }

    # =====================================
    # AMBIL NAMA JUDUL UTAMA
    # =====================================

    title_name = None

    folders = root.xpath(
        '//kml:Folder/kml:name',
        namespaces=ns
    )

    if folders:

        title_name = folders[0].text.strip()

    else:

        docs = root.xpath(
            '//kml:Document/kml:name',
            namespaces=ns
        )

        if docs:

            title_name = docs[0].text.strip()

    if not title_name:

        title_name = 'DEFAULT DESCRIPTION'

    # =====================================
    # CARI POLYGON
    # =====================================

    placemarks = root.xpath(
        '//kml:Placemark',
        namespaces=ns
    )

    total = 0

    for placemark in placemarks:

        polygon = placemark.find(
            'kml:Polygon',
            namespaces=ns
        )

        if polygon is not None:

            description = placemark.find(
                'kml:description',
                namespaces=ns
            )

            if description is None:

                description = etree.SubElement(
                    placemark,
                    '{http://www.opengis.net/kml/2.2}description'
                )

            description.text = title_name

            total += 1

    return tree, title_name, total


if uploaded_file:

    with tempfile.TemporaryDirectory() as tmpdir:

        input_path = os.path.join(
            tmpdir,
            uploaded_file.name
        )

        with open(input_path, 'wb') as f:

            f.write(uploaded_file.read())

        # =====================================
        # KMZ
        # =====================================

        if uploaded_file.name.lower().endswith('.kmz'):

            extract_dir = os.path.join(
                tmpdir,
                'extract'
            )

            os.makedirs(
                extract_dir,
                exist_ok=True
            )

            with zipfile.ZipFile(
                input_path,
                'r'
            ) as zip_ref:

                zip_ref.extractall(extract_dir)

            kml_file = None

            for root_dir, dirs, files in os.walk(extract_dir):

                for file in files:

                    if file.lower().endswith('.kml'):

                        kml_file = os.path.join(
                            root_dir,
                            file
                        )

                        break

            if not kml_file:

                st.error(
                    'KML tidak ditemukan di dalam KMZ'
                )

                st.stop()

            tree, title_name, total = process_kml(kml_file)

            tree.write(
                kml_file,
                pretty_print=True,
                xml_declaration=True,
                encoding='UTF-8'
            )

            output_kmz = os.path.join(
                tmpdir,
                'edited.kmz'
            )

            with zipfile.ZipFile(
                output_kmz,
                'w',
                zipfile.ZIP_DEFLATED
            ) as zip_out:

                for root_dir, dirs, files in os.walk(extract_dir):

                    for file in files:

                        full_path = os.path.join(
                            root_dir,
                            file
                        )

                        arcname = os.path.relpath(
                            full_path,
                            extract_dir
                        )

                        zip_out.write(
                            full_path,
                            arcname
                        )

            st.success(
                f'{total} polygon berhasil diubah'
            )

            st.write(
                f'Description baru: {title_name}'
            )

            with open(output_kmz, 'rb') as f:

                st.download_button(
                    label='Download KMZ Hasil',
                    data=f,
                    file_name='edited.kmz',
                    mime='application/vnd.google-earth.kmz'
                )

        # =====================================
        # KML
        # =====================================

        else:

            tree, title_name, total = process_kml(input_path)

            output_kml = os.path.join(
                tmpdir,
                'edited.kml'
            )

            tree.write(
                output_kml,
                pretty_print=True,
                xml_declaration=True,
                encoding='UTF-8'
            )

            st.success(
                f'{total} polygon berhasil diubah'
            )

            st.write(
                f'Description baru: {title_name}'
            )

            with open(output_kml, 'rb') as f:

                st.download_button(
                    label='Download KML Hasil',
                    data=f,
                    file_name='edited.kml',
                    mime='application/vnd.google-earth.kml+xml'
                )
