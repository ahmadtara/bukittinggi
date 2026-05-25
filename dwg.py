import streamlit as st
import tempfile
import zipfile
import os
import xml.etree.ElementTree as ET
import geopandas as gpd

st.set_page_config(
    page_title="QGIS Project to KML",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ QGIS Project to KML Converter")

st.write("""
Upload ZIP yang berisi project QGIS atau data GIS.

Didukung:

- QGS
- SHP
- GPKG
- GeoJSON
- KML
- KMZ
""")

SUPPORTED_GIS = (
    ".shp",
    ".gpkg",
    ".geojson",
    ".json",
    ".kml",
    ".kmz"
)


def read_qgs_datasources(qgs_file):

    result = []

    try:

        tree = ET.parse(qgs_file)
        root = tree.getroot()

        for datasource in root.iter("datasource"):

            if datasource.text:

                result.append(
                    datasource.text.strip()
                )

    except Exception as e:

        st.error(
            f"Gagal membaca QGS: {e}"
        )

    return result


def find_gis_files(folder):

    files_found = []

    for root, dirs, files in os.walk(folder):

        for file in files:

            full = os.path.join(root, file)

            if file.lower().endswith(
                SUPPORTED_GIS
            ):
                files_found.append(full)

    return files_found


uploaded = st.file_uploader(
    "Upload ZIP",
    type=["zip"]
)

if uploaded:

    with tempfile.TemporaryDirectory() as tempdir:

        zip_path = os.path.join(
            tempdir,
            uploaded.name
        )

        with open(zip_path, "wb") as f:

            f.write(
                uploaded.getbuffer()
            )

        extract_dir = os.path.join(
            tempdir,
            "extract"
        )

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as z:

            z.extractall(
                extract_dir
            )

        qgs_files = []

        for root, dirs, files in os.walk(
            extract_dir
        ):

            for file in files:

                if file.lower().endswith(
                    ".qgs"
                ):

                    qgs_files.append(
                        os.path.join(
                            root,
                            file
                        )
                    )

        if qgs_files:

            st.success(
                f"QGS ditemukan ({len(qgs_files)})"
            )

            for qgs in qgs_files:

                with st.expander(
                    f"Project: {os.path.basename(qgs)}"
                ):

                    datasources = read_qgs_datasources(
                        qgs
                    )

                    if datasources:

                        st.write(
                            "Datasource yang ditemukan:"
                        )

                        for ds in datasources:

                            st.code(ds)

                    else:

                        st.warning(
                            "Tidak ada datasource."
                        )

        gis_files = find_gis_files(
            extract_dir
        )

        st.subheader(
            "File GIS Ditemukan"
        )

        if not gis_files:

            st.error(
                """
Tidak ditemukan file GIS.

Biasanya file ZIP Anda hanya berisi:

- .qgs
- database style

Sedangkan data asli (.shp/.gpkg/.kmz)
belum ikut diupload.
"""
            )

            st.stop()

        for file in gis_files:

            st.write(
                os.path.basename(file)
            )

        selected = st.selectbox(
            "Pilih Layer",
            gis_files,
            format_func=lambda x:
            os.path.basename(x)
        )

        if st.button(
            "Convert ke KML"
        ):

            try:

                st.info(
                    "Membaca layer..."
                )

                gdf = gpd.read_file(
                    selected
                )

                st.success(
                    f"{len(gdf)} fitur ditemukan"
                )

                st.write(
                    "Preview Data:"
                )

                st.dataframe(
                    gdf.drop(
                        columns="geometry",
                        errors="ignore"
                    ).head(20)
                )

                output_kml = os.path.join(
                    tempdir,
                    "hasil.kml"
                )

                gdf.to_file(
                    output_kml,
                    driver="KML"
                )

                with open(
                    output_kml,
                    "rb"
                ) as f:

                    st.download_button(
                        label="⬇ Download KML",
                        data=f,
                        file_name="hasil.kml",
                        mime="application/vnd.google-earth.kml+xml"
                    )

                st.success(
                    "Konversi selesai."
                )

            except Exception as e:

                st.error(
                    f"Gagal convert: {e}"
                )
