import streamlit as st
import zipfile
import tempfile
import os
from lxml import etree

# =====================================
# STREAMLIT CONFIG
# =====================================

st.set_page_config(
    page_title="KMZ Polygon Description Editor",
    layout="wide"
)

st.title("KMZ / KML Polygon Description Editor")

st.write(
    """
    Upload file KMZ / KML lalu semua description polygon
    otomatis mengikuti parent teratas:
    
    - PKB
    - ABD
    - CL
    - .kmz
    """
)

# =====================================
# UPLOAD
# =====================================

uploaded_file = st.file_uploader(
    "Upload KMZ / KML",
    type=["kmz", "kml"]
)

# =====================================
# PROCESS KML
# =====================================

def process_kml(kml_path):

    parser = etree.XMLParser(
        remove_blank_text=True
    )

    tree = etree.parse(
        kml_path,
        parser
    )

    root = tree.getroot()

    ns = {
        'kml': 'http://www.opengis.net/kml/2.2'
    }

    total = 0

    # =====================================
    # SEMUA PLACEMARK
    # =====================================

    placemarks = root.xpath(
        '//kml:Placemark',
        namespaces=ns
    )

    for placemark in placemarks:

        polygon = placemark.find(
            './/kml:Polygon',
            namespaces=ns
        )

        # =====================================
        # HANYA POLYGON
        # =====================================

        if polygon is None:
            continue

        # =====================================
        # CARI PARENT TERATAS
        # =====================================

        parent = placemark.getparent()

        matched_titles = []

        while parent is not None:

            name_elem = parent.find(
                'kml:name',
                namespaces=ns
            )

            if (
                name_elem is not None
                and name_elem.text
            ):

                parent_name = (
                    name_elem.text.strip()
                )

                upper_name = parent_name.upper()

                # =====================================
                # KEYWORD VALID
                # =====================================

                if (

                    'PKB' in upper_name
                    or 'ABD' in upper_name
                    or 'CL' in upper_name
                    or '.KMZ' in upper_name

                ):

                    clean_name = (
                        parent_name
                        .replace('.kmz', '')
                        .replace('.KMZ', '')
                        .strip()
                    )

                    matched_titles.append(
                        clean_name
                    )

            parent = parent.getparent()

        # =====================================
        # AMBIL PARENT PALING ATAS
        # =====================================

        if not matched_titles:
            continue

        title_name = matched_titles[-1]

        # =====================================
        # DESCRIPTION
        # =====================================

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

    return tree, total

# =====================================
# PROCESS FILE
# =====================================

if uploaded_file:

    with tempfile.TemporaryDirectory() as tmpdir:

        input_path = os.path.join(
            tmpdir,
            uploaded_file.name
        )

        # SAVE FILE
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

            # EXTRACT
            with zipfile.ZipFile(
                input_path,
                'r'
            ) as zip_ref:

                zip_ref.extractall(
                    extract_dir
                )

            # CARI KML
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
                    "KML tidak ditemukan di dalam KMZ"
                )

                st.stop()

            # PROCESS
            tree, total = process_kml(kml_file)

            # SAVE
            tree.write(
                kml_file,
                pretty_print=True,
                xml_declaration=True,
                encoding='UTF-8'
            )

            # REPACK KMZ
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
                f"{total} polygon berhasil diubah"
            )

            # DOWNLOAD
            with open(output_kmz, 'rb') as f:

                st.download_button(
                    label="Download KMZ Hasil",
                    data=f,
                    file_name="edited.kmz",
                    mime="application/vnd.google-earth.kmz"
                )

        # =====================================
        # KML
        # =====================================

        else:

            tree, total = process_kml(input_path)

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
                f"{total} polygon berhasil diubah"
            )

            with open(output_kml, 'rb') as f:

                st.download_button(
                    label="Download KML Hasil",
                    data=f,
                    file_name="edited.kml",
                    mime="application/vnd.google-earth.kml+xml"
                )
