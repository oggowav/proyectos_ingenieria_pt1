import os
import time
import re
import time
from collections import Counter, defaultdict

project_folder = 'C:/Users/OGGO/Desktop/Ultimo Semestre/Fase1Act1'
folder_path = 'C:/Users/OGGO/Desktop/Ultimo Semestre/Fase1Act1/CS13309_Archivos_HTML/Files'
output_folder = 'C:/Users/OGGO/Desktop/Ultimo Semestre/Fase1Act1/CS13309_Archivos_TEXT'

os.makedirs(output_folder, exist_ok=True)

HASH_TABLE_SIZE = 20000 
EMPTY_SLOT_INDICATOR = "vacio"
EMPTY_POSTING_POSITION = -1

def extract_words(text):
    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\-]+", text)
    return words

def hash_function(key, size):
    """Implementa una versión simple de la función hash DJB2."""
    hash_value = 5381
    for char in key:
        hash_value = ((hash_value << 5) + hash_value) + ord(char)
    return hash_value % size

def process_words(cleaned_text, output_file):
    start_processing = time.time()

    words = extract_words(cleaned_text)
    words = [w.lower() for w in words]
    counter = Counter(words)
    sorted_words = sorted(counter.items())

    with open(output_file, "w", encoding="utf-8") as f:
        for word, count in sorted_words:
            f.write(f"{word} se repite: {count} veces.\n")

    end_processing = time.time()
    processing_time = end_processing - start_processing
    return processing_time

def list_html_files(folder_path, output_folder):
    reading_results = []
    cleanning_results = []
    words_results = []

    try:
        files = os.listdir(folder_path)
        html_files = [f for f in files if f.endswith('.html')]

        for file in html_files:
            path = os.path.join(folder_path, file)

            start_reading = time.time()
            with open(path, 'r', encoding="latin-1") as f:
                content = f.read()
            end_reading = time.time()
            reading_duration = end_reading - start_reading

            start_cleanning = time.time()
            cleaned_text = re.sub(r'<.*?>', '', content)
            
            output_file = os.path.join(output_folder, file.replace(".html", ".txt"))
            with open(output_file, "w", encoding="utf-8") as out:
                out.write(cleaned_text)
            end_cleanning = time.time()
            cleanning_duration = end_cleanning - start_cleanning

            words_file = os.path.join(output_folder, file.replace(".html", "_alphabetic_order_words.txt"))
            words_duration = process_words(cleaned_text, words_file)

            reading_results.append((file, reading_duration))
            cleanning_results.append((file, cleanning_duration))
            words_results.append((file, words_duration))

        return reading_results, cleanning_results, words_results
    
    except Exception as e:
        print(f"Ocurrió un error en list_html_files: {e}")
        return [], [], []


def create_consolidated_words_file(output_folder, project_folder):
    file_durations = []
    all_words = []

    txt_files = [f for f in os.listdir(output_folder) if f.endswith('.txt') and not f.endswith('_alphabetic_order_words.txt')]
    for file in txt_files:
        start_file = time.time()
        path = os.path.join(output_folder, file)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            words = extract_words(text)
            all_words.extend([w.lower() for w in words])
        end_file = time.time()
        duration = end_file - start_file
        file_durations.append((file, duration))

    start_sort = time.time()
    all_words_sorted = sorted(all_words)
    end_sort = time.time()
    sort_duration = end_sort - start_sort

    consolidated_file = os.path.join(project_folder, "consolidado_palabras.txt")
    with open(consolidated_file, "w", encoding="utf-8") as f:
        for word in all_words_sorted:
            f.write(f"{word}\n")

    total_consolidated_duration = sum(d for _, d in file_durations) + sort_duration
    return file_durations, sort_duration, total_consolidated_duration

def create_specific_consolidated_file(folder_path, project_folder):
    files_to_process = ['simple.html', 'medium.html', 'hard.html', '049.html']
    all_words = []
    file_durations = []

    start_total = time.time()

    for filename in files_to_process:
        path = os.path.join(folder_path, filename)

        start_file = time.time()
        try:
            with open(path, "r", encoding="latin-1") as f:
                text = f.read()
                cleaned_text = re.sub(r'<.*?>', '', text)
                words = extract_words(cleaned_text)
                all_words.extend([w.lower() for w in words])
        except Exception as e:
            print(f"Error en A5 al procesar {filename}: {e}")
        end_file = time.time()
        file_durations.append((filename, end_file - start_file))

    counter = Counter(all_words)

    start_sort = time.time()
    all_words_sorted = sorted(counter.items())
    end_sort = time.time()
    sort_duration = end_sort - start_sort
    
    end_total = time.time()
    total_time = end_total - start_total

    output_file = os.path.join(project_folder, "a5_03038135.txt")
    with open(output_file, "w", encoding="utf-8") as archivo:
        for word, count in all_words_sorted:
            archivo.write(f"{word} {count}\n")

        archivo.write(f"Tiempo total de procesamiento de palabras y conteo (sin incluir archivos individuales): {sort_duration:.4f} segundos\n")
        archivo.write(f"Tiempo total de ejecucion: {total_time:.4f} segundos\n")

    return file_durations, sort_duration, total_time

def create_dictionary_with_file_count(folder_path, project_folder):
    files_to_process = [f for f in os.listdir(folder_path) if f.endswith(".html")]
    token_counter = Counter()
    token_files = defaultdict(set)
    file_durations = []

    start_total = time.time()

    for filename in files_to_process:
        path = os.path.join(folder_path, filename)

        start_file = time.time()
        try:
            with open(path, "r", encoding="latin-1") as f:
                text = f.read()
                cleaned_text = re.sub(r'<.*?>', '', text)
                words = extract_words(cleaned_text)

                for w in words:
                    word = w.lower()
                    token_counter[word] += 1
                    token_files[word].add(filename)
        except Exception as e:
            print(f"Error en A6 al procesar {filename}: {e}")
            
        end_file = time.time()
        file_durations.append((filename, end_file - start_file))

    end_total = time.time()
    total_time = end_total - start_total

    output_file = os.path.join(project_folder, "a6_dictionary.txt")
    with open(output_file, "w", encoding="utf-8") as archivo:
        for token, count in sorted(token_counter.items()):
            archivo.write(f"{token};{count};{len(token_files[token])}\n")

    log_file = os.path.join(project_folder, "a6_03038135.txt")
    with open(log_file, "w", encoding="utf-8") as log:
        for filename, duration in file_durations:
            log.write(f"{filename}            {duration:.4f} \n")
        log.write(f"Tiempo total de ejecucion: {total_time:.4f} segundos\n")        

    return file_durations, total_time

def create_copy_log(folder_path, project_folder):
    files_to_process = [f for f in os.listdir(folder_path) if f.endswith(".html")]
    file_durations = []

    start_total = time.time()

    for filename in sorted(files_to_process):
        path = os.path.join(folder_path, filename)

        start_file = time.time()
        try:
            with open(path, "r", encoding="latin-1") as f:
                text = f.read()
        except Exception as e:
            print(f"Error en A7 al procesar {filename}: {e}")
            
        end_file = time.time()
        file_durations.append((filename, end_file - start_file))

    end_total = time.time()
    total_time = end_total - start_total

    log_file = os.path.join(project_folder, "a7_03038135.txt")
    with open(log_file, "w", encoding="utf-8") as log:
        for filename, duration in file_durations:
            log.write(f"{filename}            {duration:.4f}\n")
        log.write(f"Tiempo total de ejecucion: {total_time:.4f} segundos\n")

    return file_durations, total_time

def create_hash_table_dictionary(folder_path, project_folder, matricula="03038135"):
    files_to_process = [f for f in os.listdir(folder_path) if f.endswith(".html")]
    
    hash_table = [[] for _ in range(HASH_TABLE_SIZE)]
    
    token_freq = Counter()
    token_files = defaultdict(set)
    
    file_durations = []
    total_collisions = 0
    
    start_total = time.time()

    for filename in files_to_process:
        path = os.path.join(folder_path, filename)
        start_file = time.time()
        
        try:
            with open(path, "r", encoding="latin-1") as f:
                text = f.read()
                cleaned_text = re.sub(r'<.*?>', '', text)
                words = extract_words(cleaned_text)

                for w in words:
                    word = w.lower()
                    token_freq[word] += 1
                    token_files[word].add(filename)
        except Exception as e:
            print(f"Error en A8 al procesar {filename}: {e}")
            
        end_file = time.time()
        file_durations.append((filename, end_file - start_file))
    
    end_data_collection = time.time()
    data_collection_time = end_data_collection - start_total
    
    start_hash_build = time.time()
    sorted_tokens = sorted(token_freq.keys())
    
    for token in sorted_tokens:
        freq = token_freq[token]
        num_files = len(token_files[token])
        
        index = hash_function(token, HASH_TABLE_SIZE)
        
        if hash_table[index]:
            total_collisions += 1
        
        hash_table[index].append((token, freq, num_files, index))
        
    end_hash_build = time.time()
    hash_build_time = end_hash_build - start_hash_build
    
    end_total = time.time()
    total_time = end_total - start_total

    output_file = os.path.join(project_folder, f"a8_dictionary.txt")
    
    with open(output_file, "w", encoding="utf-8") as archivo:
        for i, slot in enumerate(hash_table):
            if not slot:
                archivo.write(f"Posición Hash: {i}, Token: {EMPTY_SLOT_INDICATOR}, Frecuencia: 0, Archivos: 0, Posición Posting: {EMPTY_POSTING_POSITION}\n")
            else:
                for token, freq, num_files, _ in slot:
                    archivo.write(f"Posición Hash: {i}, Token: {token}, Frecuencia: {freq}, Archivos: {num_files}, Posición Posting: {i}\n")
                    
    log_file = os.path.join(project_folder, f"a8_{matricula}.txt")
    with open(log_file, "w", encoding="utf-8") as log:
        for filename, duration in file_durations:
            log.write(f"{filename}           {duration:.4f} \n")

        log.write(f"Tiempo total de ejecución del programa: {total_time:.4f} segundos\n") 
    return file_durations, total_time, total_collisions, HASH_TABLE_SIZE


def create_filtered_hash_table_dictionary(folder_path, project_folder, matricula="03038135", min_frequency=3):
    files_to_process = [f for f in os.listdir(folder_path) if f.endswith(".html")]
    
    stoplist_path = os.path.join(project_folder, "Actividad9_stoplist.txt")
    stopwords = set()
    try:
        with open(stoplist_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            stopwords.update(re.split(r'\s+|,', content))
            stopwords.discard('')
    except FileNotFoundError:
        print(f"ADVERTENCIA: Archivo de stoplist no encontrado en {stoplist_path}. Continuando sin filtrar stopwords.")
    except Exception as e:
        print(f"ADVERTENCIA: Error al leer stoplist: {e}. Continuando sin filtrar stopwords.")

    hash_table = [[] for _ in range(HASH_TABLE_SIZE)]
    token_freq = Counter()
    token_files = defaultdict(set)
    
    file_durations = []
    total_collisions = 0
    total_tokens_read = 0
    
    start_total = time.time()

    for filename in files_to_process:
        path = os.path.join(folder_path, filename)
        start_file = time.time()
        
        try:
            with open(path, "r", encoding="latin-1") as f:
                text = f.read()
                cleaned_text = re.sub(r'<.*?>', '', text)
                words = extract_words(cleaned_text)

                for w in words:
                    word = w.lower()
                    
                    total_tokens_read += 1 
                    
                    if len(word) <= 1: 
                        continue
                    
                    if word in stopwords: 
                        continue
                        
                    token_freq[word] += 1
                    token_files[word].add(filename)
        except Exception as e:
            print(f"Error en A9 al procesar {filename}: {e}")
            
        end_file = time.time()
        file_durations.append((filename, end_file - start_file))
    
    end_data_collection = time.time()
    data_collection_time = end_data_collection - start_total
    
    start_hash_build = time.time()
    sorted_tokens = sorted(token_freq.keys())
    
    total_tokens_filtered_low_freq = 0
    
    for token in sorted_tokens:
        freq = token_freq[token]
        
        if freq < min_frequency:
            total_tokens_filtered_low_freq += 1
            continue 
        
        num_files = len(token_files[token])
        index = hash_function(token, HASH_TABLE_SIZE)
        
        if hash_table[index]:
            total_collisions += 1
        
        hash_table[index].append((token, freq, num_files, index))
        
    end_hash_build = time.time()
    hash_build_time = end_hash_build - start_hash_build
    
    end_total = time.time()
    total_time = end_total - start_total
    
    tokens_stored = len(token_freq) - total_tokens_filtered_low_freq

    output_file = os.path.join(project_folder, f"a9_dictionary.txt")
    
    with open(output_file, "w", encoding="utf-8") as archivo:
        for i, slot in enumerate(hash_table):
            if not slot:
                archivo.write(f"Posición Hash: {i}, Token: {EMPTY_SLOT_INDICATOR}, Frecuencia: 0, Archivos: 0, Posición Posting: {EMPTY_POSTING_POSITION}\n")
            else:
                for token, freq, num_files, _ in slot:
                    archivo.write(f"Posición Hash: {i}, Token: {token}, Frecuencia: {freq}, Archivos: {num_files}, Posición Posting: {i}\n")
                    
    log_file = os.path.join(project_folder, f"a9_{matricula}.txt")
    with open(log_file, "w", encoding="utf-8") as log:
        for filename, duration in file_durations:
            log.write(f"{filename}           {duration:.4f} \n")
        
        log.write(f"Tiempo total de ejecucio||n del programa: {total_time:.4f} segundos\n") 

    return file_durations, total_time, total_collisions, HASH_TABLE_SIZE

def create_inverted_index(folder_path, project_folder, matricula="03038135"):
    files_to_process = sorted([f for f in os.listdir(folder_path) if f.endswith('.html')])

    log_filename = f"a11_{matricula}.txt"
    log_path = os.path.join(project_folder, log_filename)

    with open(log_path, "w", encoding="utf-8") as log:
        log.write("=== A11 - Generación de Índice Invertido ===\n")
        log.write(f"Matrícula: {matricula}\n\n")

        document_ids = {}
        documents_output = os.path.join(project_folder, "documents.txt")

        with open(documents_output, "w", encoding="utf-8") as doc_file:
            start_total = time.time()

            for i, filename in enumerate(files_to_process, start=1):
                start = time.time()

                full_path = os.path.join(folder_path, filename)
                document_ids[filename] = i
                doc_file.write(f"{i} - {filename} - {full_path}\n")

                end = time.time()
                log.write(f"{filename} - {end - start:.4f} segundos\n")

        log.write("\n=== Procesando tokens ===\n")

        token_doc_freq = defaultdict(lambda: defaultdict(int))

        for filename in files_to_process:
            start = time.time()
            full_path = os.path.join(folder_path, filename)

            with open(full_path, "r", encoding="latin-1") as f:
                cleaned = re.sub(r'<.*?>', '', f.read())
                words = extract_words(cleaned)

                for w in words:
                    token = w.lower()
                    token_doc_freq[token][filename] += 1

            end = time.time()
            log.write(f"Tokens de {filename} procesados en {end - start:.4f} segundos\n")

        log.write("\n=== Creando Posting y Diccionario ===\n")

        posting_output = os.path.join(project_folder, "posting.txt")
        dictionary_output = os.path.join(project_folder, "dictionary.txt")

        posting_position = 0
        posting_entries = []

        with open(dictionary_output, "w", encoding="utf-8") as dict_file, \
             open(posting_output, "w", encoding="utf-8") as post_file:

            for token in sorted(token_doc_freq.keys()):
                docs = token_doc_freq[token]
                total_freq = sum(docs.values())

                start_pos = posting_position

                for filename, freq in docs.items():
                    doc_id = document_ids[filename]
                    weight = round(freq / total_freq, 4)
                    posting_entries.append(f"{doc_id} - {weight}")
                    posting_position += 1

                dict_file.write(
                    f"token: {token} | freq: {total_freq} | docs: {len(docs)} | posting_pos: {start_pos}\n"
                )

            for idx, entry in enumerate(posting_entries):
                post_file.write(f"{idx}:  {entry}\n")

        end_total = time.time()
        total_time = end_total - start_total

        log.write("\n=== RESUMEN FINAL ===\n")
        log.write(f"Archivos procesados: {len(files_to_process)}\n")
        log.write(f"Tiempo total del proceso: {total_time:.4f} segundos\n")
        log.write("============================================\n")

    return log_path

if __name__ == "__main__":
    
    starting_total_time = time.time()
    
    reading_results, cleanning_results, words_results = list_html_files(folder_path, output_folder)
    
    file_durations_a4, sort_duration_a4, consolidated_duration_a4 = create_consolidated_words_file(output_folder, project_folder)
    
    file_durations_a5, sort_duration_a5, total_time_a5 = create_specific_consolidated_file(folder_path, project_folder)

    file_durations_a6, total_time_a6 = create_dictionary_with_file_count(folder_path, project_folder)

    file_durations_a7, total_time_a7 = create_copy_log(folder_path, project_folder)

    file_durations_a8, total_time_a8, total_collisions_a8, hash_size_a8 = create_hash_table_dictionary(folder_path, project_folder)

    file_durations_a9, total_time_a9, total_collisions_a9, hash_size_a9 = create_filtered_hash_table_dictionary(folder_path, project_folder)

    create_inverted_index(folder_path, project_folder)
    
    ending_total_time = time.time()
    total_execution_time = ending_total_time - starting_total_time

    with open(os.path.join(project_folder, "a1_03038135.txt"), "w", encoding="utf-8") as archivo:
        for file, duration in reading_results:
            archivo.write(f"{file}            {duration:.4f} \n")
        archivo.write(f"tiempo total en abrir los archivos: {sum(d for _, d in reading_results):.4f} segundos\n")
        archivo.write(f"tiempo total de ejecucion {total_execution_time:.4f} segundos\n")
        
    with open(os.path.join(project_folder, "a2_03038135.txt"), "w", encoding="utf-8") as archivo:
        for file, duration in cleanning_results:
            archivo.write(f"{file}            {duration:.4f} \n")
        archivo.write(f"tiempo total en eliminar las etiquetas HTML: {sum(d for _, d in cleanning_results):.4f} segundos\n")
        archivo.write(f"tiempo total de ejecucion {total_execution_time:.4f} segundos\n")

    with open(os.path.join(project_folder, "a3_03038135.txt"), "w", encoding="utf-8") as archivo:
        for file, duration in words_results:
            archivo.write(f"{file}            {duration:.4f} \n")
        archivo.write(f"tiempo total en conteo de palabras y escritura de archivo: {sum(d for _, d in words_results):.4f} segundos\n")
        archivo.write(f"tiempo total de ejecucion {total_execution_time:.4f} segundos\n")

    with open(os.path.join(project_folder, "a4_03038135.txt"), "w", encoding="utf-8") as archivo:
        for file, duration in file_durations_a4:
            archivo.write(f"{file}            {duration:.4f} \n")
        archivo.write(f"tiempo total en crear el nuevo archivo (incluye sort): {consolidated_duration_a4:.4f} segundos\n")
        archivo.write(f"tiempo total de ejecucion: {total_execution_time:.4f} segundos\n")