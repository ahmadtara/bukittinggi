import streamlit as st
                encoding='UTF-8'
            )

            # REPACK KMZ
            output_kmz = os.path.join(
                tmpdir,
                'edited.kmz'
            )

            with zipfile.ZipFile(output_kmz, 'w', zipfile.ZIP_DEFLATED) as zip_out:

                for root_dir, dirs, files in os.walk(extract_dir):
                    for file in files:

                        full_path = os.path.join(root_dir, file)

                        arcname = os.path.relpath(
                            full_path,
                            extract_dir
                        )

                        zip_out.write(full_path, arcname)

            st.success(f'{total} polygon berhasil diubah')

            st.write(f'Description baru: {title_name}')

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

            st.success(f'{total} polygon berhasil diubah')

            st.write(f'Description baru: {title_name}')

            with open(output_kml, 'rb') as f:

                st.download_button(
                    label='Download KML Hasil',
                    data=f,
                    file_name='edited.kml',
                    mime='application/vnd.google-earth.kml+xml'
                )
