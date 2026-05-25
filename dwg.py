import streamlit as st
import tempfile
import zipfile
import os
import geopandas as gpd

st.set_page_config(
    page_title="GIS to KML Converter",
    layout="wide"
)

st.title("🗺️ GIS to KML Converter")

st.write("""
Upload ZIP yang berisi:
- Shapefile (.shp + .dbf + .shx + .prj)
- GeoPackage (.gpkg)
- GeoJSON (.geojson)
- KML
- KMZ
""")

uploaded = st.file_uploader(
    "Upload ZIP",
    type=["zip"]
)

SUPPORTED = (
    ".shp",
    ".gpkg",
    ".geojson",
    ".json",
    ".kml",
    ".kmz"
)

if uploaded:

    with tempfile.TemporaryDirectory() as tempdir:

        zip_path = os.path.join(tempdir, uploaded.name)

        with open(zip_path, "wb") as f:
            f.write(uploaded.getbuffer())

        extract_dir = os.path.join(tempdir, "extract")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        found_files = []

        for root, dirs, files in os.walk(extract_dir):
            for file in files:

                if file.lower().endswith(SUPPORTED):
                    found_files.append(
                        os.path.join(root, file)
                    )

        st.subheader("File GIS Ditemukan")

        if not found_files:
            st.error("Tidak ditemukan file GIS yang didukung.")
            st.stop()

        for f in found_files:
            st.write(f)

        selected = st.selectbox(
            "Pilih Layer",
            found_files
        )

        if st.button("Convert ke KML"):

            try:

                st.info("Membaca data...")

                gdf = gpd.read_file(selected)

                st.success(
                    f"Berhasil membaca {len(gdf)} fitur"
                )

                output_kml = os.path.join(
                    tempdir,
                    "hasil.kml"
                )

                gdf.to_file(
                    output_kml,
                    driver="KML"
                )

                with open(output_kml, "rb") as f:

                    st.download_button(
                        label="⬇ Download KML",
                        data=f,
                        file_name="hasil.kml",
                        mime="application/vnd.google-earth.kml+xml"
                    )

            except Exception as e:

                st.error(str(e))
