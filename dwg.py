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
    # FOLDER YANG DIABAIKAN
    # =====================================

    ignore_keywords = [

        'BOUNDARY',
        'BOUNDARY FAT',
        'BOUNDARY CLUSTER',
        'FAT COVERAGE',
        'COVER LINE'

    ]

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
        # CARI PARENT VALID
        # =====================================

        parent = placemark.getparent()

        valid_titles = []

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
                # SKIP FOLDER TIDAK VALID
                # =====================================

                skip = False

                for keyword in ignore_keywords:

                    if keyword in upper_name:

                        skip = True
                        break

                if not skip:

                    clean_name = (
                        parent_name
                        .replace('.kmz', '')
                        .replace('.KMZ', '')
                        .strip()
                    )

                    valid_titles.append(
                        clean_name
                    )

            parent = parent.getparent()

        # =====================================
        # AMBIL PARENT PALING ATAS
        # =====================================

        if not valid_titles:
            continue

        title_name = valid_titles[-1]

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
