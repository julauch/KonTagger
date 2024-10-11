import os
import xml.etree.ElementTree as ET
import pandas as pd

# Pfade zu den Ordnern und der CSV-Datei
input_folder = './data'  # Ordner, in dem die ursprünglichen Dateien liegen
output_folder = './data_kon'  # Ordner, in dem die annotierten Dateien gespeichert werden
csv_file_path = 'kontagger_rules.csv'  # Pfad zur CSV-Datei

# Funktion zum Hinzufügen von Annotationsebenen für eine einzelne Datei
def add_annotation_tier_with_adv_kon_for_file(xml_file_path, csv_file_path, output_folder):
    try: #Fehler / Abbrüche aufgrund fehlerhafter Dateien vorbeugen
        # XML-Datei einlesen
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # CSV-Datei mit Mapping-Regeln einlesen
        mapping_df = pd.read_csv(csv_file_path)

        # Neue 'tier'-Element für 'annotation_kon'
        basic_body = root.find('basic-body')
        annotation_kon_tier = ET.Element('tier', {
            'id': 'annotation_kon', 
            'speaker': 'PART_CLEAN', 
            'category': 'annotation_kon', 
            'type': 'a',
            'display-name': 'PART_CLEAN [kon]'
        })
    
        # Neue 'tier'-Element für 'adv_kon'
        adv_kon_tier = ET.Element('tier', {
            'id': 'adv_kon', 
            'speaker': 'PART_CLEAN', 
            'category': 'adv_kon', 
            'type': 'a',
            'display-name': 'PART_CLEAN [adv_kon]'
        })
    
        # Lemma-Tier finden
        lemma_tier = basic_body.find(".//tier[@category='lemma']")

    
        if lemma_tier is None:
            raise ValueError(f"Keine Lemma-Ebene in der Datei {xml_file_path} gefunden.")
        else:
            # Jedes Event im Lemma-Tier durchgehen
            for event in lemma_tier.findall('event'):
                lemma = event.text.strip()
                # Prüfen, ob das Lemma in der Mapping-Tabelle vorhanden ist
                match = mapping_df[mapping_df['lemma'] == lemma]
                if not match.empty:
                    # Wenn ein Match gefunden wurde, das entsprechende Tag aus der CSV hinzufügen
                    annotation_tag = match['tag'].values[0]
                    new_event_kon = ET.Element('event', {
                        'start': event.get('start'),
                        'end': event.get('end')
                    })
                    new_event_kon.text = annotation_tag
                    # Event zum annotation_kon-Tier hinzufügen
                    annotation_kon_tier.append(new_event_kon)
                
                    # Wenn das Tag "ADV" oder "?ADV" im Text des Tags vorkommt, füge das entsprechende Positionstag hinzu
                    if 'ADV' in annotation_tag:  # Prüfen, ob "ADV" Teil des Tags ist
                        position = match['position'].values[0]  # Das entsprechende Positionstag
                        if pd.notna(position):  # Nur hinzufügen, wenn die Position nicht NaN ist
                            new_event_adv_kon = ET.Element('event', {
                                'start': event.get('start'),
                                'end': event.get('end')
                            })
                            new_event_adv_kon.text = position
                            adv_kon_tier.append(new_event_adv_kon)
    
        # Neues Tiers zum 'basic-body' hinzufügen
        basic_body.append(annotation_kon_tier)
        basic_body.append(adv_kon_tier)

        # Den Dateinamen für den Output erstellen mit dem Appendix "_kon"
        base_name = os.path.splitext(os.path.basename(xml_file_path))[0]  # Dateiname ohne Extension
        output_file_path = os.path.join(output_folder, f"{base_name}_kon.exb")

        # Die geänderte XML-Datei speichern
        tree.write(output_file_path)

        print(f"Die Datei wurde erfolgreich gespeichert unter: {output_file_path}")
    except ValueError as ve:
        # bei Fehlen der lemma-Ebene
        print(f"Warnung: {ve}")
    except Exception as e:  
        print(f"Fehler bei der Verarbeitung der Datei {xml_file_path}: {e}")

# Funktion zum Verarbeiten mehrerer Dateien im Ordner "data" und Speichern in "data_kon"
def process_multiple_files(input_folder, output_folder, csv_file_path):
    # Unterordner erstellen, falls er noch nicht existiert
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Alle Dateien im "data"-Ordner durchsuchen
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.exb'):  # Nur XML-Dateien (EXMARaLDA) verarbeiten
            xml_file_path = os.path.join(input_folder, file_name)
            add_annotation_tier_with_adv_kon_for_file(xml_file_path, csv_file_path, output_folder)

# Funktion aufrufen, um mehrere Dateien zu verarbeiten
process_multiple_files(input_folder, output_folder, csv_file_path)
