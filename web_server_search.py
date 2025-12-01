from flask import Flask, request, render_template_string
import os
import re

# =================================================================
# ATENCIÓN: DEBES MODIFICAR ESTAS RUTAS PARA TU ENTORNO LOCAL
# Esto es CRÍTICO para que el programa encuentre tus archivos de índice.
# =================================================================
PROJECT_FOLDER = 'C:/Users/OGGO/Desktop/Ultimo Semestre/Fase1Act1'
HTML_FOLDER = 'C:/Users/OGGO/Desktop/Ultimo Semestre/Fase1Act1/CS13309_Archivos_HTML/Files'
# =================================================================

# --- Lógica del Motor de Búsqueda (Adaptada de tu código original) ---

class SearchEngine:
    """Motor de búsqueda para documentos indexados, listo para usarse en un servidor."""
    
    def __init__(self, project_folder, html_folder):
        self.project_folder = project_folder
        self.html_folder = html_folder
        self.documents = {}
        self.dictionary = {}
        self.posting_list = []
        self.load_index()
        self.index_loaded = len(self.documents) > 0 # Verificar si la carga fue exitosa
    
    def load_index(self):
        """Carga el índice invertido desde los archivos."""
        try:
            # Cargar documents.txt
            documents_file = os.path.join(self.project_folder, "documents.txt")
            if os.path.exists(documents_file):
                with open(documents_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(' - ')
                        if len(parts) >= 3:
                            doc_id = int(parts[0])
                            filename = parts[1]
                            self.documents[doc_id] = filename
            
            # Cargar dictionary.txt
            dictionary_file = os.path.join(self.project_folder, "dictionary.txt")
            if os.path.exists(dictionary_file):
                with open(dictionary_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'token:' in line:
                            parts = line.strip().split('|')
                            token = parts[0].split(':')[1].strip()
                            freq = int(parts[1].split(':')[1].strip())
                            docs_count = int(parts[2].split(':')[1].strip())
                            posting_pos = int(parts[3].split(':')[1].strip())
                            
                            self.dictionary[token] = {
                                'freq': freq,
                                'docs': docs_count,
                                'posting_pos': posting_pos
                            }
            
            # Cargar posting.txt
            posting_file = os.path.join(self.project_folder, "posting.txt")
            if os.path.exists(posting_file):
                with open(posting_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if ':' in line:
                            parts = line.strip().split(':')[1].strip().split(' - ')
                            if len(parts) == 2:
                                doc_id = int(parts[0])
                                weight = float(parts[1])
                                self.posting_list.append((doc_id, weight))
        except Exception as e:
            # En un servidor, es mejor imprimir el error en consola que mostrar un messagebox
            print(f"ERROR AL CARGAR EL ÍNDICE: {e}")
            
    def search_word(self, word):
        """Busca una palabra única y devuelve la lista de resultados."""
        word = word.lower().strip()
        if not word or word not in self.dictionary:
            return []
        
        info = self.dictionary[word]
        results = []
        
        for i in range(info['posting_pos'], info['posting_pos'] + info['docs']):
            if i < len(self.posting_list):
                doc_id, weight = self.posting_list[i]
                if doc_id in self.documents:
                    results.append({
                        'filename': self.documents[doc_id],
                        'relevance': weight * 100,
                        'matched_words': [word]
                    })
        
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results

    def search_multiple_words(self, words):
        """Busca múltiples palabras y combina los resultados."""
        word_list = [w.strip().lower() for w in words.split() if w.strip()]
        if not word_list: return []
        
        all_results = {}
        for word in word_list:
            # Usar search_word para obtener los postings de cada término
            single_word_results = self.search_word(word)
            
            for doc in single_word_results:
                filename = doc['filename'] # Usar filename como key único para la agregación
                
                if filename not in all_results:
                    all_results[filename] = {
                        'filename': filename,
                        'relevance': 0,
                        'matched_words': []
                    }
                
                # Sumar la relevancia
                all_results[filename]['relevance'] += doc['relevance']
                
                # Registrar la palabra encontrada
                if word not in all_results[filename]['matched_words']:
                    all_results[filename]['matched_words'].append(word)
        
        combined_results = list(all_results.values())
        combined_results.sort(key=lambda x: x['relevance'], reverse=True)
        return combined_results
        
    def get_document_preview(self, filename, max_chars=300):
        """Obtiene una vista previa limpia del documento para la web."""
        filepath = os.path.join(self.html_folder, filename)
        if not os.path.exists(filepath):
            return "Documento no encontrado o ruta incorrecta."
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
                # Limpiar HTML
                cleaned = re.sub(r'<.*?>', '', content)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                return cleaned[:max_chars] + "..." if len(cleaned) > max_chars else cleaned
        except Exception as e:
            return f"Error al leer: {e}"

    def get_document_content(self, filename):
        """Obtiene el contenido COMPLETO y limpio del documento para su visualización."""
        filepath = os.path.join(self.html_folder, filename)
        if not os.path.exists(filepath):
            return "Error: Documento no encontrado o ruta incorrecta.", False
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
                # Limpiar HTML (mostrando solo el texto limpio)
                cleaned = re.sub(r'<.*?>', '', content)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                return cleaned, True
        except Exception as e:
            return f"Error al leer: {e}", False

# --- Inicialización de Flask y el Motor de Búsqueda ---
app = Flask(__name__)
# Inicializamos el motor de búsqueda globalmente
search_engine = SearchEngine(PROJECT_FOLDER, HTML_FOLDER)

# --- Plantilla HTML de Vista de Documento Completo ---
DOC_VIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualizando: {{ filename }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f7f9fb; }
    </style>
</head>
<body class="p-4 sm:p-8">
    <div class="max-w-4xl mx-auto bg-white p-6 sm:p-10 rounded-xl shadow-2xl">
        <a href="/" class="text-blue-600 hover:text-blue-800 transition duration-150 mb-6 inline-block font-semibold">
            &larr; Volver a la Búsqueda
        </a>
        <h1 class="text-2xl font-bold text-gray-800 border-b pb-2 mb-4">
            Contenido de: <span class="text-blue-700">{{ filename }}</span>
        </h1>
        
        <pre class="whitespace-pre-wrap p-4 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-700 leading-relaxed overflow-auto max-h-[70vh]">
            {{ content }}
        </pre>
    </div>
</body>
</html>
"""

# --- Plantilla HTML (Usando Tailwind para una interfaz moderna) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buscador Web de Documentos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f7f9fb; }
    </style>
</head>
<body class="p-4 sm:p-8">
    <div class="max-w-4xl mx-auto bg-white p-6 sm:p-10 rounded-xl shadow-2xl">
        <h1 class="text-3xl font-extrabold text-blue-700 mb-2">🔍 Buscador Web de Documentos HTML</h1>
        <p class="text-gray-500 mb-6">Motor de Recuperación de Información con {{ total_docs }} documentos indexados.</p>

        {% if not index_loaded %}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong class="font-bold">¡Advertencia!</strong>
          <span class="block sm:inline">El índice no pudo ser cargado. Por favor, verifica las rutas de PROJECT_FOLDER y HTML_FOLDER en el archivo Python.</span>
        </div>
        {% endif %}

        <form action="/" method="get" class="flex flex-col sm:flex-row gap-4 mb-8">
            <input type="text" name="query" placeholder="Ingresa palabra(s) clave..." 
                   value="{{ query if query else '' }}"
                   class="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-lg shadow-sm">
            <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-150 shadow-md">
                Buscar
            </button>
        </form>

        {% if query %}
            <h2 class="text-xl font-semibold text-gray-800 mb-4">
                Resultados para: "<span class="text-blue-600">{{ query }}</span>"
            </h2>
            <p class="text-gray-500 mb-6">
                Encontrados {{ results | length }} documento(s)
            </p>

            <div class="space-y-4">
                {% for doc in results %}
                <div class="bg-white border border-gray-200 rounded-xl p-5 shadow-lg hover:shadow-xl transition duration-150">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-lg font-bold">
                            {{ loop.index }}. 
                            <a href="/view_doc/{{ doc.filename }}" class="text-gray-800 hover:text-blue-600 transition duration-150">
                                {{ doc.filename }}
                            </a>
                        </h3>
                        <span class="text-sm font-semibold bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
                            {{ "%.1f" | format(doc.relevance) }}% Relevante
                        </span>
                    </div>
                    <p class="text-sm text-green-600 mb-2">
                        Palabras encontradas: {{ doc.matched_words | join(', ') }}
                    </p>
                    <p class="text-gray-600 mb-4 text-sm leading-relaxed">
                        {{ search_engine.get_document_preview(doc.filename) }}
                    </p>
                </div>
                {% endfor %}
            </div>
            
            {% if not results %}
            <p class="text-center text-gray-500 py-10">❌ No se encontraron resultados para su búsqueda.</p>
            {% endif %}

        {% else %}
            <div class="text-center py-20 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                <p class="text-gray-500">Inicia una búsqueda ingresando una o varias palabras clave.</p>
            </div>
        {% endif %}
        
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    """Ruta principal que maneja la búsqueda y renderiza la interfaz."""
    query = request.args.get('query', '').strip()
    results = []
    
    if query:
        # Si la consulta contiene espacios, usamos la búsqueda de múltiples palabras
        if ' ' in query.strip():
            results = search_engine.search_multiple_words(query)
        else:
            # Si es una sola palabra, usamos la búsqueda de una sola palabra
            results = search_engine.search_word(query)
            
    return render_template_string(HTML_TEMPLATE, 
                                  query=query, 
                                  results=results,
                                  search_engine=search_engine, # Permite llamar a get_document_preview desde el template
                                  total_docs=len(search_engine.documents),
                                  index_loaded=search_engine.index_loaded)

@app.route('/view_doc/<filename>', methods=['GET'])
def view_document(filename):
    """Ruta para ver el contenido completo de un documento."""
    content, success = search_engine.get_document_content(filename)
    
    return render_template_string(DOC_VIEW_TEMPLATE,
                                  filename=filename,
                                  content=content)


if __name__ == '__main__':
    if not search_engine.index_loaded:
        print("\n=======================================================")
        print("ADVERTENCIA: El índice no se cargó correctamente.")
        print(f"Revisa las variables PROJECT_FOLDER ('{PROJECT_FOLDER}') y HTML_FOLDER.")
        print("=======================================================\n")
    
    # Esto inicia el servidor local en http://127.0.0.1:5000/
    print("Iniciando el servidor Flask...")
    app.run(debug=True)